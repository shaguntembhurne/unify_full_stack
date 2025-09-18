from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, ProjectMember
from premitive.models import Notification


def projects_home(request):
	projects = Project.objects.all()
	return render(request, 'projects/projects.html', {'projects': projects})


@login_required
@require_POST
def project_create(request):
	title = request.POST.get('title', '').strip()
	skills = request.POST.get('skills', '').strip()
	description = request.POST.get('description', '').strip()
	status = request.POST.get('status', 'recruiting')
	if not title or not description:
		messages.error(request, 'Title and Description are required.')
		return redirect('projects:home')
	Project.objects.create(
		title=title,
		skills=skills,
		description=description,
		status=status if status in dict(Project.STATUS_CHOICES) else 'recruiting',
		author=request.user,
	)
	messages.success(request, 'Project created!')
	return redirect('projects:home')

# Create your views here.


@login_required
@require_POST
def project_join(request, project_id):
	try:
		project = Project.objects.get(id=project_id)
	except Project.DoesNotExist:
		messages.error(request, 'Project not found.')
		return redirect('projects:home')
	if project.author_id == request.user.id:
		messages.info(request, 'You are the author of this project.')
		return redirect('projects:home')
	membership, created = ProjectMember.objects.get_or_create(project=project, user=request.user)
	if created:
		if project.author_id != request.user.id:
			Notification.objects.create(
				user=project.author,
				actor=request.user,
				type='project_join',
				message=f"{request.user.first_name or request.user.username} joined your project",
				project=project,
			)
		messages.success(request, 'Joined project!')
	else:
		messages.info(request, 'You already joined this project.')
	return redirect('projects:home')
