from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Count
from .models import NewsPost, Announcement, Poll, PollVote, NewsLike, NewsComment, NewsShare
from premitive.models import UserProfile, Notification


@login_required
def news_list(request):
	posts = (
		NewsPost.objects.select_related('author')
		.annotate(likes_count=Count('likes', distinct=True))
		.annotate(comments_count=Count('comments', distinct=True))
		.annotate(shares_count=Count('shares', distinct=True))
		.all()
	)
	announcements = []
	polls = Poll.objects.select_related('author').prefetch_related('votes').all()
	# Ensure profile exists and determine role
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	role = profile.role
	if role == 'teacher':
		announcements = Announcement.objects.filter(author=request.user).select_related('author')
	# Build poll stats and attach to poll instances for UI (no leading underscores for template safety)
	for p in polls:
		opts = p.options_list()
		total = p.votes.count()
		counts = [0] * len(opts)
		for v in p.votes.all():
			if 0 <= v.option_index < len(counts):
				counts[v.option_index] += 1
		if total > 0:
			percentages = [round(c * 100 / total, 1) for c in counts]
		else:
			percentages = [0.0] * max(1, len(counts))
		user_choice = None
		if request.user.is_authenticated:
			uv = next((v for v in p.votes.all() if v.user_id == request.user.id), None)
			user_choice = uv.option_index if uv else None
		p.total_votes = total
		p.user_choice = user_choice
		p.choice_rows = [
			{
				'idx': i,
				'text': opts[i],
				'count': counts[i],
				'pct': percentages[i],
			}
			for i in range(len(opts))
		]
	# Ensure attached attributes persist into the template
	polls = list(polls)
	context = {
		'posts': posts,
		'announcements': announcements,
		'polls': polls,
		'is_teacher': role == 'teacher'
	}
	return render(request, 'news/news.html', context)


@login_required
@require_POST
def news_create(request):
	title = request.POST.get('title', '').strip()
	category = request.POST.get('category', 'academics')
	content = request.POST.get('content', '').strip()
	image_url = request.POST.get('image_url', '').strip()
	if title and content and category in dict(NewsPost.CATEGORY_CHOICES):
		NewsPost.objects.create(
			title=title,
			category=category,
			content=content,
			image_url=image_url,
			author=request.user
		)
	return redirect('news:list')


@login_required
@require_POST
def announcement_create(request):
	title = request.POST.get('a_title', '').strip()
	content = request.POST.get('a_content', '').strip()
	# Only teachers allowed
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	if profile.role != 'teacher':
		return redirect('news:list')
	if title and content:
		ann = Announcement.objects.create(title=title, content=content, author=request.user)
		# Notify all students about teacher's announcement
		# Minimal approach: notify all users except the author
		from django.contrib.auth.models import User
		recipients = User.objects.exclude(id=request.user.id)
		bulk = [
			Notification(
				user=u,
				actor=request.user,
				type='announcement',
				message=f"New announcement: {title}",
				announcement=ann,
			) for u in recipients
		]
		Notification.objects.bulk_create(bulk, ignore_conflicts=True)
	return redirect('news:list')


@login_required
@require_POST
def poll_create(request):
	question = request.POST.get('p_question', '').strip()
	options = request.POST.get('p_options', '').strip()
	if question and options:
		Poll.objects.create(question=question, options=options, author=request.user)
	return redirect('news:list')


@login_required
@require_POST
def poll_vote(request, poll_id):
	try:
		poll = Poll.objects.get(id=poll_id)
	except Poll.DoesNotExist:
		return redirect('news:list')
	try:
		option_index = int(request.POST.get('option_index', '-1'))
	except ValueError:
		option_index = -1
	options = poll.options_list()
	if 0 <= option_index < len(options):
		# Create or update user's vote for this poll
		PollVote.objects.update_or_create(
			poll=poll,
			user=request.user,
			defaults={'option_index': option_index}
		)
	return redirect('news:list')


@login_required
@require_POST
def post_like(request, post_id):
	try:
		post = NewsPost.objects.get(id=post_id)
	except NewsPost.DoesNotExist:
		return JsonResponse({'error': 'Not found'}, status=404)
	like, created = NewsLike.objects.get_or_create(post=post, user=request.user)
	if not created:
		like.delete()
		liked = False
	else:
		liked = True
		if post.author_id != request.user.id:
			Notification.objects.create(
				user=post.author,
				actor=request.user,
				type='like',
				message=f"{request.user.first_name or request.user.username} liked your post",
				post=post,
			)
	counts = post.likes.count()
	return JsonResponse({'liked': liked, 'likes': counts})


@login_required
def post_comment_list(request, post_id):
	try:
		post = NewsPost.objects.get(id=post_id)
	except NewsPost.DoesNotExist:
		return JsonResponse({'error': 'Not found'}, status=404)
	data = [
		{
			'user': c.user.first_name or c.user.username,
			'text': c.text,
			'created_at': c.created_at.isoformat(),
		}
		for c in post.comments.select_related('user')[:50]
	]
	return JsonResponse({'comments': data})


@login_required
@require_POST
def post_comment_create(request, post_id):
	try:
		post = NewsPost.objects.get(id=post_id)
	except NewsPost.DoesNotExist:
		return JsonResponse({'error': 'Not found'}, status=404)
	text = (request.POST.get('text') or '').strip()
	if not text:
		return HttpResponseBadRequest('Empty')
	c = NewsComment.objects.create(post=post, user=request.user, text=text)
	if post.author_id != request.user.id:
		Notification.objects.create(
			user=post.author,
			actor=request.user,
			type='comment',
			message=f"{request.user.first_name or request.user.username} commented on your post",
			post=post,
		)
	return JsonResponse({
		'ok': True,
		'comment': {
			'user': c.user.first_name or c.user.username,
			'text': c.text,
			'created_at': c.created_at.isoformat(),
		},
		'count': post.comments.count(),
	})


@login_required
@require_POST
def post_share(request, post_id):
	try:
		post = NewsPost.objects.get(id=post_id)
	except NewsPost.DoesNotExist:
		return JsonResponse({'error': 'Not found'}, status=404)
	NewsShare.objects.create(post=post, user=request.user)
	return JsonResponse({'ok': True, 'shares': post.shares.count()})
