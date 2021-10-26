from django.urls import include, path
from django.views.generic import TemplateView

from . import views

app_name = "core"
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),
    path("home/", views.home, name="home"),
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
                    "<str:movement_type>/<int:inventory_item_id>",
                    views.movement_confirm,
                    name="movement_confirm",
                ),
            ]
        ),
    ),
]
