from rest_framework.routers import DefaultRouter
from user_backends import views

router = DefaultRouter()

router.register("users", views.UserViewSet, basename="users")

urlpatterns = router.urls
