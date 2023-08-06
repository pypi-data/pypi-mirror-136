=========================
Betik Application Staff
=========================

This application provides opportunities such as recording all personal and registration information of employees in a corporate company, leave tracking, report, entry-exit times, overtime information.

Quick start
-----------

1. Install 3rd. party application::

    pip install django-filter
    pip install djangorestframework
    pip install drf-yasg

2. Add "betik_app_xxx" and 3rd. party application to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        "django_filters",
        "rest_framework",
        "drf-yasg",

        "betik_app_staff",
    ]


3. Add the following options in settings like this::

    AUTH_USER_MODEL = 'auth.User'
    TESTING = True if sys.argv[1:2] == ['test'] else False

4. Create pagination.py file in project main folder and paste following lines::

    from rest_framework.pagination import PageNumberPagination
    class StandardPagination(PageNumberPagination):
        page_size = 50
        page_size_query_param = 'page_size'

7. Run ``python manage.py migrate`` to create the location models.

8. Include the location URLconf in your project urls.py like this::

    path('betik-app-staff/', include('betik_app_staff.urls')),

9. Visit http://127.0.0.1:8000/betik-app-staff/ to participate.

10. Visit http://127.0.0.1:8000/doc to swagger documentation.