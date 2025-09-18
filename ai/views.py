from datetime import date
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from news.models import NewsPost
from .ai_services import query_similar, ollama_generate


@require_POST
@login_required
def chat_assistant(request):
    question = (request.POST.get('q') or '').strip()
    if not question:
        return HttpResponseBadRequest('Missing q')
    retrieved = query_similar(question, n=6)
    context_blocks = []
    for r in retrieved:
        meta = r.get('metadata') or {}
        prefix = 'News' if meta.get('type') == 'news' else 'Project'
        context_blocks.append(f"[{prefix}] {meta.get('title','')}\n{r.get('text','')}")
    context_text = "\n\n".join(context_blocks) if context_blocks else "No context found."
    prompt = (
        "You are a helpful university assistant. Use the provided context to answer the user's question accurately.\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n"
        "Answer concisely and cite whether info came from News or Projects when relevant."
    )
    answer = ollama_generate(prompt)
    return JsonResponse({'answer': answer, 'used_context': len(context_blocks)})


@login_required
def news_summary_today(request):
    today = timezone.localdate()
    posts = NewsPost.objects.filter(created_at__date=today).order_by('-created_at')
    if not posts.exists():
        return JsonResponse({'summary': 'No news published today.'})
    joined = "\n\n".join([f"- {p.title}: {p.content}" for p in posts])
    prompt = (
        "Summarize today's university news into 4-6 bullet points that capture key updates.\n"
        f"Today's items:\n{joined}\n"
        "Provide a student-friendly, factual summary."
    )
    summary = ollama_generate(prompt)
    return JsonResponse({'summary': summary, 'count': posts.count()})


@require_POST
@login_required
def news_qa_today(request):
    question = (request.POST.get('q') or '').strip()
    if not question:
        return HttpResponseBadRequest('Missing q')
    today = timezone.localdate()
    posts = NewsPost.objects.filter(created_at__date=today).order_by('-created_at')
    if not posts.exists():
        return JsonResponse({'answer': 'No news published today.', 'count': 0})
    joined = "\n\n".join([f"- {p.title}: {p.content}" for p in posts])
    prompt = (
        "You are a helpful university assistant. Using ONLY the provided items from today's news, answer the user's question precisely.\n"
        "If the user asks for a count, respond with the number first, followed by a short explanation.\n"
        f"Today's items:\n{joined}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    answer = ollama_generate(prompt)
    return JsonResponse({'answer': answer, 'count': posts.count()})