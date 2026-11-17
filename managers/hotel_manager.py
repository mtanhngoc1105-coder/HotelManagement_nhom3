# Thành viên 5 - phụ trách nhánh feature/hotel-manager

from datetime import date, datetime

from models.booking import Booking
from utils.validators import (
    get_date_input,
    get_email_input,
    get_int_input,
    get_non_empty_input,
    get_phone_input,
    get_positive_float,
    get_yes_no_input,
)

from managers.booking_manager import BookingManager

try:
    from managers.room_manager import RoomManager
except (ImportError, AttributeError):
    RoomManager = None

try:
    from managers.guest_manager import GuestManager
except (ImportError, AttributeError):
    GuestManager = None

try:
    from utils.storage import JSONStorage
except (ImportError, AttributeError):
    JSONStorage = None

try:
    from reports.report import ReportService
except (ImportError, AttributeError):
    ReportService = None

try:
    from models.room import DeluxeRoom, Room, StandardRoom
except (ImportError, AttributeError):
    Room = None
    StandardRoom = None
    DeluxeRoom = None

try:
    from models.guest import Guest
except (ImportError, AttributeError):
    Guest = None

ROOM_STATUSES = ("AVAILABLE", "BOOKED", "OCCUPIED", "MAINTENANCE")


class HotelManager:
    """Facade điều phối trung tâm: kết nối các Manager, JSONStorage và
    ReportService; nạp/lưu dữ liệu toàn hệ thống; điều phối tìm kiếm,
    sắp xếp và tạo booking thông qua API công khai của các thành phần."""

    def __init__(self, data_directory: str = "data"):
        self.__initialization_notes: list = []

        self.__room_manager = self.__create_component(
            RoomManager, "RoomManager", "managers/room_manager.py"
        )
        self.__guest_manager = self.__create_component(
            GuestManager, "GuestManager", "managers/guest_manager.py"
        )

        self.__booking_manager = BookingManager()

        self.__storage = None
        if JSONStorage is None:
            self.__initialization_notes.append(
                "JSONStorage chưa import được: utils/storage.py phụ thuộc "
                "models/room.py và models/guest.py hiện còn trống."
            )
        else:
            try:
                self.__storage = JSONStorage(data_directory)
            except OSError as error:
                self.__initialization_notes.append(
                    f"Không tạo được thư mục dữ liệu cho JSONStorage: {error}"
                )

        self.__report_service = None
        if ReportService is None:
            self.__initialization_notes.append(
                "ReportService chưa sẵn sàng: reports/report.py còn trống."
            )
        else:
            try:
                self.__report_service = ReportService(
                    self.__booking_manager, self.__room_manager
                )
            except Exception as error:  # noqa: BLE001
                self.__initialization_notes.append(
                    f"Không khởi tạo được ReportService (cần thống nhất chữ ký "
                    f"constructor với thành viên phụ trách): {error}"
                )

        self.load_system_data()

    def __create_component(self, component_class, class_name: str, file_path: str):
        if component_class is None:
            self.__initialization_notes.append(
                f"{class_name} chưa sẵn sàng: {file_path} chưa được thành viên "
                f"phụ trách hoàn thiện."
            )
            return None
        try:
            return component_class()
        except Exception as error:  # noqa: BLE001
            self.__initialization_notes.append(
                f"Không khởi tạo được {class_name} ({file_path}): {error}"
            )
            return None

    def __notify_waiting(self, component_name: str, file_path: str) -> None:
        print(f"[Thông báo] {component_name} chưa sẵn sàng ({file_path}).")
        print("Chức năng này đang chờ thành viên phụ trách hoàn thiện module.")

    def __require(self, component, component_name: str, file_path: str) -> bool:
        if component is None:
            self.__notify_waiting(component_name, file_path)
            return False
        return True

    def get_initialization_notes(self) -> list:
        """Danh sách các thành phần chưa sẵn sàng và lý do cụ thể."""
        return list(self.__initialization_notes)

    def load_system_data(self) -> None:
        """Nạp dữ liệu phòng, khách hàng, đặt phòng từ JSONStorage vào các Manager."""
        if self.__storage is None:
            print(
                "[Thông báo] Chưa thể nạp dữ liệu hệ thống: JSONStorage chưa sẵn sàng."
            )
            print(
                "Đang chờ bàn giao models/room.py và models/guest.py để "
                "utils/storage.py import được."
            )
            return

        try:
            data = self.__storage.load_data()
        except (KeyError, ValueError, TypeError, OSError) as error:
            print(f"[Lỗi] Dữ liệu JSON không hợp lệ, không thể nạp: {error}")
            return

        self.__hand_over_items(
            self.__room_manager,
            data.get("rooms", []),
            "add_room",
            "RoomManager",
            "managers/room_manager.py",
            "phòng",
        )
        self.__hand_over_items(
            self.__guest_manager,
            data.get("guests", []),
            "add_guest",
            "GuestManager",
            "managers/guest_manager.py",
            "khách hàng",
        )

        bookings = data.get("bookings", [])
        self.__booking_manager.bookings = bookings
        print(f"[Nạp dữ liệu] Đã nạp {len(bookings)} booking vào BookingManager.")

    def __hand_over_items(
        self,
        manager,
        items: list,
        add_method_name: str,
        component_name: str,
        file_path: str,
        label: str,
    ) -> None:
        if not items:
            return
        if manager is None:
            print(
                f"[Thông báo] Đã đọc {len(items)} {label} từ JSON nhưng chưa thể "
                f"chuyển giao: {component_name} chưa sẵn sàng ({file_path})."
            )
            return
        add_method = getattr(manager, add_method_name, None)
        if not callable(add_method):
            print(
                f"[Thông báo] {component_name} chưa có phương thức "
                f"{add_method_name}() công khai; cần thống nhất với thành viên phụ trách."
            )
            return
        accepted = 0
        for item in items:
            try:
                if add_method(item):
                    accepted += 1
            except Exception as error:  # noqa: BLE001
                print(
                    f"[Lỗi] {component_name}.{add_method_name}() từ chối một phần tử: {error}"
                )
        print(
            f"[Nạp dữ liệu] Đã chuyển {accepted}/{len(items)} {label} vào {component_name}."
        )

    def save_system_data(self) -> None:
        """Lưu dữ liệu phòng, khách hàng, đặt phòng xuống các tệp JSON."""
        if self.__storage is None:
            self.__notify_waiting("JSONStorage", "utils/storage.py")
            return

        results = {}

        rooms = (
            getattr(self.__room_manager, "rooms", None) if self.__room_manager else None
        )
        if isinstance(rooms, list):
            results["phòng"] = self.__storage.save_rooms(rooms)
        else:
            print(
                "[Thông báo] Bỏ qua lưu phòng: chưa lấy được danh sách qua API "
                "công khai của RoomManager (cần thống nhất getter `rooms`)."
            )

        guests = (
            getattr(self.__guest_manager, "guests", None)
            if self.__guest_manager
            else None
        )
        if isinstance(guests, list):
            results["khách hàng"] = self.__storage.save_guests(guests)
        else:
            print(
                "[Thông báo] Bỏ qua lưu khách hàng: chưa lấy được danh sách qua "
                "API công khai của GuestManager (cần thống nhất getter `guests`)."
            )

        results["đặt phòng"] = self.__storage.save_bookings(
            self.__booking_manager.bookings
        )

        for label, ok in results.items():
            if ok:
                print(f"[Lưu dữ liệu] Đã lưu danh sách {label} thành công.")
            else:
                print(
                    f"[Lỗi] Lưu danh sách {label} thất bại (JSONStorage trả về False)."
                )

    def manage_rooms(self):
        """Trả về RoomManager (None nếu module chưa được bàn giao)."""
        return self.__room_manager

    def manage_guests(self):
        """Trả về GuestManager (None nếu module chưa được bàn giao)."""
        return self.__guest_manager

    def manage_bookings(self) -> BookingManager:
        """Trả về BookingManager đang được quản lý."""
        return self.__booking_manager

    def create_booking(self, booking: Booking = None) -> bool:
        """Tạo booking thông qua BookingManager. True nếu thành công."""
        interactive = booking is None
        if interactive:
            if not self.__require(
                self.__booking_manager, "BookingManager", "managers/booking_manager.py"
            ):
                return False
            booking = self.__prompt_booking()
            if booking is None:
                return False

        if not isinstance(booking, Booking):
            print("[Lỗi] Tham số truyền vào phải là một đối tượng Booking.")
            return False
        if not self.__require(
            self.__booking_manager, "BookingManager", "managers/booking_manager.py"
        ):
            return False

        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ) or not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return False

        room = self.__room_manager.find_room(booking.room_id)
        if room is None:
            print(f"[Lỗi] Không tìm thấy phòng {booking.room_id}.")
            return False
        if self.__guest_manager.find_guest(booking.guest_id) is None:
            print(f"[Lỗi] Không tìm thấy khách hàng {booking.guest_id}.")
            return False
        if room.status.value == "MAINTENANCE":
            print(f"[Lỗi] Phòng {booking.room_id} đang bảo trì.")
            return False
        if not booking.check_date_validity():
            print("[Lỗi] Ngày nhận/trả phòng không hợp lệ.")
            return False

        nights = (booking.check_out - booking.check_in).days
        calculate_price = getattr(room, "calculate_price", None)
        total_price = (
            calculate_price(nights)
            if callable(calculate_price)
            else room.get_price() * nights
        )
        booking.calculate_total(total_price / nights)
        ok = self.__booking_manager.create_booking(booking)

        if interactive:
            if ok:
                print(f"Đã tạo booking {booking.booking_id} thành công.")

                if get_yes_no_input(
                    "Xác nhận booking ngay để có thể nhận phòng? (y/n): "
                ):
                    try:
                        booking.confirm()
                        print("Booking đã chuyển sang trạng thái CONFIRMED.")
                    except ValueError as error:
                        print(f"[Lỗi] Không thể xác nhận booking: {error}")
            else:
                print(
                    "Tạo booking thất bại (trùng mã, ngày không hợp lệ hoặc trùng lịch)."
                )
        return ok

    def __prompt_booking(self):
        booking_id = get_non_empty_input("Mã đặt phòng: ")
        guest_id = get_non_empty_input("Mã khách hàng: ")
        room_id = get_non_empty_input("Mã phòng: ")
        check_in = self.__prompt_date("Ngày nhận phòng (dd/mm/yyyy): ")
        check_out = self.__prompt_date("Ngày trả phòng (dd/mm/yyyy): ")
        return Booking(booking_id, guest_id, room_id, check_in, check_out)

    def __prompt_date(self, prompt: str) -> date:
        text = get_date_input(prompt, "%d/%m/%Y")
        return datetime.strptime(text, "%d/%m/%Y").date()

    def search_all(self, keyword: str) -> list:
        """Tìm kiếm đồng thời trên phòng, khách hàng và đặt phòng."""

        if keyword is None or not str(keyword).strip():
            return []
        keyword = str(keyword).strip()

        results = []

        sources = (
            (self.__room_manager, "search_room"),
            (self.__guest_manager, "search_guest"),
            (self.__booking_manager, "search_booking"),
        )
        for manager, method_name in sources:
            if manager is None:
                continue
            search_method = getattr(manager, method_name, None)
            if callable(search_method):
                results.extend(search_method(keyword))
        return results

    def sort_all(self, criteria: str, reverse: bool = False) -> list:
        """Sắp xếp qua RoomManager.sort_rooms(); trả về danh sách kết quả."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return []
        sort_method = getattr(self.__room_manager, "sort_rooms", None)
        if not callable(sort_method):
            print(
                "[Thông báo] RoomManager chưa có sort_rooms() công khai; "
                "cần thống nhất với thành viên phụ trách."
            )
            return []
        try:
            return sort_method(criteria, reverse)
        except (ValueError, KeyError) as error:
            print(
                f"[Thông báo] Tiêu chí sắp xếp '{criteria}' không được hỗ trợ: {error}"
            )
            return []

    def get_report(self):
        """Trả về ReportService (None nếu module chưa được bàn giao)."""
        return self.__report_service

    def add_room(self) -> None:
        """Hỏi thông tin phòng từ bàn phím rồi chuyển cho RoomManager.add_room()."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return
        if not self.__require(Room, "Room", "models/room.py"):
            return
        room = self.__prompt_room()
        if room is None:
            return
        if self.__room_manager.add_room(room):
            print("Đã thêm phòng thành công.")
        else:
            print("Thêm phòng thất bại (RoomManager từ chối, có thể trùng mã).")

    def __prompt_room(self):
        """Thu thập thông tin phòng và dựng đúng lớp con theo lựa chọn."""
        print("Loại phòng: 1. StandardRoom  2. DeluxeRoom  3. Room (cơ bản)")
        choice = get_int_input("Chọn loại phòng (1-3): ", 1, 3)

        common = {
            "room_id": get_non_empty_input("Mã phòng: "),
            "room_number": get_non_empty_input("Số phòng: "),
            "price": get_positive_float("Giá thuê 1 đêm: "),
            "status": self.__prompt_room_status(),
            "description": input("Mô tả (có thể để trống): ").strip(),
            "capacity": get_int_input("Sức chứa (người): ", 1),
        }
        if choice == 1:
            if not self.__require(StandardRoom, "StandardRoom", "models/room.py"):
                return None
            return StandardRoom(
                **common,
                has_window=get_yes_no_input("Có cửa sổ? (y/n): "),
                bed_type=get_non_empty_input("Loại giường: "),
            )
        if choice == 2:
            if not self.__require(DeluxeRoom, "DeluxeRoom", "models/room.py"):
                return None
            raw = input("Tiện nghi (phân cách bằng dấu phẩy): ").strip()
            amenities = [a.strip() for a in raw.split(",") if a.strip()]
            return DeluxeRoom(
                **common,
                amenities=amenities,
                has_balcony=get_yes_no_input("Có ban công? (y/n): "),
            )
        return Room(**common)

    def __prompt_room_status(self) -> str:
        """Nhập trạng thái phòng, mặc định AVAILABLE cho phòng mới."""
        while True:
            raw = (
                input(
                    "Trạng thái (AVAILABLE/BOOKED/OCCUPIED/MAINTENANCE, "
                    "Enter = AVAILABLE): "
                )
                .strip()
                .upper()
            )
            if raw == "":
                return "AVAILABLE"
            if raw in ROOM_STATUSES:
                return raw
            print("Trạng thái không hợp lệ, vui lòng nhập lại.")

    def update_room(self, room_id: str = None, data: dict = None) -> bool:
        """Cập nhật phòng qua RoomManager, nhận dữ liệu hoặc hỏi trên Console."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return False
        if room_id is None:
            room_id = get_non_empty_input("Mã phòng cần cập nhật: ")

        if data is None:
            room = self.__room_manager.find_room(room_id)
            if room is None:
                print(f"Không tìm thấy phòng {room_id}.")
                return False

            data = {}
            fields = (
                ("room_number", "Số phòng mới"),
                ("price", "Giá thuê mỗi đêm"),
                ("status", "Trạng thái mới"),
                ("description", "Mô tả mới"),
                ("capacity", "Sức chứa mới"),
            )
            for field, label in fields:
                value = input(f"{label} (Enter để giữ nguyên): ").strip()
                if not value:
                    continue
                try:
                    if field == "price":
                        value = float(value.replace(",", "."))
                    elif field == "capacity":
                        value = int(value)
                    elif field == "status":
                        value = value.upper()
                except ValueError:
                    print(f"[Lỗi] Giá trị {label.lower()} không hợp lệ.")
                    return False
                data[field] = value
            if not data:
                print("Không có thông tin nào được thay đổi.")
                return False

        if self.__room_manager.update_room(room_id, data):
            print("Cập nhật phòng thành công.")
            return True
        else:
            print("Cập nhật phòng thất bại (không tìm thấy mã hoặc bị từ chối).")
            return False

    def delete_room(self) -> None:
        """Hỏi mã phòng rồi chuyển cho RoomManager.delete_room(room_id)."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return
        room_id = get_non_empty_input("Mã phòng cần xóa: ")
        if self.__room_manager.delete_room(room_id):
            print("Xóa phòng thành công.")
        else:
            print("Xóa phòng thất bại (không tìm thấy mã hoặc bị từ chối).")

    def show_rooms(self) -> None:
        """Chuyển tiếp tới RoomManager.display_rooms()."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return
        self.__room_manager.display_rooms()

    def find_room(self) -> None:
        """Tìm và hiển thị phòng khớp từ khóa."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return
        keyword = get_non_empty_input("Từ khóa cần tìm phòng: ")
        rooms = self.__room_manager.search_room(keyword)
        if not rooms:
            print(f"Không tìm thấy phòng khớp với '{keyword}'.")
            return
        for room in rooms:
            print(room.display_info())

    def sort_rooms(self) -> None:
        """Hỏi tiêu chí và chiều sắp xếp rồi điều phối qua sort_all()."""
        if not self.__require(
            self.__room_manager, "RoomManager", "managers/room_manager.py"
        ):
            return
        criteria = get_non_empty_input(
            "Tiêu chí sắp xếp (theo quy ước của RoomManager): "
        )
        reverse = get_yes_no_input("Sắp xếp giảm dần? (y/n): ")
        results = self.sort_all(criteria, reverse)
        if not results:
            print("Không có kết quả để hiển thị.")
            return
        for room in results:
            print(room)

    def add_guest(self) -> None:
        """Hỏi thông tin khách rồi chuyển cho GuestManager.add_guest()."""
        if not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return
        if not self.__require(Guest, "Guest", "models/guest.py"):
            return

        guest = Guest(
            guest_id=get_non_empty_input("Mã khách hàng: "),
            full_name=get_non_empty_input("Họ và tên: "),
            phone=get_phone_input("Số điện thoại: "),
            email=get_email_input("Email: "),
            address=get_non_empty_input("Địa chỉ: "),
            identity_number=get_non_empty_input("Số CCCD/CMND: "),
        )
        if self.__guest_manager.add_guest(guest):
            print("Đã thêm khách hàng thành công.")
        else:
            print("Thêm khách hàng thất bại (GuestManager từ chối, có thể trùng mã).")

    def update_guest(self) -> None:
        """Hỏi mã khách rồi chuyển cho GuestManager.update_guest(guest_id)."""
        if not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return
        guest_id = get_non_empty_input("Mã khách hàng cần cập nhật: ")
        if self.__guest_manager.update_guest(guest_id):
            print("Cập nhật khách hàng thành công.")
        else:
            print("Cập nhật khách hàng thất bại (không tìm thấy mã hoặc bị từ chối).")

    def delete_guest(self) -> None:
        """Hỏi mã khách rồi chuyển cho GuestManager.delete_guest(guest_id)."""
        if not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return
        guest_id = get_non_empty_input("Mã khách hàng cần xóa: ")
        if self.__guest_manager.delete_guest(guest_id):
            print("Xóa khách hàng thành công.")
        else:
            print("Xóa khách hàng thất bại (không tìm thấy mã hoặc bị từ chối).")

    def show_guests(self) -> None:
        """Chuyển tiếp tới GuestManager.display_guests()."""
        if not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return
        self.__guest_manager.display_guests()

    def find_guest(self) -> None:
        """Tìm và hiển thị khách hàng khớp từ khóa."""
        if not self.__require(
            self.__guest_manager, "GuestManager", "managers/guest_manager.py"
        ):
            return
        keyword = get_non_empty_input("Từ khóa cần tìm khách hàng: ")
        guests = self.__guest_manager.search_guest(keyword)
        if not guests:
            print(f"Không tìm thấy khách hàng khớp với '{keyword}'.")
            return
        for guest in guests:
            print(guest.display_info())

    def cancel_booking(self, booking_id: str | None = None) -> None:
        """Hủy booking qua BookingManager.cancel_booking()."""
        if not self.__require(
            self.__booking_manager, "BookingManager", "managers/booking_manager.py"
        ):
            return
        if booking_id is None:
            booking_id = get_non_empty_input("Mã booking cần hủy: ")
        if self.__booking_manager.cancel_booking(booking_id):
            print("Hủy booking thành công.")
        else:
            print(
                "Hủy booking thất bại (không tìm thấy mã hoặc trạng thái không cho phép)."
            )

    def check_in(self, booking_id: str | None = None) -> None:
        """Nhận phòng qua BookingManager.check_in()."""
        if not self.__require(
            self.__booking_manager, "BookingManager", "managers/booking_manager.py"
        ):
            return
        if booking_id is None:
            booking_id = get_non_empty_input("Mã booking cần nhận phòng: ")
        if self.__booking_manager.check_in(booking_id):
            booking = self.__booking_manager.find_booking(booking_id)
            room = (
                self.__room_manager.find_room(booking.room_id)
                if self.__room_manager
                else None
            )
            if room is not None:
                room.set_status("OCCUPIED")
            print("Nhận phòng thành công.")
        else:
            print("Nhận phòng thất bại (booking phải ở trạng thái CONFIRMED).")

    def check_out(self, booking_id: str | None = None) -> None:
        """Trả phòng qua BookingManager.check_out()."""
        if not self.__require(
            self.__booking_manager, "BookingManager", "managers/booking_manager.py"
        ):
            return
        if booking_id is None:
            booking_id = get_non_empty_input("Mã booking cần trả phòng: ")
        if self.__booking_manager.check_out(booking_id):
            booking = self.__booking_manager.find_booking(booking_id)
            room = (
                self.__room_manager.find_room(booking.room_id)
                if self.__room_manager
                else None
            )
            if room is not None and room.status.value == "OCCUPIED":
                room.set_status("AVAILABLE")
            print("Trả phòng thành công.")
        else:
            print("Trả phòng thất bại (booking phải ở trạng thái CHECKED_IN).")

    def show_bookings(self) -> None:
        """Chuyển tiếp tới BookingManager.display_bookings()."""
        if not self.__require(
            self.__booking_manager, "BookingManager", "managers/booking_manager.py"
        ):
            return
        self.__booking_manager.display_bookings()

    def show_revenue(self) -> None:
        """Chuyển tiếp tới ReportService.display_revenue_report()."""
        if not self.__require(
            self.__report_service, "ReportService", "reports/report.py"
        ):
            return
        self.__report_service.display_revenue_report()

    def show_room_occupancy(self) -> None:
        """Chuyển tiếp tới ReportService.display_occupancy_report()."""
        if not self.__require(
            self.__report_service, "ReportService", "reports/report.py"
        ):
            return
        self.__report_service.display_occupancy_report()

    def show_daily_bookings(self) -> None:
        """Thống kê booking đang chiếm phòng trong một ngày nhập từ bàn phím."""
        target_date = self.__prompt_date("Ngày cần thống kê (dd/mm/yyyy): ")
        if self.__report_service is not None:
            bookings = self.__report_service.get_bookings_by_date(target_date)
        else:
            print(
                "[Ghi chú] ReportService chưa sẵn sàng; tạm dùng "
                "BookingManager.get_bookings_by_date()."
            )
            bookings = self.__booking_manager.get_bookings_by_date(target_date)
        if not bookings:
            print("Không có booking nào đang chiếm phòng trong ngày này.")
            return
        for booking in bookings:
            print(booking)
