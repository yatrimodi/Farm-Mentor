from django.apps import AppConfig


class FarmMentorAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "farm_mentor_app"

    def ready(self):
        import farm_mentor_app.signals
