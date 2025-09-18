from django.db import models
from django.contrib.auth.models import User


class NewsPost(models.Model):
	CATEGORY_CHOICES = [
		('academics', 'Academics'),
		('events', 'Events'),
		('sports', 'Sports'),
		('research', 'Research'),
	]
	title = models.CharField(max_length=200)
	category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
	content = models.TextField()
	image_url = models.URLField(blank=True)
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_posts')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title


class NewsLike(models.Model):
	post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='likes')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_likes')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('post', 'user')


class NewsComment(models.Model):
	post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='comments')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_comments')
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']


class NewsShare(models.Model):
	post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='shares')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_shares')
	created_at = models.DateTimeField(auto_now_add=True)


class Announcement(models.Model):
	title = models.CharField(max_length=200)
	content = models.TextField()
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title


class Poll(models.Model):
	question = models.CharField(max_length=255)
	options = models.TextField(help_text='One option per line')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.question

	def options_list(self):
		raw = self.options or ''
		try:
			import re
			parts = re.split(r'[\r\n,;]+', raw)
		except Exception:
			parts = raw.splitlines()
		return [o.strip() for o in parts if o.strip()]

	@property
	def options_parsed(self):
		return self.options_list()


class PollVote(models.Model):
	poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
	option_index = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('poll', 'user')

	def __str__(self):
		return f"{self.user.username} -> {self.poll_id}:{self.option_index}"
