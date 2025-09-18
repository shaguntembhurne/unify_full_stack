from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
	STATUS_CHOICES = [
		('recruiting', 'Recruiting'),
		('in_progress', 'In Progress'),
		('completed', 'Completed'),
	]

	title = models.CharField(max_length=200)
	description = models.TextField()
	skills = models.TextField(blank=True)  # comma-separated
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='recruiting')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title

	def skills_list(self):
		return [s.strip() for s in (self.skills or '').split(',') if s.strip()]

class ProjectMember(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('project', 'user')

	def __str__(self):
		return f"{self.user.username} -> {self.project.title}"

# Create your models here.
