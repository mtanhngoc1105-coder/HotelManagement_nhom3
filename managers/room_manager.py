
"""
Module quản lý danh sách phòng của khách sạn.

RoomManager chịu trách nhiệm quản lý các đối tượng phòng trong bộ nhớ,
bao gồm các chức năng:
- Thêm phòng mới vào danh sách.
- Cập nhật thông tin phòng.
- Xóa phòng khỏi danh sách.
- Tìm phòng theo mã phòng.
- Tìm kiếm phòng theo từ khóa hoặc khoảng giá.
- Sắp xếp phòng theo nhiều tiêu chí.
- Hiển thị danh sách phòng.

Lưu ý:
RoomManager chỉ quản lý danh sách phòng trong bộ nhớ.
Việc đọc và ghi dữ liệu JSON thuộc trách nhiệm của module Storage,
không thực hiện trong file này.
"""

# re: Hỗ trợ biểu thức chính quy để nhận diện cú pháp tìm kiếm theo khoảng giá.
import re

# sys: Lấy thông tin mã hóa đầu ra của cửa sổ Console.
# Module này được sử dụng để xử lý trường hợp Console Windows
# không hỗ trợ hiển thị đầy đủ một số ký tự Unicode.
import sys

# Mapping: Kiểu dữ liệu đại diện cho các cấu trúc ánh xạ dạng key-value,
# ví dụ như dictionary dùng để truyền thông tin cần cập nhật.
from collections.abc import Mapping

# Any: Cho phép khai báo kiểu dữ liệu tổng quát khi chưa xác định
# chính xác kiểu của giá trị được truyền vào.
from typing import Any

# Import lớp Room làm kiểu dữ liệu cơ sở cho danh sách phòng.
# StandardRoom và DeluxeRoom đều kế thừa Room nên cũng có thể
# được thêm vào và quản lý thông qua RoomManager.
from models.room import Room


# Biểu thức chính quy dùng để nhận diện khoảng giá do người dùng nhập.
#
# Các định dạng được hỗ trợ:
#   100-500
#   100..500
#   100:500
#
# Trong đó:
#   \d+             : Một hoặc nhiều chữ số.
#   (?:\.\d+)?      : Phần thập phân không bắt buộc.
#   \s*             : Cho phép có khoảng trắng ở hai bên.
#   -|\.{2}|:       : Dấu phân cách giữa giá nhỏ nhất và lớn nhất.
#
# Ví dụ: "100 - 500" sẽ được hiểu là tìm phòng có giá
# nằm trong khoảng từ 100 đến 500.
_PRICE_RANGE_PATTERN = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*(?:-|\.{2}|:)\s*(\d+(?:\.\d+)?)\s*$"
)


