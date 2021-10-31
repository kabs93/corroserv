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
                path("<str:item_type>/", views.create, name="create"),
            ]
        ),
    ),
    path(
        "task/",
        include(
            [
                path("<str:task_type>/", views.task, name="task"),
                path(
                    "<str:task_type>/<uuid:item_uuid>/",
                    views.task_confirm,
                    name="task_confirm",
                ),
            ]
        ),
    ),
]
