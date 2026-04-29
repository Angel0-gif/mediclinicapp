from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def register_view(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'admin':
        messages.error(request, 'Only administrators can create accounts.')
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            u = User.objects.create_user(
                username=username,
                email=request.POST.get('email',''),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name',''),
                last_name=request.POST.get('last_name',''),
            )
            UserProfile.objects.filter(user=u).update(
                role=request.POST.get('role','receptionist'),
                phone=request.POST.get('phone','')
            )
            messages.success(request, f'Account created for {u.get_full_name()}.')
            return redirect('staff_list')
    return render(request, 'auth/register.html')


@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name  = request.POST.get('last_name',  request.user.last_name)
        request.user.email      = request.POST.get('email',      request.user.email)
        request.user.save()
        if profile:
            profile.phone = request.POST.get('phone', profile.phone)
            profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'auth/profile.html', {'profile': profile})
