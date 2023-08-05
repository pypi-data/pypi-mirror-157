from django.apps import AppConfig


class EasyauditfarruxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Easy Audit Farrux Application'
    name = 'easyauditfarrux'

    def ready(self):
        from easyauditfarrux.signals import auth_signals, model_signals, request_signals
