
"""Mô hình phòng và các loại phòng của khách sạn.

File này định nghĩa các lớp dùng để biểu diễn thông tin phòng trong hệ thống
quản lý khách sạn, bao gồm:

- Room: Lớp cơ sở, lưu trữ những thông tin chung của một phòng.
- StandardRoom: Lớp phòng tiêu chuẩn, kế thừa từ Room.
- DeluxeRoom: Lớp phòng Deluxe, kế thừa từ Room.
- RoomStatus: Enum quy định những trạng thái hợp lệ của phòng.

Các lớp trong file tập trung vào quản lý dữ liệu và xử lý thông tin của phòng.
Việc thêm, sửa, xóa, tìm kiếm và sắp xếp danh sách phòng được thực hiện
trong lớp RoomManager ở file managers/room_manager.py.
"""

# Enum được sử dụng để định nghĩa tập hợp các trạng thái cố định của phòng.
from enum import Enum

# isfinite dùng để kiểm tra một số có phải số hữu hạn hay không.
# Ví dụ: loại bỏ các giá trị vô cực (inf) và không phải số (nan).
from math import isfinite

# Any: cho phép khai báo kiểu dữ liệu linh hoạt khi kiểm tra giá trị.
# Mapping: biểu diễn dữ liệu dạng ánh xạ khóa - giá trị,
# thường được sử dụng khi truyền thông tin cần cập nhật.
from typing import Any, Mapping


class RoomStatus(str, Enum):
    """Định nghĩa các trạng thái hợp lệ của phòng khách sạn.

    Kế thừa từ str và Enum để mỗi trạng thái vừa là một hằng số Enum,
    vừa có thể sử dụng như một giá trị chuỗi khi xử lý dữ liệu.

    Các trạng thái:
    - AVAILABLE: Phòng còn trống, có thể được đặt.
    - BOOKED: Phòng đã được đặt trước.
    - OCCUPIED: Phòng đang có khách lưu trú.
    - MAINTENANCE: Phòng đang bảo trì, không được sử dụng.
    """

    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"


