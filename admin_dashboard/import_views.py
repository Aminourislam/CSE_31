import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse

from accounts.models import User
from profiles.models import Profile
from universities.models import University, Department, Session, Batch
from locations.models import Division, District, Upazila

from .permissions import admin_required


# ============================================
# CSV COLUMN ORDER (must match sample CSV)
# ============================================
CSV_COLUMNS = [
    'full_name',
    'email',
    'phone',
    'student_id',
    'university',
    'department',
    'session',
    'batch',
    'division',
    'district',
    'upazila',
    'occupation',
    'organization',
    'designation',
    'gender',
    'date_of_birth',   # YYYY-MM-DD
    'blood_group',
]


# ============================================
# MAIN VIEW
# ============================================
@admin_required
def import_members(request):
    # ----- Handle downloaded sample -----
    if request.GET.get('sample'):
        return _download_sample()

    # ----- Handle actual import after preview -----
    if request.method == 'POST' and request.POST.get('confirm') == '1':
        return _do_import(request)

    # ----- Handle preview (CSV upload) -----
    if request.method == 'POST' and request.FILES.get('csv_file'):
        return _preview(request)

    # ----- Show upload form -----
    return render(request, 'admin_dashboard/import.html')


# ============================================
# PREVIEW STEP
# ============================================
def _preview(request):
    csv_file = request.FILES['csv_file']

    if not csv_file.name.lower().endswith('.csv'):
        messages.error(request, 'Only .csv files are accepted.')
        return redirect('admin_dashboard:import_members')

    try:
        decoded = csv_file.read().decode('utf-8-sig')   # strip BOM if present
    except UnicodeDecodeError:
        try:
            csv_file.seek(0)
            decoded = csv_file.read().decode('latin-1')
        except Exception:
            messages.error(request, 'Could not read the CSV file. Save it as UTF-8.')
            return redirect('admin_dashboard:import_members')

    reader = csv.DictReader(io.StringIO(decoded))

    # Validate header
    if not reader.fieldnames:
        messages.error(request, 'The CSV has no header row.')
        return redirect('admin_dashboard:import_members')

    missing_cols = [c for c in ['full_name', 'email', 'student_id'] if c not in reader.fieldnames]
    if missing_cols:
        messages.error(
            request,
            f'Missing required columns: {", ".join(missing_cols)}. '
            f'Expected columns: {", ".join(CSV_COLUMNS)}'
        )
        return redirect('admin_dashboard:import_members')

    valid_rows = []
    error_rows = []

    # Track duplicates within the file itself
    seen_emails = set()
    seen_student_ids = set()

    for idx, raw in enumerate(reader, start=2):   # row 1 is header
        row = {k.strip(): (v.strip() if v else '') for k, v in raw.items()}
        errors = []

        email = row.get('email', '').lower()
        student_id = row.get('student_id', '')

        # Required
        if not row.get('full_name'):
            errors.append('full_name is required')
        if not email:
            errors.append('email is required')
        elif '@' not in email:
            errors.append('email is invalid')
        if not student_id:
            errors.append('student_id is required')

        # Duplicates in file
        if email and email in seen_emails:
            errors.append('duplicate email in file')
        if student_id and student_id in seen_student_ids:
            errors.append('duplicate student_id in file')

        # Duplicates in DB
        if email and User.objects.filter(email=email).exists():
            errors.append('email already exists in database')
        if student_id and Profile.objects.filter(student_id=student_id).exists():
            errors.append('student_id already exists in database')

        if email:
            seen_emails.add(email)
        if student_id:
            seen_student_ids.add(student_id)

        if errors:
            row['errors_list'] = errors
            row['row_number'] = idx
            error_rows.append(row)
        else:
            row['row_number'] = idx
            valid_rows.append(row)

    # Store valid rows in session for the confirm step
    # (small datasets only — for very large CSVs, save to a temp file instead)
    request.session['import_valid_rows'] = valid_rows
    request.session.modified = True

    context = {
        'valid_rows': valid_rows,
        'error_rows': error_rows,
        'valid_count': len(valid_rows),
        'error_count': len(error_rows),
        'total_count': len(valid_rows) + len(error_rows),
        'csv_columns': CSV_COLUMNS,
    }
    return render(request, 'admin_dashboard/import_preview.html', context)


