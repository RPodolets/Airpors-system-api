from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
    Flight,
)
from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer,
)

FLIGHT_LIST_URL = reverse("airport:flight-list")
ORDER_LIST_URL = reverse("airport:order-list")
ROUTE_LIST_URL = reverse("airport:route-list")


def sample_airport(**params):
    defaults = {
        "name": "airport_name",
        "closest_big_city": "city_nearby",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_airplane_type(**params):
    id = AirplaneType.objects.count() + 1
    defaults = {
        "name": f"airplane_type #{id}",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    defaults = {
        "name": f"Boing",
        "rows": 10,
        "seats_in_row": 10,
        "type": sample_airplane_type(),
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": f"Test first name",
        "last_name": f"Test last name",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_airport(name="Airport 1"),
        "destination": sample_airport(name="Airport 2"),
        "distance": 200,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    defaults = {
        "route": sample_route(),
        "airplane": sample_airplane(),
        "departure_time": timezone.now() + timedelta(hours=1),
        "arrival_time": timezone.now() + timedelta(hours=2),
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


def detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        response = self.client.get(FLIGHT_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_auth_required(self):
        response = self.client.get(ORDER_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
        )
        self.flight = sample_flight()
        self.client.force_authenticate(self.user)

    def test_flight_list(self):
        sample_flight()
        sample_flight()

        response = self.client.get(FLIGHT_LIST_URL)

        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_flight_detail(self):
        response = self.client.get(detail_flight_url(self.flight.id))

        detail = Flight.objects.get(id=self.flight.id)
        serializer = FlightDetailSerializer(detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": sample_route(),
            "airplane": sample_airplane(),
            "departure_time": timezone.now() + timedelta(hours=1),
            "arrival_time": timezone.now() + timedelta(hours=2),
        }
        response = self.client.post(FLIGHT_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order(self):
        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
                {"row": 1, "seat": 2, "flight": self.flight.id},
            ]
        }

        response = self.client.post(ORDER_LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_order_must_be_validated(self):
        payload = {
            "tickets": [
                {"row": 1, "seat": 1, "flight": self.flight.id},
                {"row": 1, "seat": 1, "flight": self.flight.id},
            ]
        }

        response = self.client.post(ORDER_LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(ValidationError)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "test_password", is_staff=True
        )
        self.flight = sample_flight()
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = sample_airport(name="Airport 1")
        destination = sample_airport(name="Airport 2")

        payload = {
            "source": source,
            "destination": destination,
            "distance": 200,
        }

        response = self.client.post(ROUTE_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
