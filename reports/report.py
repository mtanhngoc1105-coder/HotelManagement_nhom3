"""Dịch vụ tính toán và hiển thị báo cáo hoạt động khách sạn."""

from datetime import date

from managers.booking_manager import BookingManager
from managers.room_manager import RoomManager
from models.booking import BookingStatus


class ReportService:
    """Tính và hiển thị báo cáo từ các manager đang được HotelManager quản lý."""

    def __init__(
        self, booking_manager: BookingManager, room_manager: RoomManager
    ) -> None:
        self.booking_manager = booking_manager
        self.room_manager = room_manager

    def calculate_revenue(self, start_date: date, end_date: date) -> float:
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise TypeError("start_date và end_date phải là kiểu date.")
        if start_date > end_date:
            raise ValueError("start_date không được sau end_date.")

        return sum(
            booking.total_price
            for booking in self.booking_manager.bookings
            if booking.status != BookingStatus.CANCELLED.value
            and start_date <= booking.check_in <= end_date
        )

    def calculate_occupancy_rate(self) -> float:
        rooms = self.room_manager.rooms
        if not rooms:
            return 0.0

        occupied = sum(
            1 for room in rooms if room.status.value == "OCCUPIED"
        )
        return round(occupied / len(rooms) * 100, 2)

    def get_bookings_by_date(self, target_date: date) -> list:
        return self.booking_manager.get_bookings_by_date(target_date)

    def display_revenue_report(self) -> None:
        revenue = self.calculate_revenue(date.min, date.max)
        print(f"Doanh thu: {revenue:,.0f} VND")

    def display_occupancy_report(self) -> None:
        rooms = self.room_manager.rooms
        rate = self.calculate_occupancy_rate()
        occupied = sum(
            1 for room in rooms if room.status.value == "OCCUPIED"
        )
        print(f"Số phòng đang sử dụng: {occupied}/{len(rooms)}")
        print(f"Tỷ lệ sử dụng phòng: {rate:.2f}%")


class HotelReport:
    """Lớp thống kê hoạt động khách sạn."""

    def __init__(self, rooms=None, bookings=None):
        self.rooms = rooms if rooms is not None else []
        self.bookings = bookings if bookings is not None else []

    # 1. Thống kê tổng doanh thu
    def tinh_doanh_thu(self):
        doanh_thu = 0

        for booking in self.bookings:
            if booking.get("status") != "cancelled":
                doanh_thu += float(booking.get("total_price", 0))

        return doanh_thu

    # 2. Tính tỷ lệ sử dụng phòng
    def tinh_ty_le_su_dung_phong(self):
        if not self.rooms:
            return 0

        so_phong_da_su_dung = sum(
            1 for room in self.rooms
            if room.get("status") == "occupied"
        )

        return round(
            so_phong_da_su_dung / len(self.rooms) * 100, 2
        )

    # 3. Thống kê đặt phòng theo ngày
    def thong_ke_dat_phong_theo_ngay(self):
        thong_ke = {}

        for booking in self.bookings:
            if booking.get("status") == "cancelled":
                continue

            ngay = booking.get("check_in")

            if ngay:
                thong_ke[ngay] = thong_ke.get(ngay, 0) + 1

        return thong_ke

    # 4. Hiển thị báo cáo tổng hợp
    def hien_thi_bao_cao(self):
        print("\n========== BAO CAO KHACH SAN ==========")

        print(f"Tong so phong: {len(self.rooms)}")

        print(
            f"Doanh thu: {self.tinh_doanh_thu():,.0f} VND"
        )

        print(
            f"Ty le su dung phong: "
            f"{self.tinh_ty_le_su_dung_phong()}%"
        )

        print("\nSo luot dat phong theo ngay:")

        thong_ke = self.thong_ke_dat_phong_theo_ngay()

        if not thong_ke:
            print("Chua co du lieu dat phong.")
        else:
            for ngay, so_luong in sorted(thong_ke.items()):
                print(f"{ngay}: {so_luong} luot")

        print("=======================================")
