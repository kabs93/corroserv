from django.urls import include, path
from django.views.generic import TemplateView

from . import views

app_name = "core"
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),
    path("home/", views.home, name="home"),
    path(
        "create/",
        include(
            [
                path(
                    "<str:item_type>/",
                    views.create,
                    name="create",
                ),
                # path(
                #     "<str:item_type>/<uuid:inventory_item_id>",
                #     views.create_confirm,
                #     name="create_confirm",
                # ),
            ]
        ),
    ),
    path(
        "movement/",
        include(
            [
                path(
                    "<str:movement_type>/",
                    views.movement,
                    name="movement",
                ),
                path(
                    "<str:movement_type>/<uuid:item_uuid>/",
                    views.movement_confirm,
                    name="movement_confirm",
                ),
                path(
                    "<str:movement_type>/<uuid:item_uuid>/<int:inventory_item_id>",
                    views.movement_confirm,
                    name="movement_confirm",
                ),
            ]
        ),
    ),
]
