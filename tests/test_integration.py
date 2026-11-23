from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from managers.hotel_manager import HotelManager
from models.booking import Booking, BookingStatus
from models.guest import Guest
from models.room import DeluxeRoom, Room, RoomStatus, StandardRoom
from utils.storage import JSONStorage


class TestHotelIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.output_redirect = redirect_stdout(StringIO())
        self.output_redirect.__enter__()
        self.hotel = HotelManager(self.temp_directory.name)
        self.check_in = date.today() + timedelta(days=1)
        self.check_out = self.check_in + timedelta(days=2)

    def tearDown(self):
        self.output_redirect.__exit__(None, None, None)
        self.temp_directory.cleanup()

    def test_booking_flow_and_json_restart(self):
        room = DeluxeRoom(
            "R101", "101", 100.0, RoomStatus.AVAILABLE, "Corner room", 2,
            ["Wi-Fi"], True,
        )
        standard_room = StandardRoom(
            "R102", "102", 75.0, RoomStatus.AVAILABLE, "Standard", 2,
            True, "Queen",
        )
        guest = Guest(
            "G1", "Nguyen An", "0912345678", "an@example.com",
            "Hanoi", "012345678901",
        )
        self.hotel.manage_rooms().add_room(room)
        self.hotel.manage_rooms().add_room(standard_room)
        self.hotel.manage_guests().add_guest(guest)

        booking = Booking("B1", "G1", "R101", self.check_in, self.check_out)
        self.assertTrue(self.hotel.create_booking(booking))
        self.assertEqual(booking.total_price, 300.0)

        booking.confirm()
        self.hotel.check_in("B1")
        self.assertEqual(room.status, RoomStatus.OCCUPIED)
        self.hotel.check_out("B1")
        self.assertEqual(room.status, RoomStatus.AVAILABLE)
        self.assertEqual(booking.status, BookingStatus.CHECKED_OUT.value)

        self.hotel.save_system_data()
        restarted = HotelManager(self.temp_directory.name)

        loaded_room = restarted.manage_rooms().find_room("R101")
        self.assertIsInstance(loaded_room, DeluxeRoom)
        self.assertEqual(loaded_room.amenities, ["Wi-Fi"])
        loaded_standard = restarted.manage_rooms().find_room("R102")
        self.assertIsInstance(loaded_standard, StandardRoom)
        self.assertEqual(loaded_standard.bed_type, "Queen")
        self.assertEqual(
            restarted.manage_guests().find_guest("G1").display_info(),
            guest.display_info(),
        )
        loaded_booking = restarted.manage_bookings().find_booking("B1")
        self.assertEqual(loaded_booking.status, BookingStatus.CHECKED_OUT.value)
        self.assertEqual(loaded_booking.total_price, 300.0)

    def test_report_service_uses_manager_models(self):
        room = Room("R1", "1", 50.0, "OCCUPIED", "", 1)
        self.hotel.manage_rooms().add_room(room)
        booking = Booking(
            "B1", "G1", "R1", self.check_in, self.check_out,
            status=BookingStatus.CONFIRMED.value, total_price=100.0,
        )
        cancelled = Booking(
            "B2", "G2", "R2", self.check_in, self.check_out,
            status=BookingStatus.CANCELLED.value, total_price=500.0,
        )
        bookings = self.hotel.manage_bookings()
        bookings.bookings.extend([booking, cancelled])

        report = self.hotel.get_report()
        self.assertEqual(report.calculate_revenue(self.check_in, self.check_in), 100.0)
        self.assertEqual(report.calculate_occupancy_rate(), 100.0)
        self.assertEqual(report.get_bookings_by_date(self.check_in), [booking])
        with self.assertRaises(ValueError):
            report.calculate_revenue(self.check_out, self.check_in)

    def test_room_and_guest_crud_search_and_sort(self):
        rooms = self.hotel.manage_rooms()
        cheaper = Room("R1", "101", 50.0, "AVAILABLE", "", 1)
        pricier = Room("R2", "102", 100.0, "AVAILABLE", "", 2)
        self.assertTrue(rooms.add_room(cheaper))
        self.assertTrue(rooms.add_room(pricier))
        self.assertTrue(rooms.update_room("R1", {"price": 75.0}))
        with patch("builtins.input", side_effect=["", "80", "", "", ""]):
            self.assertTrue(self.hotel.update_room("R1"))
        self.assertEqual(cheaper.price, 80.0)
        self.assertEqual(rooms.search_room("R1"), [cheaper])
        self.assertEqual(rooms.sort_rooms("price"), [cheaper, pricier])
        self.assertEqual(self.hotel.search_all("R1"), [cheaper])
        self.assertEqual(self.hotel.sort_all("price"), [cheaper, pricier])
        self.assertTrue(rooms.delete_room("R2"))

        guests = self.hotel.manage_guests()
        guest = Guest(
            "G1", "Nguyen An", "0912345678", "an@example.com",
            "Hanoi", "012345678901",
        )
        self.assertTrue(guests.add_guest(guest))
        self.assertEqual(guests.search_guest("an"), [guest])
        with patch(
            "builtins.input",
            side_effect=[
                "Nguyen Binh", "0987654321", "binh@example.com",
                "Hue", "012345678902",
            ],
        ):
            self.assertTrue(guests.update_guest("G1"))
        self.assertEqual(guests.find_guest("G1").display_info().splitlines()[1],
                         "Họ tên: Nguyen Binh")
        self.assertTrue(guests.delete_guest("G1"))

    def test_booking_overlap_search_and_cancel(self):
        self.hotel.manage_rooms().add_room(
            Room("R1", "101", 50.0, "AVAILABLE", "", 1)
        )
        self.hotel.manage_guests().add_guest(
            Guest(
                "G1", "Nguyen An", "0912345678", "an@example.com",
                "Hanoi", "012345678901",
            )
        )
        first = Booking("B1", "G1", "R1", self.check_in, self.check_out)
        overlap = Booking(
            "B2", "G1", "R1",
            self.check_in + timedelta(days=1),
            self.check_out + timedelta(days=1),
        )
        self.assertTrue(self.hotel.create_booking(first))
        self.assertFalse(self.hotel.create_booking(overlap))
        self.assertEqual(
            self.hotel.manage_bookings().search_booking("G1"), [first]
        )
        self.hotel.manage_bookings().cancel_booking("B1")
        self.assertEqual(first.status, BookingStatus.CANCELLED.value)
        self.assertTrue(self.hotel.create_booking(overlap))

    def test_invalid_json_is_reported(self):
        storage = JSONStorage(self.temp_directory.name)
        with open(
            f"{self.temp_directory.name}\\rooms.json", "w", encoding="utf-8"
        ) as data_file:
            data_file.write("{invalid json")
        with self.assertRaisesRegex(ValueError, "JSON"):
            storage.load_rooms()


if __name__ == "__main__":
    unittest.main()
