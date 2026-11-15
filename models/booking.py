# Mô tả: Chứa 2 thành phần:
#   1. BookingStatus : Enum liệt kê các trạng thái của một lượt đặt phòng
#   2. Booking       : Lớp đại diện cho 1 lượt đặt phòng của khách hàng
# ==============================================================================

# Import "date" để lưu ngày nhận/trả phòng (chỉ có năm-tháng-ngày)
# Import "datetime" để lưu ngày giờ đặt phòng (có cả giờ phút giây)
from datetime import date, datetime

# Import "Enum" để tạo kiểu liệt kê, giúp tránh gõ sai chuỗi trạng thái
# (ví dụ gõ nhầm "CONFRIMED" thì Enum sẽ báo lỗi ngay, còn chuỗi thường thì không)
from enum import Enum


# ==============================================================================
# ENUM BookingStatus
# Khớp với khối <<enumeration>> BookingStatus trong sơ đồ UML
# Vòng đời của một booking: PENDING -> CONFIRMED -> CHECKED_IN -> CHECKED_OUT
# Nhánh huỷ: PENDING hoặc CONFIRMED -> CANCELLED
# ==============================================================================
class BookingStatus(Enum):
    PENDING = "PENDING"          # Vừa tạo, đang chờ xác nhận
    CONFIRMED = "CONFIRMED"      # Đã xác nhận, chờ khách đến nhận phòng
    CHECKED_IN = "CHECKED_IN"    # Khách đã nhận phòng, đang ở
    CHECKED_OUT = "CHECKED_OUT"  # Khách đã trả phòng, kết thúc
    CANCELLED = "CANCELLED"      # Booking đã bị huỷ


# ==============================================================================
# LỚP Booking
# Mỗi đối tượng Booking = 1 lượt đặt phòng, liên kết với 1 Guest và 1 Room
# thông qua guest_id và room_id (chỉ lưu mã, không lưu cả đối tượng)
# ==============================================================================
class Booking:

    # --------------------------------------------------------------------------
    # HÀM KHỞI TẠO (+__init__)
    # Chạy tự động khi tạo đối tượng: Booking("B001", "G001", "R101", ...)
    # Các tham số có "= giá trị" phía sau là tham số tuỳ chọn (có giá trị mặc định)
    # --------------------------------------------------------------------------
    def __init__(self, booking_id: str, guest_id: str, room_id: str,
                 check_in: date, check_out: date,
                 booking_date: datetime = None,
                 status: str = BookingStatus.PENDING.value,
                 total_price: float = 0.0):

        # Dấu "__" ở đầu tên = thuộc tính PRIVATE (dấu "-" trong UML)
        # Code bên ngoài không truy cập trực tiếp được, phải đi qua getter bên dưới
        self.__booking_id = booking_id      # Mã đặt phòng, ví dụ "B001"
        self.__guest_id = guest_id          # Mã khách đặt, trỏ tới Guest.guest_id
        self.__room_id = room_id            # Mã phòng được đặt, trỏ tới Room.room_id
        self.__check_in = check_in          # Ngày khách đến nhận phòng
        self.__check_out = check_out        # Ngày khách trả phòng

        # Nếu người gọi không truyền booking_date thì tự lấy thời điểm hiện tại
        # (đây là cách viết if-else gọn trên 1 dòng)
        self.__booking_date = booking_date if booking_date else datetime.now()

        # Status lưu dạng CHUỖI (ví dụ "PENDING") chứ không lưu Enum
        # vì chuỗi dễ ghi vào file JSON hơn
        self.__status = status

        # Tổng tiền ban đầu bằng 0, sẽ được tính lại khi gọi calculate_total()
        self.__total_price = total_price

    # --------------------------------------------------------------------------
    # CÁC GETTER (đọc thuộc tính private)
    # @property biến hàm thành "thuộc tính chỉ đọc":
    #   dùng:  booking.booking_id      (KHÔNG có dấu ngoặc)
    #   không phải: booking.booking_id()
    # Không viết setter => bên ngoài không thể sửa trực tiếp, chỉ đọc được
    # --------------------------------------------------------------------------
    @property
    def booking_id(self) -> str:
        return self.__booking_id        # Trả về mã đặt phòng

    @property
    def guest_id(self) -> str:
        return self.__guest_id          # Trả về mã khách

    @property
    def room_id(self) -> str:
        return self.__room_id           # Trả về mã phòng

    @property
    def check_in(self) -> date:
        return self.__check_in          # Trả về ngày nhận phòng

    @property
    def check_out(self) -> date:
        return self.__check_out         # Trả về ngày trả phòng

    @property
    def booking_date(self) -> datetime:
        return self.__booking_date      # Trả về thời điểm đặt phòng

    @property
    def status(self) -> str:
        return self.__status            # Trả về trạng thái hiện tại (dạng chuỗi)

    @property
    def total_price(self) -> float:
        return self.__total_price       # Trả về tổng tiền

    # --------------------------------------------------------------------------
    # +calculate_total(room_price) : float
    # Tính tổng tiền của booking.
    # Tham số room_price = giá thuê 1 đêm, do bên ngoài truyền vào
    # (Booking không biết giá phòng vì chỉ lưu room_id, nên phải nhận từ ngoài)
    # --------------------------------------------------------------------------
    def calculate_total(self, room_price: float) -> float:
        """Tính tổng tiền = số đêm * giá phòng 1 đêm."""
        # Trừ 2 đối tượng date cho ra kiểu timedelta, ".days" lấy số ngày
        # Ví dụ: nhận 10/12, trả 13/12 => 3 đêm
        nights = (self.__check_out - self.__check_in).days

        # Lưu kết quả vào thuộc tính để lần sau đọc lại bằng booking.total_price
        self.__total_price = nights * room_price

        # Đồng thời trả về kết quả để người gọi dùng ngay nếu cần
        return self.__total_price

    # --------------------------------------------------------------------------
    # +check_date_validity() : bool
    # Kiểm tra ngày nhận/trả có hợp lệ không.
    # Trả về True nếu hợp lệ, False nếu sai
    # --------------------------------------------------------------------------
    def check_date_validity(self) -> bool:
        """Ngày hợp lệ khi: nhận phòng không ở quá khứ và trả phòng sau nhận phòng."""
        # Điều kiện 1: ngày nhận phòng không được nhỏ hơn hôm nay
        # (date.today() = ngày hiện tại của máy tính)
        if self.__check_in < date.today():
            return False

        # Điều kiện 2: ngày trả phải SAU ngày nhận ít nhất 1 ngày
        # Dùng "<=" vì nếu trả cùng ngày nhận thì số đêm = 0, không hợp lệ
        if self.__check_out <= self.__check_in:
            return False

        # Qua hết các điều kiện => ngày hợp lệ
        return True

    # --------------------------------------------------------------------------
    # +check_overlap(bookings) : bool
    # Kiểm tra booking này có TRÙNG LỊCH với booking nào trong danh sách không.
    # Trả về True nếu bị trùng, False nếu không trùng
    # --------------------------------------------------------------------------
    def check_overlap(self, bookings: list) -> bool:
        """Trả về True nếu booking này TRÙNG lịch với booking nào đó trong danh sách."""
        # Duyệt từng booking khác trong danh sách để so sánh
        for other in bookings:

            # Bỏ qua chính nó (so sánh theo mã), tránh tự trùng với bản thân
            if other.booking_id == self.__booking_id:
                continue    # "continue" = bỏ qua lượt này, sang booking kế tiếp

            # Khác phòng thì không thể trùng lịch, bỏ qua
            if other.room_id != self.__room_id:
                continue

            # Booking đã huỷ hoặc đã trả phòng thì phòng đã được giải phóng,
            # không còn chiếm chỗ nên cũng bỏ qua
            if other.status in (BookingStatus.CANCELLED.value,
                                BookingStatus.CHECKED_OUT.value):
                continue

            # Công thức kiểm tra 2 khoảng thời gian [A_in, A_out) và [B_in, B_out)
            # có giao nhau: A_in < B_out  VÀ  A_out > B_in
            # Ví dụ: A = 10->13, B = 12->15 => 10 < 15 và 13 > 12 => TRÙNG
            # Ví dụ: A = 10->13, B = 13->15 => 13 > 13 sai => KHÔNG trùng
            #        (khách A trả phòng đúng ngày khách B nhận thì vẫn ổn)
            if self.__check_in < other.check_out and self.__check_out > other.check_in:
                return True     # Tìm thấy 1 booking trùng là kết luận luôn

        # Duyệt hết mà không thấy trùng => trả về False
        return False

    # --------------------------------------------------------------------------
    # +check_in_room() : void
    # Chuyển trạng thái sang CHECKED_IN khi khách đến nhận phòng.
    # Không trả về gì (void => None). Nếu sai trạng thái thì ném lỗi ValueError
    # --------------------------------------------------------------------------
    def check_in_room(self) -> None:
        """Nhận phòng: chỉ cho phép khi booking đang ở trạng thái CONFIRMED."""
        # Chỉ booking đã xác nhận mới được nhận phòng
        if self.__status != BookingStatus.CONFIRMED.value:
            # "raise" ném ra lỗi để BookingManager bắt bằng try/except
            raise ValueError("Chỉ booking đã xác nhận (CONFIRMED) mới được check-in.")

        # Hợp lệ => đổi trạng thái
        self.__status = BookingStatus.CHECKED_IN.value

    # --------------------------------------------------------------------------
    # +check_out_room() : void
    # Chuyển trạng thái sang CHECKED_OUT khi khách trả phòng
    # --------------------------------------------------------------------------
    def check_out_room(self) -> None:
        """Trả phòng: chỉ cho phép khi khách đang ở (CHECKED_IN)."""
        # Khách chưa nhận phòng thì không thể trả phòng
        if self.__status != BookingStatus.CHECKED_IN.value:
            raise ValueError("Chỉ booking đã check-in mới được check-out.")

        # Hợp lệ => đổi trạng thái
        self.__status = BookingStatus.CHECKED_OUT.value

    # --------------------------------------------------------------------------
    # +cancel() : void
    # Huỷ booking
    # --------------------------------------------------------------------------
    def cancel(self) -> None:
        """Huỷ đặt phòng: không huỷ được khi khách đã nhận/trả phòng hoặc đã huỷ rồi."""
        # Các trạng thái này không được phép huỷ:
        #  - CHECKED_IN  : khách đang ở trong phòng
        #  - CHECKED_OUT : khách đã trả phòng, booking đã xong
        #  - CANCELLED   : đã huỷ rồi, không huỷ lần 2
        if self.__status in (BookingStatus.CHECKED_IN.value,
                             BookingStatus.CHECKED_OUT.value,
                             BookingStatus.CANCELLED.value):
            raise ValueError("Không thể huỷ booking ở trạng thái hiện tại.")

        # Chỉ còn PENDING hoặc CONFIRMED => cho phép huỷ
        self.__status = BookingStatus.CANCELLED.value

    # --------------------------------------------------------------------------
    # confirm() : HÀM BỔ SUNG, KHÔNG CÓ TRONG UML
    # Cần có vì UML không có bước nào đưa booking từ PENDING sang CONFIRMED,
    # trong khi check_in_room() lại yêu cầu trạng thái CONFIRMED.
    # --------------------------------------------------------------------------
    def confirm(self) -> None:
        """Chuyển PENDING -> CONFIRMED để sau đó mới check-in được."""
        # Chỉ booking đang chờ (PENDING) mới được xác nhận
        if self.__status != BookingStatus.PENDING.value:
            raise ValueError("Chỉ booking PENDING mới được xác nhận.")

        self.__status = BookingStatus.CONFIRMED.value

    # --------------------------------------------------------------------------
    # +display_info() : str
    # Trả về chuỗi thông tin ĐẦY ĐỦ, nhiều dòng, dùng khi xem chi tiết 1 booking
    # Lưu ý: hàm này TRẢ VỀ chuỗi chứ không in, muốn in thì print(b.display_info())
    # --------------------------------------------------------------------------
    def display_info(self) -> str:
        """Trả về chuỗi thông tin chi tiết của booking."""
        # f-string: chèn biến vào chuỗi bằng {tên_biến}
        # "\n" xuống dòng
        # strftime('%Y-%m-%d %H:%M') định dạng datetime thành "2026-12-10 14:30"
        # {self.__total_price:,.0f} định dạng số có dấu phẩy ngăn cách hàng nghìn,
        #   không có số lẻ. Ví dụ 1500000 -> "1,500,000"
        return (f"Mã đặt phòng : {self.__booking_id}\n"
                f"Mã khách     : {self.__guest_id}\n"
                f"Mã phòng     : {self.__room_id}\n"
                f"Nhận phòng   : {self.__check_in}\n"
                f"Trả phòng    : {self.__check_out}\n"
                f"Ngày đặt     : {self.__booking_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"Trạng thái   : {self.__status}\n"
                f"Tổng tiền    : {self.__total_price:,.0f}")

    # --------------------------------------------------------------------------
    # +__str__() : str
    # Hàm đặc biệt của Python: được gọi tự động khi print(booking) hoặc str(booking)
    # Dùng chuỗi NGẮN, 1 dòng, tiện in cả danh sách booking
    # --------------------------------------------------------------------------
    def __str__(self) -> str:
        """Chuỗi ngắn gọn khi print(booking)."""
        return (f"[{self.__booking_id}] Khách {self.__guest_id} - Phòng {self.__room_id} "
                f"({self.__check_in} -> {self.__check_out}) - {self.__status}")