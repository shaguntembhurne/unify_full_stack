from django.db.models.signals import post_save
from django.dispatch import receiver
from news.models import NewsPost
from projects.models import Project
from .ai_services import add_documents
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=NewsPost)
def index_news(sender, instance: NewsPost, created, **kwargs):
    text = f"News: {instance.title}\nCategory: {instance.get_category_display()}\n{instance.content}"
    try:
        add_documents([
            {
                'id': f"news:{instance.id}",
                'text': text,
                'metadata': {'type': 'news', 'title': instance.title, 'category': instance.category}
            }
        ])
    except Exception as e:
        logger.warning("Failed to index news %s: %s", instance.id, e)


@receiver(post_save, sender=Project)
def index_project(sender, instance: Project, created, **kwargs):
    skills = ', '.join(instance.skills_list())
    text = f"Project: {instance.title}\nSkills: {skills}\n{instance.description}"
    try:
        add_documents([
            {
                'id': f"project:{instance.id}",
                'text': text,
                'metadata': {'type': 'project', 'title': instance.title, 'skills': skills}
            }
        ])
    except Exception as e:
        logger.warning("Failed to index project %s: %s", instance.id, e)