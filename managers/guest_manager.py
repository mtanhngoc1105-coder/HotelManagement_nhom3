
# ============================================================
# Name: Nhi
# Date: 14/11/2026
# Description: Xây dựng lớp GuestManager để quản lý danh sách khách hàng.
# ============================================================

# Import lớp Guest từ module guest
from models.guest import Guest


# Định nghĩa lớp GuestManager
class GuestManager:

    # Hàm khởi tạo danh sách khách hàng
    def __init__(self):

        # Tạo danh sách rỗng để lưu các đối tượng khách hàng
        self.guests = []

    # Thêm khách hàng vào danh sách
    def add_guest(self, guest):

        # Kiểm tra đối tượng truyền vào có phải Guest hay không
        if not isinstance(guest, Guest):

            # Thông báo dữ liệu khách hàng không hợp lệ
            print("Dữ liệu khách hàng không hợp lệ!")

            # Trả về False nếu thêm thất bại
            return False

        # Kiểm tra thông tin khách hàng có hợp lệ hay không
        if not guest.validate_info():

            # Thông báo thông tin khách hàng không hợp lệ
            print("Thông tin khách hàng không hợp lệ!")

            # Trả về False nếu thông tin không hợp lệ
            return False

        # Kiểm tra mã khách hàng đã tồn tại hay chưa
        if self.find_guest(guest.get_guest_id()) is not None:

            # Thông báo mã khách hàng đã bị trùng
            print("Mã khách hàng đã tồn tại!")

            # Trả về False nếu mã khách hàng bị trùng
            return False

        # Thêm đối tượng khách hàng vào danh sách
        self.guests.append(guest)

        # Thông báo thêm khách hàng thành công
        print("Thêm khách hàng thành công!")

        # Trả về True nếu thêm thành công
        return True

    # Cập nhật thông tin khách hàng theo mã
    def update_guest(self, guest_id):

        # Tìm khách hàng cần cập nhật
        guest = self.find_guest(guest_id)

        # Kiểm tra khách hàng có tồn tại hay không
        if guest is None:

            # Thông báo không tìm thấy khách hàng
            print("Không tìm thấy khách hàng!")

            # Trả về False nếu không tìm thấy
            return False

        # Hiển thị thông tin khách hàng hiện tại
        print("Thông tin khách hàng hiện tại:")
        print(guest.display_info())

        # Nhập họ tên mới của khách hàng
        full_name = input("Nhập họ tên mới: ")

        # Nhập số điện thoại mới của khách hàng
        phone = input("Nhập số điện thoại mới: ")

        # Nhập email mới của khách hàng
        email = input("Nhập email mới: ")

        # Nhập địa chỉ mới của khách hàng
        address = input("Nhập địa chỉ mới: ")

        # Nhập số giấy tờ tùy thân mới
        identity_number = input("Nhập số giấy tờ tùy thân mới: ")

        # Tạo từ điển chứa các thông tin cần cập nhật
        data = {
            "full_name": full_name,
            "phone": phone,
            "email": email,
            "address": address,
            "identity_number": identity_number
        }

        # Gọi phương thức cập nhật thông tin của đối tượng Guest
        if guest.update_info(data):

            # Thông báo cập nhật thành công
            print("Cập nhật thông tin khách hàng thành công!")

            # Trả về True nếu cập nhật thành công
            return True

        # Thông báo nếu thông tin mới không hợp lệ
        print("Thông tin mới không hợp lệ, không thể cập nhật!")

        # Trả về False nếu cập nhật thất bại
        return False

    # Xóa khách hàng theo mã
    def delete_guest(self, guest_id):

        # Tìm khách hàng cần xóa
        guest = self.find_guest(guest_id)

        # Kiểm tra khách hàng có tồn tại hay không
        if guest is None:

            # Thông báo không tìm thấy khách hàng
            print("Không tìm thấy khách hàng!")

            # Trả về False nếu không tìm thấy
            return False

        # Xóa khách hàng khỏi danh sách
        self.guests.remove(guest)

        # Thông báo xóa khách hàng thành công
        print("Xóa khách hàng thành công!")

        # Trả về True nếu xóa thành công
        return True

    # Tìm khách hàng theo mã
    def find_guest(self, guest_id):

        # Duyệt từng khách hàng trong danh sách
        for guest in self.guests:

            # So sánh mã khách hàng với mã cần tìm
            if guest.get_guest_id() == guest_id:

                # Trả về đối tượng khách hàng nếu tìm thấy
                return guest

        # Trả về None nếu không tìm thấy khách hàng
        return None

    # Tìm kiếm khách hàng theo từ khóa
    def search_guest(self, keyword):

        # Chuyển từ khóa thành chữ thường và loại bỏ khoảng trắng thừa
        keyword = str(keyword).strip().lower()

        # Tạo danh sách để lưu kết quả tìm kiếm
        result = []

        # Duyệt từng khách hàng trong danh sách
        for guest in self.guests:

            # Lấy thông tin khách hàng và chuyển thành chữ thường
            guest_info = guest.display_info().lower()

            # Kiểm tra từ khóa có xuất hiện trong thông tin hay không
            if keyword in guest_info:

                # Thêm khách hàng phù hợp vào danh sách kết quả
                result.append(guest)

        # Trả về danh sách khách hàng tìm được
        return result

    # Hiển thị danh sách khách hàng
    def display_guests(self):

        # Kiểm tra danh sách khách hàng có rỗng hay không
        if not self.guests:

            # Thông báo danh sách hiện chưa có khách hàng
            print("Danh sách khách hàng hiện đang trống!")

            # Kết thúc phương thức nếu danh sách rỗng
            return

        # In tiêu đề danh sách khách hàng
        print("\n========== DANH SÁCH KHÁCH HÀNG ==========")

        # Duyệt từng khách hàng trong danh sách
        for guest in self.guests:

            # Hiển thị thông tin của từng khách hàng
            print(guest.display_info())

            # In đường phân cách giữa các khách hàng
            print("-" * 45)
