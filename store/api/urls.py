from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()

router.register("items", views.ItemViewSet, basename="items")
router.register("orders", views.OrderViewSet, basename="orders")
router.register("order-items", views.ItemInOrderRelationshipViewSet, basename="order-items")
router.register("top-up", views.TopUpBalanceViewSet, basename="top-up")

urlpatterns = [
    path('auth/', include('user_backends.urls')),
]

urlpatterns += router.urls