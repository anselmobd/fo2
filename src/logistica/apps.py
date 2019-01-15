from django.apps import AppConfig


class LogisticaConfig(AppConfig):
    name = 'logistica'
    verbose_name = 'Logística'

    def ready(self):
        import logistica.signals
