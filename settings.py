import os

from django.conf import settings


def configure_settings():
    """
    Configures settings for manage.py and for run_tests.py.
    """

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    if not settings.configured:
        # Determine the database settings depending on if a test_db var is set in CI mode or not
        test_db = os.environ.get('DB', None)

        if test_db is None:
            db_config = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'ambition',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'db',
                'TEST': {
                    'NAME': 'test_entity_emailer'
                }
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
            ENTITY_EMAILER_MAX_SEND_MESSAGE_TRIES=3,
            DATABASES={
                'default': db_config,
            },
            INSTALLED_APPS=(
                'db_mutex',
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.messages',
                'django.contrib.sessions',
                'entity',
                'entity_event',
                'entity_emailer',
                'entity_emailer.tests',
            ),
            MIDDLEWARE=(
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ),
            ROOT_URLCONF='entity_emailer.urls',
            DEFAULT_FROM_EMAIL='test@example.com',
            DEBUG=False,
            TEMPLATES=[{
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages'
                    ]
                }
            }],
            TEST_RUNNER='django_nose.NoseTestSuiteRunner',
            NOSE_ARGS=['--nocapture', '--nologcapture', '--verbosity=1'],
        )