# ============================================
# IMPORT STEP
# ============================================
def _do_import(request):
    valid_rows = request.session.get('import_valid_rows', [])

    if not valid_rows:
        messages.error(request, 'Nothing to import. Please upload a CSV again.')
        return redirect('admin_dashboard:import_members')

    created = 0
    skipped = 0

    for row in valid_rows:
        try:
            # --- Auto-create / look up related records ---
            university = _get_or_create_university(row.get('university', ''))
            department = _get_or_create_department(university, row.get('department', ''))
            session_obj = _get_or_create_session(row.get('session', ''))
            batch = _get_or_create_batch(row.get('batch', ''), department, session_obj)

            division = _lookup_location(Division, row.get('division', ''))
            district = _lookup_location(District, row.get('district', ''), division)
            upazila = _lookup_location(Upazila, row.get('upazila', ''), district)

            # --- Create user with default password ---
            DEFAULT_IMPORT_PASSWORD = '1234'
            user = User.objects.create_user(
                email=row['email'].lower(),
                password=DEFAULT_IMPORT_PASSWORD,
                status=User.Status.APPROVED,
                role=User.Role.MEMBER,
            )

            # --- Update profile (auto-created by signal) ---
            profile = user.profile
            profile.full_name = row.get('full_name', '')
            profile.phone = row.get('phone', '')
            profile.student_id = row.get('student_id', '')
            profile.university = university
            profile.department = department
            profile.session = session_obj
            profile.batch = batch
            profile.division = division
            profile.district = district
            profile.upazila = upazila
            profile.occupation = row.get('occupation', '')
            profile.organization = row.get('organization', '')
            profile.designation = row.get('designation', '')

            gender = (row.get('gender') or '').upper()
            if gender in ('MALE', 'FEMALE', 'OTHER'):
                profile.gender = gender

            dob = row.get('date_of_birth', '')
            if dob:
                from datetime import datetime
                try:
                    profile.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    pass

            profile.blood_group = row.get('blood_group', '')
            profile.save()

            created += 1
        except Exception as e:
            skipped += 1
            print(f"Import error for {row.get('email')}: {e}")

    # Clear session data
    if 'import_valid_rows' in request.session:
        del request.session['import_valid_rows']

    messages.success(request, f'Imported {created} member(s). {skipped} skipped due to errors.')
    return redirect('admin_dashboard:users_list')


# ============================================
# HELPERS
# ============================================
def _get_or_create_university(name):
    if not name:
        return None
    name = name.strip()
    obj, _ = University.objects.get_or_create(
        name=name,
        defaults={'short_name': name[:20]},
    )
    return obj


def _get_or_create_department(university, name):
    if not name or not university:
        return None
    name = name.strip()
    obj, _ = Department.objects.get_or_create(
        university=university,
        name=name,
    )
    return obj


def _get_or_create_session(name):
    if not name:
        return None
    name = name.strip()
    obj, _ = Session.objects.get_or_create(name=name)
    return obj


def _get_or_create_batch(name, department, session_obj):
    if not name or not department or not session_obj:
        return None
    name = name.strip()
    obj, _ = Batch.objects.get_or_create(
        name=name,
        department=department,
        session=session_obj,
    )
    return obj


def _lookup_location(model, name, parent):
    if not name:
        return None
    name = name.strip()
    filters = {'name__iexact': name}
    if parent:
        if model is District:
            filters['division'] = parent
        elif model is Upazila:
            filters['district'] = parent
    return model.objects.filter(**filters).first()


# ============================================
# SAMPLE CSV DOWNLOAD
# ============================================
def _download_sample():
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="members_sample.csv"'
    response.write('\ufeff')  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow(CSV_COLUMNS)
    writer.writerow([
        'Rahim Ahmed',
        'rahim@example.com',
        '01700000001',
        'CSE001',
        'Chittagong University of Engineering & Technology',
        'Computer Science & Engineering',
        '2020-21',
        'CSE 10th Batch',
        'Chattogram',
        'Chattogram',
        'Hathazari',
        'Software Engineer',
        'Acme Ltd',
        'Senior Engineer',
        'MALE',
        '1998-05-15',
        'B+',
    ])
    writer.writerow([
        'Fatima Khan',
        'fatima@example.com',
        '01700000002',
        'CSE002',
        'Chittagong University of Engineering & Technology',
        'Computer Science & Engineering',
        '2020-21',
        'CSE 10th Batch',
        'Dhaka',
        'Dhaka',
        'Savar',
        'Student',
        'CUET',
        '',
        'FEMALE',
        '1999-11-20',
        'O+',
    ])
    return response