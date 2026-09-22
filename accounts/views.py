from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistrationForm, LoginForm


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:pending')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Wait for admin approval.')
        return response


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.status == 'PENDING':
            messages.error(self.request, 'Your account is pending approval.')
            return redirect('accounts:login')
        if user.status == 'REJECTED':
            messages.error(self.request, 'Your account was rejected.')
            return redirect('accounts:login')
        if user.status == 'SUSPENDED':
            messages.error(self.request, 'Your account is suspended.')
            return redirect('accounts:login')
        return super().form_valid(form)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


def pending_view(request):
    return render(request, 'accounts/pending.html')