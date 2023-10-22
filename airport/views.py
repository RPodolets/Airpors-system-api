from datetime import datetime

from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order,
)
from .permissions import IsAdminOrIfAuthenticatedReadOnly
from .serializers import (
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    OrderSerializer,
    OrderListSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    FlightCreateSerializer,
)


def _params_to_ints(qs):
    return [int(str_id) for str_id in qs.split(",")]


class AirportViewSet(
    viewsets.ModelViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            source_ids = _params_to_ints(source)
            queryset = queryset.filter(source__id__in=source_ids)
        if destination:
            destination_ids = _params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by source id (ex. ?genres=2,5)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by destination id (ex. ?actors=2,5)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        name = self.request.query_params.get("name")
        types = self.request.query_params.get("types")
        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)
        if types:
            type_ids = _params_to_ints(types)
            queryset = queryset.filter(type__id__in=type_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by name (ex. ?name=Boing)",
            ),
            OpenApiParameter(
                "types",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by airplane_type id "
                            "(ex. ?airplane_types=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane"
    ).prefetch_related("crew")
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        arrival_time = self.request.query_params.get("arrival_time")
        departure_time = self.request.query_params.get("departure_time")
        route_id_str = self.request.query_params.get("route")

        queryset = self.queryset

        if arrival_time:
            date = datetime.strptime(arrival_time, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=date)

        if departure_time:
            date = datetime.strptime(departure_time, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if route_id_str:
            queryset = queryset.filter(route_id=int(route_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        if self.action == "create":
            return FlightCreateSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type=OpenApiTypes.INT,
                description="Filter by route id (ex. ?route=1)",
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by arrival time of Flight "
                    "(ex. ?arrival_time=2022-10-23)"
                ),
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATE,
                description=(
                    "Filter by departure time of Flight "
                    "(ex. ?departure_time=2022-10-23)"
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