class Room:
    """Lớp cơ sở mô tả những thông tin chung của một phòng khách sạn.

    Đây là lớp cha của StandardRoom và DeluxeRoom.

    Các thuộc tính được đóng gói bằng dấu gạch dưới (_) để hạn chế
    việc truy cập và thay đổi dữ liệu trực tiếp từ bên ngoài.

    Việc đọc và cập nhật thuộc tính được thực hiện thông qua property,
    giúp kiểm tra tính hợp lệ của dữ liệu trước khi lưu.
    """

    def __init__(
        self,
        room_id: str,
        room_number: str,
        price: float,
        status: RoomStatus | str,
        description: str,
        capacity: int,
    ) -> None:
        """Khởi tạo một phòng với các thông tin cơ bản.

        Args:
            room_id: Mã định danh duy nhất của phòng.
            room_number: Số phòng hiển thị trong khách sạn.
            price: Đơn giá cơ sở của phòng cho một ngày.
            status: Trạng thái hiện tại của phòng.
            description: Mô tả đặc điểm của phòng.
            capacity: Số lượng khách tối đa phòng có thể phục vụ.

        Mỗi giá trị đều được kiểm tra trước khi gán vào thuộc tính.
        Nếu dữ liệu không hợp lệ, chương trình sẽ phát sinh ngoại lệ.
        """

        # Dấu "_" thể hiện các thuộc tính được đóng gói.
        # Dữ liệu được kiểm tra trước khi lưu để tránh giá trị không hợp lệ.
        self._room_id = self._validate_field("room_id", room_id)
        self._room_number = self._validate_field("room_number", room_number)
        self._price = self._validate_field("price", price)
        self._status = self._validate_field("status", status)
        self._description = self._validate_field("description", description)
        self._capacity = self._validate_field("capacity", capacity)

    @staticmethod
    def _validate_field(field: str, value: Any) -> Any:
        """Kiểm tra dữ liệu dựa trên tên thuộc tính cần xử lý.

        Đây là phương thức tĩnh (staticmethod), không cần truy cập
        đến đối tượng self nên có thể dùng chung cho nhiều lớp.

        Args:
            field: Tên thuộc tính cần kiểm tra.
            value: Giá trị được truyền vào thuộc tính đó.

        Returns:
            Giá trị đã được kiểm tra và chuẩn hóa nếu hợp lệ.

        Raises:
            TypeError: Khi giá trị không đúng kiểu dữ liệu.
            ValueError: Khi giá trị đúng kiểu nhưng không hợp lệ.

        Phương thức này được sử dụng trong:
        - Hàm khởi tạo của các lớp.
        - Các property setter.
        - Phương thức cập nhật thông tin phòng.
        """

        # Kiểm tra mã phòng và số phòng.
        # Hai trường này phải là chuỗi và không được để trống.
        if field in ("room_id", "room_number"):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} phải là chuỗi không được để trống.")

            # strip() loại bỏ khoảng trắng thừa ở đầu và cuối chuỗi.
            return value.strip()

        # Kiểm tra đơn giá phòng.
        if field == "price":

            # bool là lớp con của int trong Python nên cần loại trừ riêng.
            # Đơn giá chỉ được nhận kiểu int hoặc float.
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError("price phải là một số.")

            try:
                # Chuyển đơn giá về float để thống nhất kiểu dữ liệu.
                price = float(value)
            except OverflowError as exc:
                raise ValueError("price phải là số dương hữu hạn.") from exc

            # Đơn giá phải lớn hơn 0 và không được là inf hoặc nan.
            if not isfinite(price) or price <= 0:
                raise ValueError("price phải là số dương hữu hạn.")

            return price

        # Kiểm tra trạng thái phòng.
        if field == "status":

            # Nếu đầu vào đã là một giá trị RoomStatus thì sử dụng trực tiếp.
            if isinstance(value, RoomStatus):
                return value

            # Nếu đầu vào là chuỗi, chuẩn hóa về chữ in hoa
            # rồi chuyển thành giá trị tương ứng của RoomStatus.
            if isinstance(value, str):
                try:
                    return RoomStatus(value.strip().upper())
                except ValueError as exc:
                    raise ValueError(
                        "status không thuộc tập trạng thái hợp lệ."
                    ) from exc

            # Không chấp nhận các kiểu dữ liệu khác.
            raise TypeError("status phải là RoomStatus hoặc chuỗi trạng thái hợp lệ.")

        # Kiểm tra phần mô tả của phòng.
        if field == "description":
            if not isinstance(value, str):
                raise TypeError("description phải là chuỗi.")

            return value.strip()

        # Kiểm tra sức chứa tối đa của phòng.
        if field == "capacity":

            # Sức chứa phải là số nguyên, không chấp nhận Boolean.
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError("capacity phải là số nguyên.")

            # Một phòng phải có sức chứa ít nhất là một người.
            if value <= 0:
                raise ValueError("capacity phải là số nguyên dương.")

            return value

        # Kiểm tra các thuộc tính có kiểu Boolean.
        # Những thuộc tính này được sử dụng trong các lớp phòng con.
        if field == "has_window" or field == "has_balcony":
            if not isinstance(value, bool):
                raise TypeError(f"{field} phải là kiểu Boolean.")

            return value

        # Kiểm tra loại giường của phòng Standard.
        if field == "bed_type":
            if not isinstance(value, str) or not value.strip():
                raise ValueError("bed_type phải là chuỗi không được để trống.")

            return value.strip()

        # Kiểm tra danh sách tiện ích của phòng Deluxe.
        if field == "amenities":

            # Tiện ích phải được truyền dưới dạng danh sách.
            if not isinstance(value, list):
                raise TypeError("amenities phải là một danh sách.")

            # Từng tiện ích phải là chuỗi và không được để trống.
            if any(not isinstance(item, str) or not item.strip() for item in value):
                raise ValueError(
                    "Mỗi tiện ích phải là chuỗi không được để trống."
                )

            # Tạo danh sách mới đã loại bỏ khoảng trắng thừa.
            return [item.strip() for item in value]

        # Nếu tên trường không nằm trong danh sách hỗ trợ,
        # chương trình không cho phép cập nhật trường đó.
        raise ValueError(f"Không thể cập nhật trường không hợp lệ: {field}.")

    def _updatable_fields(self) -> set[str]:
        """Trả về tập hợp những thuộc tính được phép cập nhật của lớp Room.

        Phương thức này được ghi đè ở các lớp con để bổ sung
        những thuộc tính riêng của từng loại phòng.

        Returns:
            Tập hợp tên các thuộc tính có thể cập nhật.
        """

        return {
            "room_id",
            "room_number",
            "price",
            "status",
            "description",
            "capacity",
        }

    # ==================== CÁC PROPERTY ====================
    # Property cho phép truy cập thuộc tính giống như biến thông thường,
    # nhưng vẫn kiểm soát được quá trình đọc và ghi dữ liệu.

    @property
    def room_id(self) -> str:
        """Lấy mã định danh của phòng."""
        return self._room_id

    @room_id.setter
    def room_id(self, value: str) -> None:
        """Cập nhật mã phòng sau khi kiểm tra tính hợp lệ."""
        self._room_id = self._validate_field("room_id", value)

    @property
    def room_number(self) -> str:
        """Lấy số phòng."""
        return self._room_number

    @room_number.setter
    def room_number(self, value: str) -> None:
        """Cập nhật số phòng sau khi kiểm tra dữ liệu."""
        self._room_number = self._validate_field("room_number", value)

    @property
    def price(self) -> float:
        """Lấy đơn giá cơ sở của phòng."""
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        """Cập nhật đơn giá phòng với điều kiện giá phải hợp lệ."""
        self._price = self._validate_field("price", value)

    @property
    def status(self) -> RoomStatus:
        """Lấy trạng thái hiện tại của phòng."""
        return self._status

    @status.setter
    def status(self, value: RoomStatus | str) -> None:
        """Cập nhật trạng thái phòng sau khi kiểm tra trạng thái hợp lệ."""
        self._status = self._validate_field("status", value)

    @property
    def description(self) -> str:
        """Lấy nội dung mô tả phòng."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Cập nhật mô tả phòng."""
        self._description = self._validate_field("description", value)

    @property
    def capacity(self) -> int:
        """Lấy sức chứa tối đa của phòng."""
        return self._capacity

    @capacity.setter
    def capacity(self, value: int) -> None:
        """Cập nhật sức chứa sau khi kiểm tra số nguyên dương."""
        self._capacity = self._validate_field("capacity", value)

    # ==================== CÁC PHƯƠNG THỨC GETTER/SETTER ====================

    def get_room_id(self) -> str:
        """Trả về mã phòng.

        Phương thức getter cung cấp cách lấy dữ liệu thông qua phương thức,
        bên cạnh cách truy cập bằng property.
        """
        return self.room_id

    def get_price(self) -> float:
        """Trả về đơn giá cơ sở của phòng."""
        return self.price

    def set_price(self, price: float) -> None:
        """Thay đổi đơn giá phòng thông qua property setter.

        Giá trị mới vẫn phải vượt qua bước kiểm tra dữ liệu.
        """
        self.price = price

    def get_status(self) -> RoomStatus:
        """Trả về trạng thái hiện tại của phòng."""
        return self.status

    def set_status(self, status: RoomStatus | str) -> None:
        """Thay đổi trạng thái phòng sau khi kiểm tra tính hợp lệ."""
        self.status = status

    # ==================== CẬP NHẬT THÔNG TIN PHÒNG ====================

    def update_info(self, data: Mapping[str, Any]) -> None:
        """Cập nhật một hoặc nhiều thuộc tính của phòng.

        Args:
            data: Dữ liệu cần cập nhật theo dạng khóa - giá trị.
                  Ví dụ: {"price": 500000, "capacity": 3}.

        Quá trình cập nhật gồm hai bước:
        1. Kiểm tra toàn bộ tên trường và giá trị mới.
        2. Chỉ khi tất cả dữ liệu hợp lệ mới tiến hành cập nhật.

        Cách làm này giúp tránh trường hợp một số thuộc tính đã được
        cập nhật nhưng thuộc tính khác lại gặp lỗi.
        """

        # Kiểm tra dữ liệu đầu vào có phải dạng Mapping hay không.
        if not isinstance(data, Mapping):
            raise TypeError("data phải là một mapping các trường cần cập nhật.")

        # Tên thuộc tính phải là chuỗi để có thể đối chiếu với danh sách
        # những trường được phép cập nhật.
        if any(not isinstance(field, str) for field in data):
            raise TypeError("Tên trường cập nhật phải là chuỗi.")

        # Lấy danh sách các trường được phép cập nhật.
        # Lớp con có thể bổ sung thêm trường riêng thông qua ghi đè phương thức.
        allowed_fields = self._updatable_fields()

        # Xác định những trường không được hỗ trợ.
        unknown_fields = set(data) - allowed_fields

        # Nếu xuất hiện trường không hợp lệ thì dừng cập nhật.
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Trường cập nhật không hợp lệ: {names}.")

        # Kiểm tra toàn bộ giá trị mới trước khi thay đổi đối tượng.
        # Dictionary này chỉ chứa dữ liệu đã được xác thực.
        updates = {
            field: self._validate_field(field, value)
            for field, value in data.items()
        }

        # Sau khi tất cả giá trị hợp lệ, tiến hành cập nhật.
        # setattr cho phép gán giá trị theo tên thuộc tính.
        # Việc gán thông qua property sẽ tiếp tục sử dụng setter tương ứng.
        for field, value in updates.items():
            setattr(self, field, value)

    # ==================== HIỂN THỊ THÔNG TIN ====================

    def display_info(self) -> str:
        """Tạo chuỗi chứa đầy đủ thông tin cơ bản của phòng.

        Returns:
            Chuỗi thông tin gồm mã phòng, số phòng, giá, trạng thái,
            sức chứa và mô tả.

        Phương thức được ghi đè ở StandardRoom và DeluxeRoom
        để bổ sung các thông tin riêng của từng loại phòng.
        """

        return (
            f"Mã phòng: {self.room_id} | Số phòng: {self.room_number} | "
            f"Giá: {self.price:.2f} | Trạng thái: {self.status.value} | "
            f"Sức chứa: {self.capacity} | Mô tả: {self.description}"
        )

    def __str__(self) -> str:
        """Trả về thông tin phòng khi sử dụng print() hoặc str().

        Ví dụ:
            print(room)

        Phương thức này gọi display_info() để tránh lặp lại
        logic tạo chuỗi thông tin phòng.
        """
        return self.display_info()


