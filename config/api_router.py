from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

# from corroserv_inventory.users.api.views import UserViewSet
from corroserv_inventory.core.api.views import MaterialViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# router.register("users", UserViewSet)
router.register("materials", MaterialViewSet)


app_name = "api"
urlpatterns = router.urls
