from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Betik Application Staff",
        default_version='0.0.0',
        description="This application provides opportunities such as recording all personal and registration information of employees in a corporate company, leave tracking, report, entry-exit times, overtime information.",
        contact=openapi.Contact(email="info@betik.com.tr"),
    ),
    public=True
)

urlpatterns = [
    url(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^doc/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/', admin.site.urls),
    path('betik-app-staff/', include('betik_app_staff.urls')),
]
