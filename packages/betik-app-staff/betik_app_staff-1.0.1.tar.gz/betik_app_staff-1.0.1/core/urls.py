from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.utils.translation import gettext as _
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from core import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Betik Application Staff",
        default_version='1.0.0',
        description="This application provides opportunities such as recording all personal and registration information of employees in a corporate company, leave tracking, report, entry-exit times, overtime information.",
        contact=openapi.Contact(email="info@betik.com.tr"),
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

    path(
        'betik-app-email/',
        include('betik_app_email.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_email',
            'name': 'Email Application'
        }
    ),

    path(
        'betik-app-auth/',
        include('betik_app_auth.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_auth',
            'name': _('Auth Application')
        }
    ),

    path(
        'betik-app-location/',
        include('betik_app_location.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_location',
            'name': 'Location Application'
        }
    ),

    path(
        'betik-app-sms/',
        include('betik_app_sms.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_sms',
            'name': _('Sms Application')
        }
    ),

    path(
        'betik-app-person/',
        include('betik_app_person.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_person',
            'name': 'Person Application'
        }
    ),

    path(
        'betik-app-print-file/',
        include('betik_app_print_file.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_print_file',
            'name': _('File Output Application')
        }
    ),

    path(
        'betik-app-private/',
        include('betik_app_private.urls'),
        kwargs={
            'accept': True,
            'code': 'betik_app_private',
            'name': 'Application Name'
        }
    ),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