class StandardRoom(Room):
    """Lớp mô tả phòng tiêu chuẩn.

    StandardRoom kế thừa Room nên sử dụng lại các thuộc tính và
    phương thức chung của lớp cha.

    Ngoài những thông tin cơ bản, phòng tiêu chuẩn có thêm:
    - has_window: Phòng có cửa sổ hay không.
    - bed_type: Loại giường được trang bị.

    Lớp này ghi đè display_info() để bổ sung thông tin riêng
    và định nghĩa cách tính giá cho phòng tiêu chuẩn.
    """

    def __init__(
        self,
        room_id: str,
        room_number: str,
        price: float,
        status: RoomStatus | str,
        description: str,
        capacity: int,
        has_window: bool,
        bed_type: str,
    ) -> None:
        """Khởi tạo một phòng tiêu chuẩn.

        Các thông tin chung được khởi tạo thông qua hàm __init__()
        của lớp cha Room bằng từ khóa super().

        Sau đó, khởi tạo và kiểm tra hai thuộc tính riêng của phòng.
        """

        # Gọi hàm khởi tạo của lớp cha để thiết lập dữ liệu chung.
        super().__init__(room_id, room_number, price, status, description, capacity)

        # Khởi tạo thuộc tính riêng của StandardRoom.
        self._has_window = self._validate_field("has_window", has_window)
        self._bed_type = self._validate_field("bed_type", bed_type)

    def _updatable_fields(self) -> set[str]:
        """Bổ sung các thuộc tính riêng của phòng tiêu chuẩn
        vào danh sách trường được phép cập nhật.

        Đây là ví dụ về tính đa hình thông qua phương thức ghi đè.
        """
        return super()._updatable_fields() | {"has_window", "bed_type"}

    @property
    def has_window(self) -> bool:
        """Kiểm tra phòng có cửa sổ hay không."""
        return self._has_window

    @has_window.setter
    def has_window(self, value: bool) -> None:
        """Cập nhật thông tin cửa sổ sau khi kiểm tra kiểu Boolean."""
        self._has_window = self._validate_field("has_window", value)

    @property
    def bed_type(self) -> str:
        """Lấy loại giường của phòng tiêu chuẩn."""
        return self._bed_type

    @bed_type.setter
    def bed_type(self, value: str) -> None:
        """Cập nhật loại giường, không chấp nhận chuỗi rỗng."""
        self._bed_type = self._validate_field("bed_type", value)

    def calculate_price(self, days: float) -> float:
        """Tính tổng tiền phòng tiêu chuẩn theo số ngày lưu trú.

        Args:
            days: Số ngày khách lưu trú.

        Returns:
            Tổng tiền phòng = đơn giá cơ sở x số ngày.

        Số ngày phải là số dương và hữu hạn.
        """
        days = _validate_days(days)

        # Phòng tiêu chuẩn sử dụng hệ số giá 1.0.
        return self.price * days

    def display_info(self) -> str:
        """Ghi đè phương thức hiển thị của lớp Room.

        Tận dụng thông tin chung từ lớp cha, sau đó bổ sung
        thông tin cửa sổ và loại giường.
        """
        return (
            f"[StandardRoom] {super().display_info()} | "
            f"Cửa sổ: {'Có' if self.has_window else 'Không'} | "
            f"Loại giường: {self.bed_type}"
        )


