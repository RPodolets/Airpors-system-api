from django.contrib.auth import get_user_model
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=63)
    closest_big_city = models.CharField(max_length=63)

    def __str__(self):
        return f"City: {self.closest_big_city}; Airport: {self.name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=63)

    def __str__(self):
        return f" Airplane type: {self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=63)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    def __str__(self):
        return f"Airplane: {self.name}"

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return f"Crew member: {self.first_name} {self.last_name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return (
            f"Route from:{self.source.closest_big_city} "
            f"to {self.destination.closest_big_city}; "
            f"Distance: {self.distance}"
        )


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return (
            f"Route: {self.route}; "
            f"Time: {self.departure_time} - {self.arrival_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders"
    )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]
