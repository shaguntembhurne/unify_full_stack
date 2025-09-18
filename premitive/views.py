from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import UserProfile
from django.views.decorators.http import require_POST
from django.contrib import messages
from news.models import NewsPost, Announcement
from projects.models import Project
from .models import Notification
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse


def landing(request):
    return render(request, 'landing.html')


def signup(request):
    return redirect('premitive:auth')


def auth_page(request):
    errors = []
    tab = 'login'
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'login':
            tab = 'login'
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            username = email  # treat email as username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('news:list')
            else:
                errors.append('Invalid email or password.')
        elif form_type == 'signup':
            tab = 'signup'
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip().lower()
            password = request.POST.get('password', '')
            role = request.POST.get('role', 'student')
            if not name or not email or not password:
                errors.append('All fields are required.')
            elif User.objects.filter(username=email).exists():
                errors.append('An account with that email already exists.')
            else:
                user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                UserProfile.objects.create(user=user, role='teacher' if role == 'teacher' else 'student')
                login(request, user)
                return redirect('news:list')
        else:
            errors.append('Unknown form submission.')
    return render(request, 'authentication_page.html', {'errors': errors, 'active_tab': tab})


def news(request):
    if not request.user.is_authenticated:
        return redirect('premitive:auth')
    tpl = get_template('news.html')
    html = tpl.render({}, request)
    print('DEBUG news template origin:', getattr(tpl, 'origin', None))
    print('DEBUG news rendered length:', len(html))
    return HttpResponse(html)


def profile(request):
    if not request.user.is_authenticated:
        return redirect('premitive:auth')
    # Ensure the user has an attached profile to avoid template errors
    if request.user.is_authenticated:
        UserProfile.objects.get_or_create(user=request.user)
    profile = request.user.profile
    my_news = NewsPost.objects.filter(author=request.user)[:5]
    my_announcements = Announcement.objects.filter(author=request.user)[:5]
    my_projects = Project.objects.filter(author=request.user)[:5]
    skills_list = []
    if profile.skills:
        skills_list = [s.strip() for s in profile.skills.split(',') if s.strip()]
    context = {
        'profile': profile,
        'my_news': my_news,
    'my_announcements': my_announcements,
    'my_projects': my_projects,
        'skills_list': skills_list,
    }
    return render(request, 'profile.html', context)


@require_POST
def profile_update(request):
    if not request.user.is_authenticated:
        return redirect('premitive:auth')
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    # Basic fields from the modal form
    request.user.first_name = request.POST.get('name', request.user.first_name)
    profile.domain = request.POST.get('domain', profile.domain)
    profile.image_url = request.POST.get('image_url', profile.image_url)
    profile.bio = request.POST.get('bio', profile.bio)
    profile.skills = request.POST.get('skills', profile.skills)
    profile.github_url = request.POST.get('github_url', profile.github_url)
    profile.linkedin_url = request.POST.get('linkedin_url', profile.linkedin_url)
    profile.portfolio_url = request.POST.get('portfolio_url', profile.portfolio_url)
    request.user.save()
    profile.save()
    messages.success(request, 'Profile updated successfully!')
    return redirect('premitive:profile')
from django.shortcuts import render

# Create your views here.


@login_required
def notifications_dropdown(request):
    items = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    data = [
        {
            'id': n.id,
            'message': n.message,
            'type': n.type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
        } for n in items
    ]
    unseen_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'items': data, 'unseen': unseen_count})


@login_required
@require_POST
def notifications_mark_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})
