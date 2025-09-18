from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from premitive.models import UserProfile, Notification
from news.models import NewsPost, Announcement
from projects.models import Project, ProjectMember


class NotificationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Users
        self.author = User.objects.create_user(username='author@example.com', email='author@example.com', password='pass', first_name='Author')
        self.student = User.objects.create_user(username='student@example.com', email='student@example.com', password='pass', first_name='Student')
        self.teacher = User.objects.create_user(username='teacher@example.com', email='teacher@example.com', password='pass', first_name='Teacher')
        UserProfile.objects.create(user=self.author, role='student')
        UserProfile.objects.create(user=self.student, role='student')
        UserProfile.objects.create(user=self.teacher, role='teacher')
        # Content
        self.post = NewsPost.objects.create(title='P1', category='events', content='Body', author=self.author)
        self.project = Project.objects.create(title='Proj', description='Desc', author=self.author)

    def login(self, user):
        ok = self.client.login(username=user.username, password='pass')
        self.assertTrue(ok)

    def test_like_creates_notification(self):
        self.login(self.student)
        url = reverse('news:post_like', args=[self.post.id])
        r = self.client.post(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Notification.objects.filter(user=self.author, type='like', post=self.post, actor=self.student).count(), 1)
        # Toggle unlike should not create new notification
        r2 = self.client.post(url)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(Notification.objects.filter(user=self.author, type='like', post=self.post, actor=self.student).count(), 1)

    def test_comment_creates_notification(self):
        self.login(self.student)
        url = reverse('news:post_comment_create', args=[self.post.id])
        r = self.client.post(url, {'text': 'Nice!'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Notification.objects.filter(user=self.author, type='comment', post=self.post, actor=self.student).count(), 1)

    def test_announcement_notifies_all_except_author(self):
        # Make some additional users
        u2 = User.objects.create_user(username='u2@example.com', email='u2@example.com', password='pass', first_name='U2')
        UserProfile.objects.create(user=u2, role='student')
        self.login(self.teacher)
        url = reverse('news:announcement_create')
        r = self.client.post(url, {'a_title': 'Exam', 'a_content': 'Midterm on Friday'})
        self.assertEqual(r.status_code, 302)
        # Everyone except teacher should get a notification
        recipients = [self.author, self.student, u2]
        for u in recipients:
            self.assertTrue(Notification.objects.filter(user=u, type='announcement').exists(), f"No announcement notification for {u.username}")
        self.assertFalse(Notification.objects.filter(user=self.teacher, type='announcement').exists())

    def test_project_join_creates_notification_for_author(self):
        self.login(self.student)
        url = reverse('projects:join', args=[self.project.id])
        r = self.client.post(url)
        self.assertEqual(r.status_code, 302)
        # Membership created
        self.assertTrue(ProjectMember.objects.filter(project=self.project, user=self.student).exists())
        # Author notified
        self.assertTrue(Notification.objects.filter(user=self.author, type='project_join', project=self.project, actor=self.student).exists())

    def test_notifications_endpoints_dropdown_and_mark_read(self):
        # Seed a notification for author
        Notification.objects.create(user=self.author, actor=self.student, type='comment', message='Test', post=self.post)
        self.login(self.author)
        # Dropdown
        dd_url = reverse('premitive:notifications_dropdown')
        r = self.client.get(dd_url)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertGreaterEqual(data.get('unseen', 0), 1)
        self.assertGreaterEqual(len(data.get('items', [])), 1)
        # Mark read
        mark_url = reverse('premitive:notifications_mark_read')
        r2 = self.client.post(mark_url)
        self.assertEqual(r2.status_code, 200)
        # Dropdown now shows unseen 0
        r3 = self.client.get(dd_url)
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.json().get('unseen', 0), 0)
