"""date : 14/11/2026"""
from datetime import datetime


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
