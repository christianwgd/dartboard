from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MatchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'match'
    verbose_name = _('Match')
