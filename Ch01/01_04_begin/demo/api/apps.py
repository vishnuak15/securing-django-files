from django.apps import AppConfig

def setup_group_permissions(sender, **kwargs):
    pass

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        pass
