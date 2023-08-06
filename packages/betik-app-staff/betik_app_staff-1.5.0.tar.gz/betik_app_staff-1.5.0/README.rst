=========================
Betik Application Staff
=========================

This application provides opportunities such as recording all personal and registration information of employees in a corporate company, leave tracking, report, entry-exit times, overtime information.

Quick start
-----------

- Install 3rd. party application::

    pip install architect==0.6.0
    pip install celery==5.0.5
    pip install celery-once==3.0.1
    pip install django-filter==2.4.0
    pip install djangorestframework==3.12.2
    pip install drf-yasg==1.20.0
    pip install Faker==8.1.3
    pip install freezegun==1.1.0
    pip install redis==3.5.3

- Create exception_handler.py file at your project folder and paste the following code::

    def custom_exception_handler(exc, context):
        response = exception_handler(exc, context)

        if isinstance(exc, StaffConflictWorkingTimeError):
            response.data['staff_errors'] = exc.item_errors

        return response

- Add ``betik_app_staff`` and 3rd. party application to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        "django_filters",
        "rest_framework",
        "drf-yasg",
        "django_cleanup",

        "betik_app_staff"
    ]

- install ``betik_app_util``. See documentation:
    http://188.132.205.203/django_app/betik_app_util/-/blob/master/README.rst

- install ``betik_app_auth``. See documentation:

    http://188.132.205.203/django_app/betik_app_auth/-/blob/master/README.rst

- install ``betik_app_email``. See documentation:

    http://188.132.205.203/django_app/betik_app_email/-/blob/master/README.rst

- install ``betik_app_sms``. See documentation:

    http://188.132.205.203/django_app/betik_app_sms/-/blob/master/README.rst

- install ``betik_app_person``. See documentation:

    http://188.132.205.203/django_app/betik_app_person/-/blob/master/README.rst

- install ``betik_app_acs``. See documentation:

    http://188.132.205.203/django_app/betik_app_acs/-/blob/master/README.rst

- install ``betik_app_document``. See documentation:

    http://188.132.205.203/django_app/betik_app_document/-/blob/master/README.rst

- Add swagger settings to your settings.py file::

     SWAGGER_SETTINGS = {
        'LOGIN_URL': 'rest_framework:login',
        'LOGOUT_URL': 'rest_framework:logout'
     }

- Add rest framework settings to your settings.py file::

    REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'betik_app_auth.permissions.HasViewPermission',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'NON_FIELD_ERRORS_KEY': 'detail',
    'EXCEPTION_HANDLER': 'core.exception_handlers.custom_exception_handler'
    }

- Add celery settings to your settings.py file::

    BROKER_URL = os.environ.get('BROKER_URL')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    CELERY_ACCEPT_CONTENT = os.environ.get('CELERY_ACCEPT_CONTENT', 'application/json').split(',')
    ONCE_CELERY_BROKER_URL = os.environ.get('ONCE_CELERY_BROKER_URL')

- Run ``python manage.py migrate`` to create the models.

- Run ``python manage.py create_bank_holidays`` to create the bank holidays.

- Run ``python manage.py create_leave_types`` to create the leave types.

- Run ``architect partition --module betik_app_staff.models`` to create partitions.

- Include the location URLconf in your project urls.py like this::

    # for swagger documentation
    schema_view = get_schema_view(
        openapi.Info(
            title="Betik Application Staff",
            default_version='0.0.0',
            description="",
            contact=openapi.Contact(email="test@test"),
        ),
        public=True,
        permission_classes=(permissions.IsAuthenticatedOrReadOnly,)
    )

    urlpatterns = [
        re_path(r'^api/doc(?P<format>\.json|\.yaml)/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('api/doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
        path('api/admin/', admin.site.urls),

        path(
            'betik-app-staff/',
            include('betik_app_staff.urls'),
            kwargs={
                'accept': True,
                'code': 'betik_app_staff',
                'name': _('Staff Application')
            }
        ),
    ]

- Paste the code below into the __init__.py file at project folder::

    from .celery import app as celery_app
    __all__ = ('celery_app',)

- Paste the code below into the celery.py file at project folder::

    app.conf.beat_schedule = {
        "apply_working_hour": {
            "task": "betik_app_staff.tasks.change_shift_period_and_apply_working_hours",
            "schedule": crontab(hour=0, minute=0)
        },

        "apply_find_in_out_time": {
            "task": "betik_app_staff.tasks.find_in_out_times",
            'schedule': crontab(hour='*/1', minute=0),
        },
    }

    app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': settings.ONCE_CELERY_BROKER_URL,
        'default_timeout': 2 * 60 * 60
        }
    }

- Visit http://127.0.0.1:8000/betik-app-staff/ to participate.

- Visit http://127.0.0.1:8000/betik-app-staff/api/doc to swagger documentation

- Visit http://127.0.0.1:8000/betik-app-staff/api/admin to admin panel