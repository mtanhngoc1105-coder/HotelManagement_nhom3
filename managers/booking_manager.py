# ==============================================================================
# File: managers/booking_manager.py
# Mô tả: Lớp BookingManager chịu trách nhiệm QUẢN LÝ DANH SÁCH các Booking:
#        thêm, tìm, huỷ, check-in, check-out, tìm kiếm, lọc theo ngày.
# Quan hệ trong UML: HotelManager chứa 1 BookingManager (composition),
#        BookingManager quản lý 0..* Booking (aggregation).
# ==============================================================================

from datetime import date                            # Dùng cho kiểu tham số ngày
from models.booking import Booking, BookingStatus   # Import lớp model và Enum trạng thái


class BookingManager:

    # --------------------------------------------------------------------------
    # HÀM KHỞI TẠO
    # --------------------------------------------------------------------------
    def __init__(self):
        # -list bookings : danh sách chứa tất cả Booking trong hệ thống
        # Ban đầu rỗng, sẽ được thêm dần bằng create_booking()
        # hoặc được nạp từ file JSON thông qua setter bên dưới
        self.__bookings = []

    # --------------------------------------------------------------------------
    # GETTER cho danh sách bookings
    # Vì __bookings là private nên các lớp khác muốn đọc phải đi qua getter này
    # Ai cần dùng: ReportService (tính doanh thu), JSONStorage (lưu file)
    # Dùng: booking_manager.bookings   (không có dấu ngoặc)
    # --------------------------------------------------------------------------
    @property
    def bookings(self) -> list:
        return self.__bookings

    # --------------------------------------------------------------------------
    # SETTER cho danh sách bookings
    # Cho phép gán cả danh sách mới vào: booking_manager.bookings = [...]
    # Dùng khi HotelManager nạp dữ liệu từ file JSON lên lúc khởi động chương trình
    # --------------------------------------------------------------------------
    @bookings.setter
    def bookings(self, value: list) -> None:
        self.__bookings = value

    # --------------------------------------------------------------------------
    # +find_booking(booking_id) : Booking
    # Tìm 1 booking theo mã. Trả về đối tượng Booking, không thấy thì trả về None
    # Đây là hàm nền tảng, các hàm cancel/check_in/check_out đều gọi lại hàm này
    # --------------------------------------------------------------------------
    def find_booking(self, booking_id: str):
        """Tìm booking theo mã. Không thấy thì trả về None."""
        # Duyệt tuần tự từng booking trong danh sách
        for b in self.__bookings:
            # So sánh mã của booking đang xét với mã cần tìm
            if b.booking_id == booking_id:
                return b        # Tìm thấy => trả về ngay, không duyệt tiếp
        # Duyệt hết mà không thấy => trả về None (nghĩa là "không có")
        return None

    # --------------------------------------------------------------------------
    # +check_room_availability(room_id, check_in, check_out) : bool
    # Kiểm tra 1 phòng có còn TRỐNG trong khoảng ngày [check_in, check_out) không
    # True = còn trống, đặt được. False = đã có người đặt trùng lịch
    # --------------------------------------------------------------------------
    def check_room_availability(self, room_id: str, check_in: date, check_out: date) -> bool:
        """Trả về True nếu phòng còn trống trong khoảng [check_in, check_out)."""
        for b in self.__bookings:

            # Booking của phòng khác thì không ảnh hưởng, bỏ qua
            if b.room_id != room_id:
                continue

            # Booking đã huỷ hoặc đã trả phòng => phòng đã được giải phóng, bỏ qua
            if b.status in (BookingStatus.CANCELLED.value,
                            BookingStatus.CHECKED_OUT.value):
                continue

            # Kiểm tra 2 khoảng ngày giao nhau (cùng công thức với check_overlap)
            # Khoảng muốn đặt: [check_in, check_out)
            # Khoảng đã có   : [b.check_in, b.check_out)
            if check_in < b.check_out and check_out > b.check_in:
                return False    # Có trùng => phòng không còn trống

        # Không có booking nào trùng => phòng trống
        return True

    # --------------------------------------------------------------------------
    # +create_booking(booking) : bool
    # Thêm 1 booking mới vào danh sách sau khi kiểm tra 3 điều kiện.
    # True = thêm thành công, False = bị từ chối
    # --------------------------------------------------------------------------
    def create_booking(self, booking: Booking) -> bool:
        """Thêm booking mới. Trả về False nếu không hợp lệ."""
        # Kiểm tra 1: mã booking không được trùng với booking đã có
        if self.find_booking(booking.booking_id) is not None:
            return False

        # Kiểm tra 2: ngày nhận/trả phải hợp lệ (gọi hàm của lớp Booking)
        if not booking.check_date_validity():
            return False

        # Kiểm tra 3: phòng phải còn trống trong khoảng ngày đó
        if not self.check_room_availability(booking.room_id,
                                            booking.check_in,
                                            booking.check_out):
            return False

        # Qua cả 3 kiểm tra => thêm vào danh sách
        self.__bookings.append(booking)
        return True

    # --------------------------------------------------------------------------
    # +cancel_booking(booking_id) : bool
    # Huỷ booking theo mã. True = huỷ thành công, False = thất bại
    # --------------------------------------------------------------------------
    def cancel_booking(self, booking_id: str) -> bool:
        """Huỷ booking theo mã."""
        # Bước 1: tìm booking
        booking = self.find_booking(booking_id)
        if booking is None:         # Không tồn tại mã này
            return False

        # Bước 2: gọi cancel() của Booking.
        # cancel() sẽ ném ValueError nếu trạng thái không cho phép huỷ,
        # nên phải bọc trong try/except để bắt lỗi và trả về False thay vì làm
        # chương trình bị dừng đột ngột.
        try:
            booking.cancel()
            return True             # Không có lỗi => huỷ thành công
        except ValueError:          # Bắt lỗi do sai trạng thái
            return False

    # --------------------------------------------------------------------------
    # +check_in(booking_id) : bool
    # Làm thủ tục nhận phòng cho 1 booking. Cấu trúc giống cancel_booking
    # --------------------------------------------------------------------------
    def check_in(self, booking_id: str) -> bool:
        """Làm thủ tục nhận phòng."""
        booking = self.find_booking(booking_id)     # Tìm booking theo mã
        if booking is None:
            return False                            # Không tìm thấy

        try:
            booking.check_in_room()                 # Đổi trạng thái sang CHECKED_IN
            return True
        except ValueError:                          # Booking chưa CONFIRMED
            return False

    # --------------------------------------------------------------------------
    # +check_out(booking_id) : bool
    # Làm thủ tục trả phòng cho 1 booking
    # --------------------------------------------------------------------------
    def check_out(self, booking_id: str) -> bool:
        """Làm thủ tục trả phòng."""
        booking = self.find_booking(booking_id)     # Tìm booking theo mã
        if booking is None:
            return False                            # Không tìm thấy

        try:
            booking.check_out_room()                # Đổi trạng thái sang CHECKED_OUT
            return True
        except ValueError:                          # Khách chưa check-in
            return False

    # --------------------------------------------------------------------------
    # +search_booking(keyword) : list
    # Tìm kiếm booking theo từ khoá. Trả về DANH SÁCH các booking khớp
    # (có thể rỗng nếu không có kết quả nào)
    # --------------------------------------------------------------------------
    def search_booking(self, keyword: str) -> list:
        """Tìm booking theo từ khoá (mã booking, mã khách, mã phòng hoặc trạng thái)."""
        # Chuẩn hoá từ khoá: .lower() chuyển chữ thường để không phân biệt hoa/thường,
        # .strip() bỏ khoảng trắng thừa ở 2 đầu
        keyword = keyword.lower().strip()

        result = []     # Danh sách chứa kết quả tìm được

        for b in self.__bookings:
            # "keyword in chuỗi" kiểm tra từ khoá có nằm trong chuỗi không
            # (tìm kiểu "chứa", ví dụ gõ "R10" sẽ ra R101, R102...)
            # Chỉ cần khớp 1 trong 4 trường là được (dùng "or")
            if (keyword in b.booking_id.lower()
                    or keyword in b.guest_id.lower()
                    or keyword in b.room_id.lower()
                    or keyword in b.status.lower()):
                result.append(b)    # Khớp => thêm vào danh sách kết quả

        return result

    # --------------------------------------------------------------------------
    # +get_bookings_by_date(date) : list
    # Lấy các booking ĐANG CHIẾM PHÒNG vào 1 ngày cụ thể.
    # ReportService dùng hàm này để tính tỉ lệ lấp đầy phòng theo ngày.
    # (Đặt tên tham số là target_date để không đè lên tên "date" của thư viện)
    # --------------------------------------------------------------------------
    def get_bookings_by_date(self, target_date: date) -> list:
        """Lấy các booking đang chiếm phòng vào ngày target_date."""
        result = []

        for b in self.__bookings:
            # Booking đã huỷ thì không tính là đang chiếm phòng
            if b.status == BookingStatus.CANCELLED.value:
                continue

            # Python cho phép viết so sánh kiểu chuỗi: a <= x < b
            # Nghĩa là: ngày nhận <= ngày cần xét < ngày trả
            # Dùng "<" ở ngày trả vì đúng ngày trả phòng thì phòng đã trống
            if b.check_in <= target_date < b.check_out:
                result.append(b)

        return result

    # --------------------------------------------------------------------------
    # display_bookings() : HÀM BỔ SUNG, KHÔNG CÓ TRONG UML
    # In toàn bộ danh sách booking ra màn hình, tiện cho menu của chương trình
    # --------------------------------------------------------------------------
    def display_bookings(self) -> None:
        # Danh sách rỗng thì báo cho người dùng biết rồi thoát luôn
        if not self.__bookings:
            print("Chưa có booking nào.")
            return

        # print(b) sẽ tự gọi hàm __str__() của Booking
        for b in self.__bookings:
            print(b)