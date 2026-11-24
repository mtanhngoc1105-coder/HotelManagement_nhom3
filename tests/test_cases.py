
import unittest
from reports.report import HotelReport


class TestHotelReport(unittest.TestCase):

    def setUp(self):
        """Tạo dữ liệu mẫu trước mỗi lần kiểm thử."""

        self.rooms = [
            {"room_id": 101, "status": "occupied"},
            {"room_id": 102, "status": "occupied"},
            {"room_id": 103, "status": "available"},
            {"room_id": 104, "status": "available"}
        ]

        self.bookings = [
            {
                "check_in": "2026-11-14",
                "total_price": 1000000,
                "status": "confirmed"
            },
            {
                "check_in": "2026-11-14",
                "total_price": 1500000,
                "status": "confirmed"
            },
            {
                "check_in": "2026-11-15",
                "total_price": 800000,
                "status": "cancelled"
            }
        ]

        self.report = HotelReport(
            self.rooms,
            self.bookings
        )

    # TC01: Kiểm tra tổng doanh thu
    def test_tinh_doanh_thu(self):
        self.assertEqual(
            self.report.tinh_doanh_thu(),
            2500000
        )

    # TC02: Kiểm tra không tính doanh thu đơn đã hủy
    def test_loai_bo_don_huy(self):
        doanh_thu = self.report.tinh_doanh_thu()

        self.assertNotEqual(doanh_thu, 3300000)
        self.assertEqual(doanh_thu, 2500000)

    # TC03: Kiểm tra tỷ lệ sử dụng phòng
    def test_ty_le_su_dung_phong(self):
        self.assertEqual(
            self.report.tinh_ty_le_su_dung_phong(),
            50.0
        )

    # TC04: Kiểm tra khi không có phòng
    def test_khong_co_phong(self):
        report = HotelReport([], self.bookings)

        self.assertEqual(
            report.tinh_ty_le_su_dung_phong(),
            0
        )

    # TC05: Kiểm tra thống kê đặt phòng theo ngày
    def test_thong_ke_dat_phong(self):
        ket_qua = self.report.thong_ke_dat_phong_theo_ngay()

        self.assertEqual(
            ket_qua,
            {"2026-11-14": 2}
        )

    # TC06: Kiểm tra không tính lượt đặt phòng đã hủy
    def test_khong_tinh_luot_dat_phong_da_huy(self):
        ket_qua = self.report.thong_ke_dat_phong_theo_ngay()

        self.assertNotIn("2026-11-15", ket_qua)

    # TC07: Kiểm tra khi không có đặt phòng
    def test_khong_co_dat_phong(self):
        report = HotelReport(self.rooms, [])

        self.assertEqual(
            report.tinh_doanh_thu(),
            0
        )

        self.assertEqual(
            report.thong_ke_dat_phong_theo_ngay(),
            {}
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