class DeluxeRoom(Room):
    """Lớp mô tả phòng Deluxe.

    DeluxeRoom kế thừa các thuộc tính và phương thức chung từ Room.

    Ngoài thông tin cơ bản, phòng Deluxe có thêm:
    - amenities: Danh sách tiện ích đi kèm.
    - has_balcony: Cho biết phòng có ban công hay không.

    Lớp này ghi đè phương thức tính giá và hiển thị thông tin
    để phù hợp với đặc điểm riêng của phòng Deluxe.
    """

    def __init__(
        self,
        room_id: str,
        room_number: str,
        price: float,
        status: RoomStatus | str,
        description: str,
        capacity: int,
        amenities: list[str],
        has_balcony: bool,
    ) -> None:
        """Khởi tạo một phòng Deluxe.

        Trước tiên gọi hàm khởi tạo của Room để thiết lập
        những thuộc tính chung.

        Tiếp theo khởi tạo danh sách tiện ích và thông tin ban công.
        """

        # Tái sử dụng hàm khởi tạo của lớp cha.
        super().__init__(room_id, room_number, price, status, description, capacity)

        # Khởi tạo các thuộc tính riêng của phòng Deluxe.
        self._amenities = self._validate_field("amenities", amenities)
        self._has_balcony = self._validate_field("has_balcony", has_balcony)

    def _updatable_fields(self) -> set[str]:
        """Bổ sung thuộc tính riêng của phòng Deluxe vào danh sách cập nhật.

        Phương thức được ghi đè để lớp DeluxeRoom có thể cập nhật
        cả những thuộc tính chung lẫn thuộc tính đặc thù.
        """
        return super()._updatable_fields() | {"amenities", "has_balcony"}

    @property
    def amenities(self) -> list[str]:
        """Trả về danh sách tiện ích của phòng.

        Sử dụng copy() để tạo một bản sao danh sách.
        Nhờ đó, việc thay đổi danh sách nhận được từ bên ngoài
        không làm thay đổi trực tiếp dữ liệu nội bộ của đối tượng.
        """
        return self._amenities.copy()

    @amenities.setter
    def amenities(self, value: list[str]) -> None:
        """Cập nhật danh sách tiện ích sau khi kiểm tra dữ liệu."""
        self._amenities = self._validate_field("amenities", value)

    @property
    def has_balcony(self) -> bool:
        """Cho biết phòng Deluxe có ban công hay không."""
        return self._has_balcony

    @has_balcony.setter
    def has_balcony(self, value: bool) -> None:
        """Cập nhật thông tin ban công với giá trị Boolean hợp lệ."""
        self._has_balcony = self._validate_field("has_balcony", value)

    def calculate_price(self, days: float) -> float:
        """Tính tổng tiền phòng Deluxe theo số ngày lưu trú.

        Args:
            days: Số ngày khách lưu trú.

        Returns:
            Tổng tiền phòng = đơn giá cơ sở x hệ số 1.5 x số ngày.

        Lưu ý:
            Hệ số 1.5 hiện là quy ước tạm thời của chương trình.
            Nhóm cần thống nhất hệ số phụ thu trước khi tích hợp
            với các module khác.
        """
        days = _validate_days(days)

        # Phòng Deluxe hiện sử dụng hệ số giá 1.5.
        # Phép tính không làm thay đổi đơn giá cơ sở của phòng.
        return self.price * 1.5 * days

    def display_info(self) -> str:
        """Ghi đè phương thức hiển thị thông tin của lớp Room.

        Bổ sung danh sách tiện ích và thông tin ban công
        vào phần thông tin chung của phòng.
        """

        # Chuyển danh sách tiện ích thành chuỗi để dễ hiển thị.
        # Nếu danh sách rỗng thì thông báo phòng chưa có tiện ích.
        amenities = ", ".join(self._amenities) if self._amenities else "Không có"

        return (
            f"[DeluxeRoom] {super().display_info()} | "
            f"Tiện ích: {amenities} | "
            f"Ban công: {'Có' if self.has_balcony else 'Không'}"
        )


def _validate_days(days: float) -> float:
    """Kiểm tra số ngày lưu trú trước khi tính tiền phòng.

    Args:
        days: Số ngày lưu trú cần kiểm tra.

    Returns:
        Số ngày đã được chuyển về kiểu float.

    Raises:
        TypeError: Nếu số ngày không phải int hoặc float.
        ValueError: Nếu số ngày nhỏ hơn hoặc bằng 0,
                    là số vô cực hoặc không phải số.

    Hàm được đặt bên ngoài các lớp vì cả StandardRoom và DeluxeRoom
    đều sử dụng chung quy tắc kiểm tra số ngày.
    """

    # Không chấp nhận Boolean dù bool có quan hệ kế thừa với int.
    if isinstance(days, bool) or not isinstance(days, (int, float)):
        raise TypeError("days phải là một số.")

    try:
        # Chuẩn hóa số ngày về kiểu float.
        days = float(days)
    except OverflowError as exc:
        raise ValueError("days phải là số dương hữu hạn.") from exc

    # Số ngày phải lớn hơn 0 và là số hữu hạn.
    if not isfinite(days) or days <= 0:
        raise ValueError("days phải là số dương hữu hạn.")

    return days
