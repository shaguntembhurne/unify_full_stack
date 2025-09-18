from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'

    def ready(self):
        # Import signals to ensure handlers are registered
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass