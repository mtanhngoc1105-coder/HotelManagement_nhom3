# Mô tả: Lớp JSONStorage chịu trách nhiệm LƯU / ĐỌC dữ liệu ra file JSON.
#        Mỗi loại dữ liệu nằm trong 1 file riêng:
#            data/rooms.json, data/guests.json, data/bookings.json
# Quan hệ UML: HotelManager chứa 1 JSONStorage (composition);
#              JSONStorage "loads and saves" Room, Guest, Booking.
# ==============================================================================

import json                          # Thư viện đọc/ghi JSON có sẵn của Python
import os                            # Thao tác thư mục, kiểm tra file tồn tại
import re                            # Biểu thức chính quy, dùng để bỏ tiền tố private
from datetime import date, datetime  # Để chuyển chuỗi ngày về lại kiểu date/datetime

# Import các lớp model để dựng lại đối tượng khi đọc file
# (nếu thư mục/tên file của nhóm khác thì sửa lại đường dẫn import cho khớp)
from models.room import Room, StandardRoom, DeluxeRoom
from models.guest import Guest
from models.booking import Booking


class JSONStorage:

    # --------------------------------------------------------------------------
    # HÀM KHỞI TẠO
    # data_directory : thư mục chứa các file JSON (mặc định là "data")
    # --------------------------------------------------------------------------
    def __init__(self, data_directory: str = "data"):
        # -str data_directory trong UML
        self.__data_directory = data_directory

        # Tạo thư mục nếu chưa có. exist_ok=True nghĩa là có rồi thì không báo lỗi
        os.makedirs(self.__data_directory, exist_ok=True)

    # --------------------------------------------------------------------------
    # HÀM PHỤ (private): ghép đường dẫn đầy đủ tới 1 file trong thư mục dữ liệu
    # Ví dụ: __path("rooms") -> "data/rooms.json"
    # --------------------------------------------------------------------------
    def __path(self, name: str) -> str:
        return os.path.join(self.__data_directory, f"{name}.json")

    # --------------------------------------------------------------------------
    # HÀM PHỤ (private): đọc 1 file JSON, trả về list các dict
    # Nếu file chưa có hoặc bị lỗi định dạng thì trả về list rỗng
    # để chương trình vẫn chạy được lần đầu tiên (chưa có dữ liệu)
    # --------------------------------------------------------------------------
    def __read_file(self, name: str) -> list:
        path = self.__path(name)
        if not os.path.exists(path):        # File chưa tồn tại
            return []
        try:
            # encoding="utf-8" để đọc đúng tiếng Việt có dấu
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)         # Chuyển nội dung JSON thành list/dict
        except (json.JSONDecodeError, OSError):
            return []                       # File hỏng hoặc không đọc được

    # --------------------------------------------------------------------------
    # HÀM PHỤ (private): ghi 1 list dict ra file JSON. True = thành công
    # --------------------------------------------------------------------------
    def __write_file(self, name: str, items: list) -> bool:
        try:
            with open(self.__path(name), "w", encoding="utf-8") as f:
                # ensure_ascii=False : giữ nguyên tiếng Việt, không biến thành \uXXXX
                # indent=4           : xuống dòng, thụt lề cho dễ đọc file
                json.dump(items, f, ensure_ascii=False, indent=4)
            return True
        except OSError:
            return False

    # --------------------------------------------------------------------------
    # HÀM PHỤ (private, static): chuyển 1 đối tượng bất kỳ thành dict
    # Cách làm: lấy toàn bộ thuộc tính của đối tượng bằng vars(obj).
    # Thuộc tính private của Python bị đổi tên, ví dụ "__room_id" của lớp Room
    # thực chất tên là "_Room__room_id", nên dùng regex bỏ tiền tố "_Room__" đi
    # để được khoá sạch là "room_id".
    # Nhờ vậy không cần ai phải viết to_dict() trong từng lớp model.
    # --------------------------------------------------------------------------
    @staticmethod
    def __to_dict(obj) -> dict:
        result = {}
        for key, value in vars(obj).items():
            clean_key = re.sub(r"^_[A-Za-z0-9]+__", "", key)   # "_Room__price" -> "price"
            # date và datetime không ghi được thẳng vào JSON => đổi thành chuỗi ISO
            # (datetime là lớp con của date nên isinstance(value, date) bao cả hai)
            if isinstance(value, date):
                value = value.isoformat()
            result[clean_key] = value
        return result

    # ==========================================================================
    # CÁC HÀM LƯU (save)
    # ==========================================================================

    # --------------------------------------------------------------------------
    # +save_rooms(rooms) : bool
    # Lưu danh sách phòng. Ghi thêm trường "room_type" (tên lớp: StandardRoom
    # hoặc DeluxeRoom) để lúc đọc biết cần dựng lại đúng loại phòng nào
    # --------------------------------------------------------------------------
    def save_rooms(self, rooms: list) -> bool:
        items = []
        for room in rooms:
            data = self.__to_dict(room)             # Đối tượng -> dict
            data["room_type"] = type(room).__name__ # Ví dụ "DeluxeRoom"
            items.append(data)
        return self.__write_file("rooms", items)

    # --------------------------------------------------------------------------
    # +save_guests(guests) : bool
    # --------------------------------------------------------------------------
    def save_guests(self, guests: list) -> bool:
        items = [self.__to_dict(g) for g in guests]
        return self.__write_file("guests", items)

    # --------------------------------------------------------------------------
    # +save_bookings(bookings) : bool
    # Với Booking dùng thẳng các getter (property) của lớp Booking cho rõ ràng
    # --------------------------------------------------------------------------
    def save_bookings(self, bookings: list) -> bool:
        items = []
        for b in bookings:
            items.append({
                "booking_id": b.booking_id,
                "guest_id": b.guest_id,
                "room_id": b.room_id,
                "check_in": b.check_in.isoformat(),          # date -> "2026-12-10"
                "check_out": b.check_out.isoformat(),
                "booking_date": b.booking_date.isoformat(),  # datetime -> chuỗi ISO
                "status": b.status,
                "total_price": b.total_price,
            })
        return self.__write_file("bookings", items)

    # --------------------------------------------------------------------------
    # +save_data(data) : bool
    # Lưu TẤT CẢ cùng lúc. data là dict dạng:
    #   {"rooms": [...], "guests": [...], "bookings": [...]}
    # Trả về True chỉ khi cả 3 lần lưu đều thành công
    # --------------------------------------------------------------------------
    def save_data(self, data: dict) -> bool:
        ok_rooms = self.save_rooms(data.get("rooms", []))
        ok_guests = self.save_guests(data.get("guests", []))
        ok_bookings = self.save_bookings(data.get("bookings", []))
        return ok_rooms and ok_guests and ok_bookings

    # ==========================================================================
    # CÁC HÀM ĐỌC (load)
    # ==========================================================================

    # --------------------------------------------------------------------------
    # +load_rooms() : list
    # Đọc file rooms.json và dựng lại thành các đối tượng Room
    # --------------------------------------------------------------------------
    def load_rooms(self) -> list:
        rooms = []
        for d in self.__read_file("rooms"):
            # Các tham số chung của mọi loại phòng (theo __init__ của Room trong UML)
            common = dict(
                room_id=d["room_id"],
                room_number=d["room_number"],
                price=d["price"],
                status=d["status"],
                description=d.get("description", ""),
                capacity=d.get("capacity", 1),
            )
            # Dựa vào room_type để tạo đúng lớp con
            room_type = d.get("room_type", "Room")
            if room_type == "StandardRoom":
                room = StandardRoom(**common,
                                    has_window=d.get("has_window", True),
                                    bed_type=d.get("bed_type", ""))
            elif room_type == "DeluxeRoom":
                room = DeluxeRoom(**common,
                                  amenities=d.get("amenities", []),
                                  has_balcony=d.get("has_balcony", False))
            else:
                room = Room(**common)       # Phòng thường (lớp cha)
            rooms.append(room)
        return rooms

    # --------------------------------------------------------------------------
    # +load_guests() : list
    # --------------------------------------------------------------------------
    def load_guests(self) -> list:
        guests = []
        for d in self.__read_file("guests"):
            guests.append(Guest(
                guest_id=d["guest_id"],
                full_name=d["full_name"],
                phone=d.get("phone", ""),
                email=d.get("email", ""),
                address=d.get("address", ""),
                identity_number=d.get("identity_number", ""),
            ))
        return guests

    # --------------------------------------------------------------------------
    # +load_bookings() : list
    # Chuỗi ngày trong file phải đổi ngược về date/datetime thì Booking mới dùng được
    # --------------------------------------------------------------------------
    def load_bookings(self) -> list:
        bookings = []
        for d in self.__read_file("bookings"):
            bookings.append(Booking(
                booking_id=d["booking_id"],
                guest_id=d["guest_id"],
                room_id=d["room_id"],
                check_in=date.fromisoformat(d["check_in"]),          # chuỗi -> date
                check_out=date.fromisoformat(d["check_out"]),
                booking_date=datetime.fromisoformat(d["booking_date"]),  # chuỗi -> datetime
                status=d["status"],
                total_price=d["total_price"],
            ))
        return bookings

    # --------------------------------------------------------------------------
    # +load_data() : dict
    # Đọc TẤT CẢ cùng lúc, trả về dict cùng định dạng với save_data()
    # HotelManager.load_system_data() sẽ gọi hàm này khi khởi động chương trình
    # --------------------------------------------------------------------------
    def load_data(self) -> dict:
        return {
            "rooms": self.load_rooms(),
            "guests": self.load_guests(),
            "bookings": self.load_bookings(),
        }