class RoomManager:
    """
    Lớp quản lý danh sách phòng khách sạn.

    Thuộc tính:
        rooms: Danh sách chứa các đối tượng phòng thuộc lớp Room
               hoặc các lớp con như StandardRoom và DeluxeRoom.

    Các phương thức của lớp thực hiện những thao tác quản lý phòng
    mà không trực tiếp phụ thuộc vào giao diện nhập liệu Console
    hoặc chức năng lưu trữ dữ liệu JSON.
    """

    def __init__(self) -> None:
        """
        Khởi tạo đối tượng RoomManager.

        Tạo một danh sách rỗng để lưu trữ các phòng trong bộ nhớ.
        Khi bắt đầu chương trình, danh sách này có thể được bổ sung
        dữ liệu từ module Storage thông qua lớp quản lý hệ thống.
        """
        self.rooms: list[Room] = []

    def add_room(self, room: Room) -> bool:
        """
        Thêm một phòng mới vào danh sách quản lý.

        Tham số:
            room: Đối tượng phòng cần thêm.
                  Có thể là Room, StandardRoom hoặc DeluxeRoom.

        Kết quả:
            True: Thêm phòng thành công.
            False: Không thêm được phòng do dữ liệu không hợp lệ
                   hoặc bị trùng mã phòng/số phòng.

        Quy tắc:
            - Đối tượng truyền vào phải thuộc lớp Room hoặc lớp con.
            - Mã phòng (room_id) không được trùng.
            - Số phòng (room_number) không được trùng.
        """

        # Kiểm tra đối tượng được truyền vào có phải là Room
        # hoặc một lớp kế thừa từ Room hay không.
        if not isinstance(room, Room):
            return False

        # Kiểm tra toàn bộ danh sách để phát hiện trùng mã phòng
        # hoặc trùng số phòng với một phòng đã tồn tại.
        if any(
            existing.room_id == room.room_id
            or existing.room_number == room.room_number
            for existing in self.rooms
        ):
            return False

        # Nếu dữ liệu hợp lệ và không bị trùng,
        # thêm đối tượng phòng vào cuối danh sách.
        self.rooms.append(room)

        return True

    def update_room(
        self,
        room_id: str,
        data: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> bool:
        """
        Cập nhật thông tin của một phòng đã tồn tại.

        Tham số:
            room_id: Mã phòng cần cập nhật.
            data: Dictionary hoặc Mapping chứa các trường cần thay đổi.
            **kwargs: Cho phép truyền trực tiếp các trường cần cập nhật
                      dưới dạng tham số có tên.

        Ví dụ:
            update_room("P101", {"price": 500000})

            update_room("P101", price=500000, capacity=3)

        Kết quả:
            True: Cập nhật thành công.
            False: Không tìm thấy phòng, dữ liệu không hợp lệ,
                   không có thông tin cập nhật hoặc bị trùng dữ liệu.

        Lưu ý:
            Việc kiểm tra kiểu dữ liệu và giá trị hợp lệ của từng thuộc tính
            được thực hiện thông qua phương thức update_info() của lớp Room.
        """

        # Tìm phòng cần cập nhật dựa trên mã phòng.
        room = self.find_room(room_id)

        # Không cập nhật nếu:
        # - Không tìm thấy phòng.
        # - Người gọi không cung cấp bất kỳ thông tin mới nào.
        if room is None or (data is None and not kwargs):
            return False

        # Nếu data được truyền vào thì phải là một Mapping,
        # thông thường là dictionary.
        if data is not None and not isinstance(data, Mapping):
            return False

        # Tạo bản sao dữ liệu cập nhật để tránh thay đổi trực tiếp
        # dữ liệu Mapping ban đầu của bên gọi.
        updates = dict(data or {})

        # Kết hợp các trường được truyền bằng kwargs.
        # Nếu cùng một trường xuất hiện ở cả hai nơi,
        # giá trị trong kwargs sẽ được ưu tiên.
        updates.update(kwargs)

        # Lấy mã phòng mới nếu có yêu cầu thay đổi,
        # nếu không thì giữ nguyên mã phòng hiện tại.
        new_room_id = updates.get("room_id", room.room_id)

        # Lấy số phòng mới nếu có yêu cầu thay đổi,
        # nếu không thì giữ nguyên số phòng hiện tại.
        new_room_number = updates.get("room_number", room.room_number)

        # Loại bỏ khoảng trắng thừa ở đầu và cuối
        # đối với mã phòng và số phòng dạng chuỗi.
        if isinstance(new_room_id, str):
            new_room_id = new_room_id.strip()

        if isinstance(new_room_number, str):
            new_room_number = new_room_number.strip()

        # Kiểm tra mã phòng và số phòng mới có bị trùng
        # với một phòng khác trong danh sách hay không.
        #
        # Điều kiện existing is not room giúp bỏ qua chính phòng
        # đang được cập nhật, tránh trường hợp phòng bị so sánh với nó.
        if any(
            existing is not room
            and (
                existing.room_id == new_room_id
                or existing.room_number == new_room_number
            )
            for existing in self.rooms
        ):
            return False

        try:
            # Gọi phương thức update_info() của đối tượng Room
            # để kiểm tra và cập nhật các thuộc tính.
            #
            # Phương thức này hỗ trợ cập nhật thông tin chung
            # và cả thuộc tính riêng của StandardRoom/DeluxeRoom.
            #
            # Nếu dữ liệu không hợp lệ, update_info() sẽ phát sinh
            # TypeError hoặc ValueError.
            room.update_info(updates)

        except (TypeError, ValueError):
            # Nếu xảy ra lỗi kiểm tra dữ liệu,
            # không tiếp tục cập nhật và trả về False.
            return False

        # Tất cả thông tin đã được cập nhật thành công.
        return True

    def delete_room(self, room_id: str) -> bool:
        """
        Xóa một phòng khỏi danh sách quản lý.

        Tham số:
            room_id: Mã của phòng cần xóa.

        Kết quả:
            True: Xóa thành công.
            False: Không tìm thấy phòng cần xóa.

        Lưu ý:
            Việc kiểm tra phòng có đang được đặt hay không
            và có được phép xóa hay không cần được phối hợp
            với BookingManager hoặc HotelManager.
        """

        # Tìm phòng cần xóa theo mã phòng.
        room = self.find_room(room_id)

        # Nếu không tồn tại phòng có mã tương ứng,
        # không thực hiện thao tác xóa.
        if room is None:
            return False

        # Xóa đối tượng phòng khỏi danh sách quản lý.
        self.rooms.remove(room)

        return True

    def find_room(self, room_id: str) -> Room | None:
        """
        Tìm một phòng theo mã phòng chính xác.

        Tham số:
            room_id: Mã phòng cần tìm.

        Kết quả:
            Trả về đối tượng Room nếu tìm thấy.
            Trả về None nếu không có phòng tương ứng.

        Phương thức này thường được sử dụng trong:
            - Cập nhật thông tin phòng.
            - Xóa phòng.
            - Kiểm tra phòng có tồn tại hay không.
            - Các nghiệp vụ khác cần lấy thông tin một phòng cụ thể.
        """

        # Duyệt lần lượt từng phòng trong danh sách.
        for room in self.rooms:

            # So sánh mã phòng của từng đối tượng
            # với mã phòng được truyền vào.
            if room.room_id == room_id:
                return room

        # Duyệt hết danh sách nhưng không tìm thấy.
        return None

    def search_room(self, keyword: str) -> list[Room]:
        """
        Tìm kiếm phòng theo từ khóa hoặc khoảng giá.

        Tham số:
            keyword: Nội dung người dùng muốn tìm kiếm.

        Các trường có thể tìm kiếm:
            - Mã phòng.
            - Số phòng.
            - Loại phòng.
            - Trạng thái phòng.
            - Giá phòng.
            - Mô tả phòng.

        Ngoài ra, hỗ trợ tìm kiếm theo khoảng giá:
            "100-500"
            "100..500"
            "100:500"

        Kết quả:
            Trả về danh sách các phòng phù hợp.
            Nếu không có kết quả hoặc từ khóa không hợp lệ,
            trả về danh sách rỗng.

        Lưu ý:
            Tìm kiếm văn bản không phân biệt chữ hoa và chữ thường.
        """

        # Kiểm tra từ khóa phải là chuỗi và không được để trống.
        if not isinstance(keyword, str) or not keyword.strip():
            return []

        # Chuẩn hóa từ khóa:
        # - Loại bỏ khoảng trắng thừa.
        # - Chuyển về dạng chữ thường không phụ thuộc ngôn ngữ.
        query = keyword.strip().casefold()

        # Kiểm tra xem từ khóa có phải là khoảng giá hay không.
        price_range = _PRICE_RANGE_PATTERN.fullmatch(keyword)

        if price_range is not None:

            # Chuyển hai giá trị trong khoảng giá thành số thực.
            minimum, maximum = map(float, price_range.groups())

            # Nếu giá nhỏ nhất lớn hơn giá lớn nhất,
            # khoảng tìm kiếm không hợp lệ.
            if minimum > maximum:
                return []

            # Lọc các phòng có đơn giá nằm trong khoảng đã nhập.
            # Kết quả bao gồm cả hai giới hạn minimum và maximum.
            return [
                room
                for room in self.rooms
                if minimum <= room.price <= maximum
            ]

        # Tạo danh sách chứa các phòng tìm thấy.
        matches = []

        # Duyệt toàn bộ phòng để kiểm tra từ khóa.
        for room in self.rooms:

            # Xây dựng danh sách các thông tin có thể tìm kiếm
            # của từng phòng.
            #
            # type(room).__name__ cho phép tìm theo tên lớp,
            # ví dụ: StandardRoom hoặc DeluxeRoom.
            #
            # room.status.value lấy giá trị chuỗi của Enum trạng thái.
            searchable_values = (
                room.room_id,
                room.room_number,
                type(room).__name__,
                room.status.value,
                str(room.price),
                f"{room.price:g}",
                room.description,
            )

            # Nếu từ khóa xuất hiện trong ít nhất một trường
            # thông tin của phòng thì thêm phòng vào kết quả.
            if any(query in value.casefold() for value in searchable_values):
                matches.append(room)

        # Trả về danh sách các phòng phù hợp với từ khóa.
        return matches

    def sort_rooms(self, criteria: str, reverse: bool = False) -> list[Room]:
        """
        Sắp xếp danh sách phòng theo tiêu chí được lựa chọn.

        Tham số:
            criteria: Tiêu chí sắp xếp.
            reverse:
                False: Sắp xếp tăng dần.
                True: Sắp xếp giảm dần.

        Các tiêu chí được hỗ trợ:
            - price: Giá phòng.
            - room_number: Số phòng.
            - room_id: Mã phòng.
            - capacity: Sức chứa.
            - status: Trạng thái phòng.

        Kết quả:
            Trả về một danh sách phòng mới đã được sắp xếp.
            Nếu tiêu chí không hợp lệ, trả về danh sách rỗng.

        Lưu ý:
            Hàm sorted() tạo danh sách mới nên không làm thay đổi
            thứ tự ban đầu của self.rooms.
        """

        # Kiểm tra tiêu chí sắp xếp phải là chuỗi.
        if not isinstance(criteria, str):
            _safe_print("Invalid sort criteria. Use a string such as 'price' or 'room_number'.")
            return []

        # Chuẩn hóa tiêu chí:
        # - Loại bỏ khoảng trắng ở hai đầu.
        # - Chuyển thành chữ thường.
        # - Thay dấu gạch ngang và dấu cách bằng dấu gạch dưới.
        #
        # Ví dụ:
        # "Room Number" -> "room_number"
        # "room-number" -> "room_number"
        normalized_criteria = criteria.strip().casefold().replace("-", "_")
        normalized_criteria = normalized_criteria.replace(" ", "_")

        # Xây dựng từ điển ánh xạ giữa tên tiêu chí
        # và hàm lấy giá trị dùng để sắp xếp.
        #
        # lambda room: ... là hàm ngắn gọn nhận một đối tượng phòng
        # và trả về giá trị tương ứng với tiêu chí cần sắp xếp.
        sort_keys = {
            "price": lambda room: room.price,
            "room_number": _room_number_sort_key,
            "room_id": lambda room: room.room_id.casefold(),
            "capacity": lambda room: room.capacity,
            "status": lambda room: room.status.value,
        }

        # Lấy hàm sắp xếp tương ứng với tiêu chí đã chọn.
        key = sort_keys.get(normalized_criteria)

        # Nếu không tìm thấy tiêu chí phù hợp,
        # thông báo lỗi và trả về danh sách rỗng.
        if key is None:
            _safe_print(f"Invalid room sort criteria: {criteria}.")
            return []

        # Sử dụng sorted() để tạo danh sách phòng đã sắp xếp.
        #
        # key: Hàm xác định giá trị dùng để so sánh.
        # reverse=False: Tăng dần.
        # reverse=True: Giảm dần.
        return sorted(self.rooms, key=key, reverse=reverse)

    def display_rooms(self) -> None:
        """
        Hiển thị toàn bộ danh sách phòng hiện có.

        Nếu danh sách rỗng:
            Hiển thị thông báo chưa có phòng.

        Nếu danh sách có dữ liệu:
            Duyệt từng phòng và gọi display_info() để hiển thị.

        Việc gọi display_info() thông qua từng đối tượng Room
        giúp tận dụng tính đa hình trong lập trình hướng đối tượng.

        Cụ thể:
            - Room sử dụng display_info() của lớp Room.
            - StandardRoom sử dụng display_info() đã ghi đè.
            - DeluxeRoom sử dụng display_info() đã ghi đè.
        """

        # Kiểm tra danh sách phòng có rỗng hay không.
        if not self.rooms:
            _safe_print("Danh sách phòng đang trống.")
            return

        # Duyệt từng phòng trong danh sách.
        for room in self.rooms:

            # Gọi phương thức display_info() của đối tượng.
            # Python tự động lựa chọn phiên bản phương thức
            # tương ứng với kiểu đối tượng thực tế.
            _safe_print(room.display_info())


def _safe_print(text: str) -> None:
    """
    In nội dung ra Console và xử lý vấn đề mã hóa ký tự.

    Mục đích:
        Hạn chế lỗi hiển thị ký tự khi chạy chương trình
        trên một số cửa sổ Console Windows không hỗ trợ Unicode đầy đủ.

    Tham số:
        text: Nội dung chuỗi cần hiển thị.

    Cách thực hiện:
        - Lấy encoding hiện tại của sys.stdout.
        - Nếu có encoding, chuyển chuỗi về dạng phù hợp.
        - Những ký tự không thể biểu diễn sẽ được thay thế.
        - In kết quả ra Console.

    Lưu ý:
        Hàm này chỉ phục vụ việc hiển thị thông báo,
        không làm thay đổi dữ liệu được lưu trong đối tượng phòng.
    """

    # Lấy bảng mã hiện tại của đầu ra Console.
    encoding = getattr(sys.stdout, "encoding", None)

    # Nếu xác định được bảng mã, chuyển đổi chuỗi
    # để hạn chế lỗi Unicode khi in ra màn hình.
    if encoding:
        text = text.encode(encoding, errors="replace").decode(encoding)

    # In nội dung sau khi đã xử lý mã hóa.
    print(text)


def _room_number_sort_key(room: Room) -> tuple[int, float | str]:
    """
    Xác định giá trị dùng để sắp xếp số phòng.

    Mục đích:
        Giúp sắp xếp số phòng theo giá trị số khi số phòng
        có dạng chữ số, thay vì sắp xếp theo thứ tự ký tự.

    Ví dụ:
        Nếu sắp xếp theo chuỗi thông thường:
            "1", "10", "2"

        Nếu sắp xếp theo giá trị số:
            "1", "2", "10"

    Trường hợp số phòng chứa chữ:
        Ví dụ: "A101", "B201".
        Khi đó, sử dụng thứ tự chữ cái không phân biệt hoa thường.

    Tham số:
        room: Đối tượng phòng cần lấy số phòng.

    Kết quả:
        Trả về một tuple gồm:
            - 0 và giá trị số nếu số phòng chuyển được thành số.
            - 1 và chuỗi nếu số phòng không phải dạng số.

        Giá trị đầu tiên giúp phân biệt hai nhóm dữ liệu
        trong quá trình sắp xếp.
    """

    # Lấy số phòng và loại bỏ khoảng trắng thừa.
    room_number = room.room_number.strip()

    try:
        # Nếu số phòng chuyển được thành số thực,
        # trả về nhóm 0 cùng giá trị số để sắp xếp theo số.
        return 0, float(room_number)

    except ValueError:
        # Nếu không chuyển được thành số,
        # trả về nhóm 1 cùng chuỗi đã chuẩn hóa.
        # casefold() giúp so sánh không phân biệt hoa thường.
        return 1, room_number.casefold()
