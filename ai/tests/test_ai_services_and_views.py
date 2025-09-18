from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from premitive.models import UserProfile
from news.models import NewsPost
from projects.models import Project


class AiServicesAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='u@example.com', email='u@example.com', password='pass')
        UserProfile.objects.create(user=self.user, role='student')
        self.client.login(username='u@example.com', password='pass')
        # Seed minimal content
        self.post = NewsPost.objects.create(title='Library Update', category='academics', content='New Python resources available', author=self.user)
        self.project = Project.objects.create(title='Data Tools', description='Build Python data tools', skills='Python, Pandas', author=self.user)

    @patch('ai.ai_services.get_collection')
    @patch('ai.ai_services.ollama_embed')
    def test_index_signals_do_not_crash(self, m_embed, m_coll):
        m_embed.return_value = [0.1, 0.2, 0.3]
        m_coll.return_value = type('C', (), {'upsert': lambda *args, **kwargs: None})()
        # Trigger save to invoke signals
        self.post.title = 'Library Update 2'
        self.post.save()
        self.project.description = 'Build Python data tools and CLI'
        self.project.save()

    @patch('ai.views.ollama_generate')
    @patch('ai.views.query_similar')
    def test_chat_view_rag_flow(self, m_query, m_gen):
        m_query.return_value = [
            {
                'id': f'project:{self.project.id}',
                'text': 'Project: Data Tools\nSkills: Python, Pandas\nBuild Python data tools',
                'metadata': {'type': 'project', 'title': 'Data Tools'},
                'distance': 0.01,
            }
        ]
        m_gen.return_value = 'Projects that use Python: Data Tools.'
        url = reverse('ai:chat')
        r = self.client.post(url, {'q': 'What projects use Python?'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('answer', data)
        self.assertTrue(data['answer'].startswith('Projects that use Python'))

    @patch('ai.views.ollama_generate')
    def test_news_summary_today(self, m_gen):
        m_gen.return_value = 'Summary bullets here.'
        url = reverse('ai:news_summary_today')
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get('summary'), 'Summary bullets here.')

    @patch('ai.views.ollama_generate')
    def test_news_qa_today(self, m_gen):
        m_gen.return_value = '3 — There are three interesting items today.'
        url = reverse('ai:news_qa_today')
        r = self.client.post(url, {'q': 'How many interesting news are there today?'})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn('answer', data)
        self.assertTrue(data['answer'].startswith('3'))