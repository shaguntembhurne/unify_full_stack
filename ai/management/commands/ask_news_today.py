from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from news.models import NewsPost
from ai.ai_services import ollama_generate


class Command(BaseCommand):
    help = "Ask a question over today's news items using local Ollama"

    def add_arguments(self, parser):
        parser.add_argument('question', type=str, nargs='+', help='Question to ask about today\'s news')

    def handle(self, *args, **options):
        question = ' '.join(options['question']).strip()
        today = timezone.localdate()
        posts = NewsPost.objects.filter(created_at__date=today).order_by('-created_at')
        if not posts.exists():
            self.stdout.write('No news published today.')
            return
        joined = "\n\n".join([f"- {p.title}: {p.content}" for p in posts])
        prompt = (
            "You are a helpful university assistant. Using ONLY the provided items from today's news, answer the user's question precisely.\n"
            "If the user asks for a count, respond with the number first, followed by a short explanation.\n"
            f"Today's items:\n{joined}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        answer = ollama_generate(prompt)
        self.stdout.write(answer)
