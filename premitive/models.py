from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
	ROLE_CHOICES = [
		('student', 'Student'),
		('teacher', 'Teacher'),
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
	# Extended profile fields
	image_url = models.URLField(blank=True)
	domain = models.CharField(max_length=120, blank=True)
	bio = models.TextField(blank=True)
	skills = models.TextField(blank=True)  # comma-separated
	github_url = models.URLField(blank=True)
	linkedin_url = models.URLField(blank=True)
	portfolio_url = models.URLField(blank=True)

	def __str__(self):
		return f"{self.user.username} ({self.role})"


class Notification(models.Model):
	TYPE_CHOICES = [
		('like', 'Like'),
		('comment', 'Comment'),
		('announcement', 'Announcement'),
		('project_join', 'Project Join'),
	]
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
	actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='actor_notifications')
	type = models.CharField(max_length=20, choices=TYPE_CHOICES)
	message = models.CharField(max_length=255)
	post = models.ForeignKey('news.NewsPost', null=True, blank=True, on_delete=models.SET_NULL, related_name='post_notifications')
	announcement = models.ForeignKey('news.Announcement', null=True, blank=True, on_delete=models.SET_NULL, related_name='announcement_notifications')
	project = models.ForeignKey('projects.Project', null=True, blank=True, on_delete=models.SET_NULL, related_name='project_notifications')
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"To {self.user.username}: {self.message}"

