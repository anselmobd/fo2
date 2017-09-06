from django.apps import AppConfig


class LogisticaConfig(AppConfig):
    name = 'logistica'
    verbose_name = 'logística'

    def ready(self):
        import logistica.signals
