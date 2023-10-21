from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
    Order,
    Ticket,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "type", "capacity")


class AirplaneListSerializer(AirplaneSerializer):
    type = serializers.SlugRelatedField(slug_field="name", read_only=True)


class AirplaneDetailSerializer(AirplaneSerializer):
    type = AirplaneTypeSerializer()


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, data):
        source = data["source"]
        destination = data["destination"]
        distance = data["distance"]

        if distance <= 1:
            raise serializers.ValidationError(
                "Distance must be greater than 0"
            )

        if source == destination:
            raise serializers.ValidationError("Flight to the same city")

        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer()
    destination = AirportSerializer()


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time")


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane = serializers.StringRelatedField(read_only=True)


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer()
    airplane = AirplaneListSerializer()
    crew = CrewSerializer(many=True)
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_places",
        )


class FlightCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "airplane",
            "route",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketSerializer):
    flight = FlightSerializer(many=False, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def validate(self, data):
        tickets_data = data.get("tickets", [])
        ticket_set = set()
        for ticket_data in tickets_data:
            ticket = (ticket_data.get("row"), ticket_data.get("seat"), ticket_data.get("flight"))
            if ticket in ticket_set:
                raise ValidationError("Duplicate ticket found in input data.")
            ticket_set.add(ticket)
        return data

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
