
# ============================================================
# Name: Nhi
# Date: 14/11/2026
# Description: Xây dựng lớp Guest để lưu trữ và quản lý thông tin khách hàng.
# ============================================================

# Định nghĩa lớp Guest
class Guest:

    # Hàm khởi tạo thông tin khách hàng
    def __init__(self, guest_id, full_name, phone, email, address, identity_number):

        # Lưu mã khách hàng
        self._guest_id = guest_id

        # Lưu họ tên khách hàng
        self._full_name = full_name

        # Lưu số điện thoại khách hàng
        self._phone = phone

        # Lưu địa chỉ email của khách hàng
        self._email = email

        # Lưu địa chỉ của khách hàng
        self._address = address

        # Lưu số giấy tờ tùy thân của khách hàng
        self._identity_number = identity_number

    # Lấy mã khách hàng
    def get_guest_id(self):

        # Trả về mã khách hàng
        return self._guest_id

    # Cập nhật thông tin khách hàng
    def update_info(self, data):

        # Kiểm tra dữ liệu cập nhật có phải kiểu từ điển hay không
        if not isinstance(data, dict):

            # Trả về False nếu dữ liệu không hợp lệ
            return False

        # Lưu lại thông tin hiện tại để khôi phục nếu cập nhật thất bại
        old_info = {
            "guest_id": self._guest_id,
            "full_name": self._full_name,
            "phone": self._phone,
            "email": self._email,
            "address": self._address,
            "identity_number": self._identity_number
        }

        # Khai báo danh sách các thuộc tính được phép cập nhật
        allowed_fields = [
            "guest_id",
            "full_name",
            "phone",
            "email",
            "address",
            "identity_number"
        ]

        # Duyệt qua các trường thông tin được gửi vào
        for field in data:

            # Kiểm tra tên thuộc tính có nằm trong danh sách cho phép hay không
            if field not in allowed_fields:

                # Trả về False nếu xuất hiện thuộc tính không hợp lệ
                return False

        # Cập nhật mã khách hàng nếu có dữ liệu mới
        self._guest_id = data.get("guest_id", self._guest_id)

        # Cập nhật họ tên nếu có dữ liệu mới
        self._full_name = data.get("full_name", self._full_name)

        # Cập nhật số điện thoại nếu có dữ liệu mới
        self._phone = data.get("phone", self._phone)

        # Cập nhật email nếu có dữ liệu mới
        self._email = data.get("email", self._email)

        # Cập nhật địa chỉ nếu có dữ liệu mới
        self._address = data.get("address", self._address)

        # Cập nhật số giấy tờ tùy thân nếu có dữ liệu mới
        self._identity_number = data.get("identity_number", self._identity_number)

        # Kiểm tra tính hợp lệ của thông tin sau khi cập nhật
        if self.validate_info():

            # Trả về True nếu tất cả thông tin đều hợp lệ
            return True

        # Khôi phục mã khách hàng cũ nếu dữ liệu mới không hợp lệ
        self._guest_id = old_info["guest_id"]

        # Khôi phục họ tên cũ
        self._full_name = old_info["full_name"]

        # Khôi phục số điện thoại cũ
        self._phone = old_info["phone"]

        # Khôi phục email cũ
        self._email = old_info["email"]

        # Khôi phục địa chỉ cũ
        self._address = old_info["address"]

        # Khôi phục số giấy tờ tùy thân cũ
        self._identity_number = old_info["identity_number"]

        # Trả về False nếu cập nhật thất bại
        return False

    # Kiểm tra tính hợp lệ của thông tin khách hàng
    def validate_info(self):

        # Kiểm tra các thông tin bắt buộc không được để trống
        if not all([
            isinstance(self._guest_id, str) and self._guest_id.strip(),
            isinstance(self._full_name, str) and self._full_name.strip(),
            isinstance(self._phone, str) and self._phone.strip(),
            isinstance(self._email, str) and self._email.strip(),
            isinstance(self._address, str) and self._address.strip(),
            isinstance(self._identity_number, str) and self._identity_number.strip()
        ]):

            # Trả về False nếu có thông tin bị bỏ trống
            return False

        # Kiểm tra số điện thoại chỉ chứa chữ số
        if not self._phone.isdigit():

            # Trả về False nếu số điện thoại không hợp lệ
            return False

        # Kiểm tra email có chứa ký tự @ và dấu chấm
        if "@" not in self._email or "." not in self._email:

            # Trả về False nếu email không đúng định dạng cơ bản
            return False

        # Trả về True nếu tất cả thông tin đều hợp lệ
        return True

    # Hiển thị thông tin khách hàng
    def display_info(self):

        # Tạo chuỗi chứa toàn bộ thông tin khách hàng
        return (
            f"Mã khách hàng: {self._guest_id}\n"
            f"Họ tên: {self._full_name}\n"
            f"Số điện thoại: {self._phone}\n"
            f"Email: {self._email}\n"
            f"Địa chỉ: {self._address}\n"
            f"Số giấy tờ tùy thân: {self._identity_number}"
        )

    # Chuyển đối tượng Guest thành chuỗi
    def __str__(self):

        # Trả về thông tin khách hàng để hiển thị
        return self.display_info()
