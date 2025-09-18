from django.core.management.base import BaseCommand, CommandError
from ai.ai_services import query_similar, ollama_generate


class Command(BaseCommand):
    help = 'Test AI chat assistant end-to-end with a question.'

    def add_arguments(self, parser):
        parser.add_argument('question', type=str, help='The question to ask the assistant.')

    def handle(self, *args, **options):
        q = options['question']
        if not q:
            raise CommandError('Question is required')
        self.stdout.write(self.style.WARNING(f'Question: {q}'))
        retrieved = query_similar(q, n=6)
        context_blocks = []
        for r in retrieved:
            meta = r.get('metadata') or {}
            prefix = 'News' if meta.get('type') == 'news' else 'Project'
            context_blocks.append(f"[{prefix}] {meta.get('title','')}\n{r.get('text','')}")
        context_text = "\n\n".join(context_blocks) if context_blocks else "No context found."
        prompt = (
            "You are a helpful university assistant. Use the provided context to answer the user's question accurately.\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {q}\n"
            "Answer concisely and cite whether info came from News or Projects when relevant."
        )
        answer = ollama_generate(prompt)
        self.stdout.write(self.style.SUCCESS('Answer:'))
        self.stdout.write(answer)