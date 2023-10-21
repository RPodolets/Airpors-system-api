from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet,
    RouteViewSet,
    AirplaneViewSet,
    OrderViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("crew", CrewViewSet)
router.register("routes", RouteViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("orders", OrderViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
