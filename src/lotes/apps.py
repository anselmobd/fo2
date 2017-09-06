from django.apps import AppConfig


class LotesConfig(AppConfig):
    name = 'lotes'

    def ready(self):
        import lotes.signals
