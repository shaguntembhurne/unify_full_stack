from django.core.management.base import BaseCommand
from django.db import transaction
from ai.ai_services import add_documents
from news.models import NewsPost
from projects.models import Project


class Command(BaseCommand):
    help = 'Re-index all News and Projects into Chroma using Ollama embeddings.'

    @transaction.atomic
    def handle(self, *args, **options):
        docs = []
        self.stdout.write(self.style.WARNING('Collecting News posts...'))
        for n in NewsPost.objects.all().iterator():
            text = f"News: {n.title}\nCategory: {n.get_category_display()}\n{n.content}"
            docs.append({'id': f'news:{n.id}', 'text': text, 'metadata': {'type': 'news', 'title': n.title, 'category': n.category}})

        self.stdout.write(self.style.WARNING('Collecting Projects...'))
        for p in Project.objects.all().iterator():
            skills = ', '.join(p.skills_list())
            text = f"Project: {p.title}\nSkills: {skills}\n{p.description}"
            docs.append({'id': f'project:{p.id}', 'text': text, 'metadata': {'type': 'project', 'title': p.title, 'skills': skills}})

        if not docs:
            self.stdout.write('No documents to index.')
            return

        self.stdout.write(self.style.WARNING(f'Indexing {len(docs)} documents...'))
        add_documents(docs)
        self.stdout.write(self.style.SUCCESS('Reindex complete.'))