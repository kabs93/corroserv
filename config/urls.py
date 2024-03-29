from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

from corroserv_inventory.core.api.views import (
    confirm_convert_materials,
    convert_material_consumption,
)

# from django.views.generic import TemplateView
# from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    # Core App
    path("", include("corroserv_inventory.core.urls", namespace="core")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("corroserv_inventory.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    path(
        "api/confirm-convert-materials/",
        confirm_convert_materials,
        name="confirm_convert_materials",
    ),
    path(
        "api/convert-material-consumption/<int:convert_material_id>/<uuid:location_uuid>/",
        convert_material_consumption,
        name="convert_material_consumption",
    ),
    # DRF auth token
    # path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
