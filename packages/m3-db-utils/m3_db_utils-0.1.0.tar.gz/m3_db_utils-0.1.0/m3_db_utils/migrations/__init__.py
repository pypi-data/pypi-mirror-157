from django.db.models.signals import (
    post_migrate,
)

from m3_db_utils.api import (
    update_model_enum_values,
)


def post_migrate_receiver(sender, app_config, **kwargs):
    """
    Выполняет обновление значений моделей-перечислений после выполнения миграций
    """
    if app_config.name == 'm3_db_utils':
        update_model_enum_values()


post_migrate.connect(post_migrate_receiver)
