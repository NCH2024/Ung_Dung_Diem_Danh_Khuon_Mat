from tkinter import *
import customtkinter
from customtkinter import *
from PIL import Image as PILImage
from config.data.get_data import login


class LoginWindow(Toplevel):
    """
    Các chức năng của lớp LoginWindow.

    Lớp LoginWindow đại diện cho cửa sổ đăng nhập của hệ thống. Nó bao gồm các
    thành phần giao diện người dùng để nhập tài khoản, mật khẩu, và một số thiết
    lập để hiển thị thông tin. Cửa sổ cũng tích hợp hình ảnh nền và có thể hiển
    thị hoặc ẩn mật khẩu tùy thuộc vào trạng thái của checkbox.

    :ivar on_success_callback: Hàm callback được gọi khi đăng nhập thành công.
    :ivar main_frame: Frame chính chứa các thành phần giao diện người dùng cho quá trình đăng nhập.
    :ivar ent_user: Trường nhập liệu dành cho tài khoản người dùng.
    :ivar ent_password: Trường nhập liệu dành cho mật khẩu người dùng.
    :ivar photo: Ảnh nền hiển thị bên phải cửa sổ đăng nhập.
    :ivar my_font: Kích thước và kiểu font chính được sử dụng trong các phần khác nhau của giao diện.
    :ivar note_font: Font nhỏ hơn được sử dụng cho các nội dung chú thích.
    :ivar heading_font: Font lớn đậm được dùng cho tiêu đề chính của giao diện.
    :ivar heading_font_2: Font đậm trung bình được sử dụng cho tiêu đề phụ của các khu vực khác nhau.
    :ivar primary_color: Màu sắc chính để hiển thị nền và các thành phần khác.
    :ivar text_color: Màu chủ đạo của chữ trong giao diện.
    :ivar text_color_light: Màu sáng hơn của chữ dùng cho các dòng thông báo ngắn hay mô tả.
    :ivar placeholder_text_color: Màu chữ placeholder trong các trường nhập liệu.
    :ivar btn_color_hover: Màu khi rê chuột qua nút trong giao diện.
    :ivar btn_color: Màu chính của các nút trong giao diện.
    :ivar check_var: Biến trạng thái kiểm tra của checkbox để hiện/ẩn mật khẩu.
    """
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.on_success_callback = on_success_callback
        self.geometry('850x450')
        self.title('Đăng nhập')
        self.resizable(FALSE, FALSE)
        self.attributes("-topmost", TRUE)
        self.main_frame = None
        self.ent_user = None
        self.ent_password = None
        self.photo = None
        self.btn_login = None

        self.my_font = customtkinter.CTkFont(family="Open sans", size=16)
        self.note_font = customtkinter.CTkFont(family="Open sans", size=10)
        self.heading_font = customtkinter.CTkFont(family="Open sans", size=30, weight='bold')
        self.heading_font_2 = customtkinter.CTkFont(family="Open sans", size=18, weight="bold")

        self.primary_color = '#1974d3'
        self.text_color = '#fff7d9'
        self.text_color_light = '#ffcc98'
        self.placeholder_text_color = '#989898'
        self.btn_color_hover = '#000181'
        self.btn_color = '#ffe6b6'

        self.check_var = IntVar(value=0)

        self.create_login_ui()

    def create_login_ui(self):
        """
        Tạo giao diện đăng nhập người dùng với các thành phần giao diện bao gồm khung nhập tài khoản, mật khẩu, và các nút chức năng.
        Phần giao diện cũng bao gồm các nhãn thông báo và tương tác để hỗ trợ người dùng trong trường hợp cần thiết.

        :raises RuntimeError: Nếu không thể tạo khung hoặc các phần tử giao diện không được khởi tạo đúng cách.
        :param self: Tham chiếu đến đối tượng hiện tại, cho phép truy cập các thuộc tính và phương thức của lớp chứa.
        """
        self.main_frame = customtkinter.CTkFrame(master=self, width=300, height=450, fg_color=self.primary_color)
        self.main_frame.pack(fill="both", expand=True)

        left_frame = customtkinter.CTkFrame(master=self.main_frame, width=500, height=600, fg_color=self.primary_color, corner_radius=0)
        left_frame.grid(column=0, row=0, sticky="nsew")

        right_frame = customtkinter.CTkFrame(master=self.main_frame, width=450, height=600, fg_color=self.primary_color, corner_radius=0)
        right_frame.grid(column=1, row=0, sticky="nsew")

        customtkinter.CTkLabel(left_frame, text='ĐĂNG NHẬP', text_color=self.text_color, font=self.heading_font, width=400).pack(pady=(20, 5))
        customtkinter.CTkLabel(left_frame, text='Phần mềm điểm danh nhận diện khuôn mặt', text_color=self.text_color_light, font=self.my_font).pack(pady=(0, 30))

        customtkinter.CTkLabel(left_frame, text='Tài Khoản: ', text_color=self.text_color, font=self.heading_font_2, width=280, anchor='w').pack()
        self.ent_user = customtkinter.CTkEntry(left_frame, width=300, height=50, placeholder_text='Hãy nhập vào mã cán bộ...', placeholder_text_color=self.placeholder_text_color, corner_radius=50, fg_color='white', text_color=self.primary_color, border_width=0, font=self.my_font)
        self.ent_user.pack(pady=(0, 20))

        customtkinter.CTkLabel(left_frame, text='Mật khẩu: ', text_color=self.text_color, font=self.heading_font_2, width=280, anchor='w').pack()
        self.ent_password = customtkinter.CTkEntry(left_frame, width=300, height=50, placeholder_text='Hãy nhập vào mật khẩu...', show='*', placeholder_text_color=self.placeholder_text_color, corner_radius=50, fg_color='white', text_color=self.primary_color, border_width=0, font=self.my_font)
        self.ent_password.pack(pady=(0, 5))

        ck_box = customtkinter.CTkCheckBox(left_frame, text='Hiện mật khẩu', font=self.my_font, text_color=self.text_color, border_color=self.text_color_light, onvalue=1, offvalue=0, variable=self.check_var, command=self.show_password)
        ck_box.pack(pady=(10, 0))

        self.btn_login = customtkinter.CTkButton(
            left_frame,
            text='Đăng nhập',
            font=self.heading_font_2,
            height=50, width=100,
            fg_color=self.btn_color_hover,
            text_color='white', border_width=2,
            border_color=self.btn_color_hover,
            corner_radius=50, hover_color=self.btn_color,
            command=lambda :login(self.ent_user, self.ent_password, self.on_success_callback)
        )
        self.btn_login.pack(pady=(10, 0))

        customtkinter.CTkLabel(left_frame, text='Liên hệ nhà phát triển nếu gặp lỗi! Tel: 0357379334', text_color=self.text_color, font=self.note_font).pack(pady=(20, 5))

        self.set_background_image(right_frame)

        self.ent_user.bind("<Return>",lambda event: login(self.ent_user, self.ent_password, self.on_success_callback))
        self.ent_password.bind("<Return>",lambda event: login(self.ent_user, self.ent_password, self.on_success_callback))

    def set_background_image(self, right_frame):
        """
        Đặt hình nền vào trong giao diện bên trong một khung cụ thể.

        Hàm này đọc một ảnh từ một vị trí định sẵn, thay đổi kích thước của ảnh,
        rồi chuyển ảnh vào dạng phù hợp để sử dụng với thư viện customtkinter.
        Ảnh sau đó được gán vào một nhãn và hiển thị tràn khung chỉ định.

        :param right_frame: Khung (frame) nơi được đặt hình nền.
            Đây phải là một đối tượng tkinter frame để hỗ trợ cấu hình giao diện.
        :return: None
        """
        try:
            # Đọc ảnh và thay đổi kích thước
            image = PILImage.open(r"..\..\assets\systems\background\bg_login.jpg")
            image = image.resize((600, 600))  # Resize để phù hợp với khung

            # Chuyển ảnh từ Pillow (PIL.Image) sang CTkImage
            self.photo = CTkImage(light_image=image, size=(600, 600))

            # Sử dụng CTkLabel từ customtkinter
            image_label = CTkLabel(right_frame, image=self.photo, text="")
            image_label.place(relwidth=1, relheight=1)  # Đặt hình ảnh theo kích thước của frame
        except Exception as e:
            print(f"Error loading background image: {e}")

    def show_password(self):
        """
        Hiển thị hoặc ẩn mật khẩu dựa trên trạng thái của biến kiểm tra.

        Phương thức này kiểm tra trạng thái của biến `self.check_var`. Nếu giá trị
        của biến là 1, trường mật khẩu sẽ được hiển thị dưới dạng văn bản thông
        thường. Ngược lại, nếu biến không phải 1, trường mật khẩu sẽ hiển thị dưới
        dạng các ký tự thay thế (như dấu '*') để bảo vệ thông tin nhạy cảm.

        :return: Không trả về giá trị nào.
        """
        if self.check_var.get() == 1:
            self.ent_password.configure(show='')
        else:
            self.ent_password.configure(show='*')

