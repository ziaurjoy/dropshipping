from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = 'users_app'
    verbose_name = 'Users Management'

    def ready(self):
        """
        Register signal handlers when the app is ready.
        This ensures that when a User is created, a Profile is automatically created.
        """
        import users_app.signals
