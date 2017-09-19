import os

from celery import Celery
from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    app = Celery('entity_emailer')
    app.config_from_object('django.conf:settings')
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', None)

        if test_db is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ambition_test',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db',
            }
        elif test_db == 'postgres':
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'USER': 'postgres',
                'NAME': 'entity',
            }
        else:
            raise RuntimeError('Unsupported test DB {0}'.format(test_db))

        settings.configure(
            MIDDLEWARE_CLASSES=(),
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'db_mutex',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.admin',
                'entity',
                'entity_event',
                'entity_emailer',
                'entity_emailer.tests',
            ),
            ROOT_URLCONF='entity_emailer.urls',
            DEFAULT_FROM_EMAIL='test@example.com',
            DEBUG=False,
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'APP_DIRS': True,
                },
            ]
        )
