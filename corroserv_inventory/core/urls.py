from django.urls import include, path
from django.views.generic import TemplateView

from . import views

app_name = "core"
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="core/about.html"), name="about"),
    path("home/", views.home, name="home"),
    path(
        "view/",
        include(
            [
                # path("", views.view_all, name="view_all"),
                path("<str:item_type>/", views.view_specific, name="view_specific"),
            ]
        ),
    ),
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
                path(
                    "Convert/",
                    include(
                        [
                            path(
                                "select-product",
                                views.convert_select_product,
                                name="convert_select_product",
                            ),
                            path(
                                "materials/<uuid:product_uuid>/",
                                views.convert_materials,
                                name="convert_materials",
                            ),
                            path(
                                "main/<int:convert_task_id>/",
                                views.convert_task_main,
                                name="convert_task_main",
                            ),
                            path(
                                "main/<int:convert_task_id>/<int:convert_material_id>/",
                                views.convert_material_locations,
                                name="convert_material_locations",
                            ),
                            path(
                                "main/<int:convert_task_id>/<int:convert_material_id>/<uuid:location_uuid>/",
                                views.convert_material_consumption,
                                name="convert_material_consumption",
                            ),
                            path(
                                "confirm/<int:convert_task_id>/",
                                views.convert_confirm_product_quantity,
                                name="convert_confirm_product_quantity",
                            ),
                        ]
                    ),
                ),
                path("<str:task_type>/", views.task, name="task"),
                path(
                    "<str:task_type>/select_item/",
                    views.task_select_item,
                    name="task_select_item",
                ),
                path(
                    "<str:task_type>/<uuid:item_uuid>/",
                    views.task_confirm,
                    name="task_confirm",
                ),
                path("<int:task_id>/details/", views.task_details, name="task_details"),
            ]
        ),
    ),
]
