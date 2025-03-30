import customtkinter
import time
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from tkinter import *
from config.data.get_data import check_diemdanh, get_attendance_report_of_day, get_attendance_report_of_subject
from login_window import LoginWindow  # Import từ file mới
from src.face_recognition.face_reco_window import FaceRecognition
from UI_main import MainUI
import os
from src.reports.report_of_day import ReportOfDay
from src.reports.report_of_subject import ReportOfSubject

class MainApp:
    """
    Giúp quản lý ứng dụng điểm danh với các chức năng đăng nhập, giao diện chính,
    các công cụ tiện ích, và xử lý sự kiện liên quan.

    Lớp này chịu trách nhiệm cung cấp các chức năng cơ bản cho ứng dụng như
    khởi tạo giao diện chính, xử lý logic đăng nhập, thiết lập menu, quản lý tài nguyên,
    cũng như hiển thị báo cáo và các công cụ hỗ trợ.

    :ivar user_id: ID tài khoản người dùng hiện tại.
    :type user_id: str
    :ivar class_id: ID lớp học mà người dùng tham gia.
    :type class_id: str
    :ivar subject: Môn học tương ứng trong hệ thống.
    :type subject: str
    :ivar lesson: Chương/bài học mà người dùng đang thao tác.
    :type lesson: str
    :ivar schedule_date: Thời gian biểu của môn học.
    :type schedule_date: str
    :ivar main_ui: Giao diện chính của ứng dụng.
    :type main_ui: MainUI or None
    :ivar root: Cửa sổ chính ứng dụng.
    :type root: CTk
    :ivar login_window: Cửa sổ giao diện đăng nhập được khởi tạo khi cần.
    :type login_window: LoginWindow or None
    """
    def __init__(self, user_id, class_id, subject, lesson, schedule_date):
        self.user_id = user_id
        self.class_id = class_id
        self.subject = subject
        self.lesson = lesson
        self.schedule_date = schedule_date
        self.schedule_date = '01-01-2000'
        self.main_ui = None

        customtkinter.set_appearance_mode('light')
        self.root = CTk()
        self.root.title("Ứng dụng điểm danh")
        self.root.geometry("1204x560")
        self.root.resizable(FALSE, FALSE)
        self.login_window = None

        self.loading_ui()
        self.setup_menu()


        self.run_login()


        # Đăng ký sự kiện đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_window_close(self):
        """
        Xử lý sự kiện đóng cửa sổ ứng dụng, bao gồm việc hiển thị hộp thoại xác nhận
        và thực hiện các thao tác cần thiết trước khi kết thúc chương trình.
        Hàm này giúp đảm bảo rằng tài nguyên được giải phóng một cách an toàn
        trước khi thoát khỏi ứng dụng.

        :param None: Hàm không nhận bất kỳ tham số nào từ người gọi.
        :return: Không trả về giá trị nào.
        """
        # Hiển thị thông báo xác nhận
        if CTkMessagebox(title="Xác nhận", message="Bạn có chắc muốn thoát không?", icon="question", option_1="Có",
                         option_2="Không").get() == "Có":
            self.cleanup_resources()  # Đảm bảo các tiến trình được giải phóng
            os._exit(0)  # Thoát hoàn toàn chương trình

    def setup_menu(self):
        """
        Thiết lập và tạo các menu chính của giao diện người dùng.

        Tóm tắt:
        Hàm này chịu trách nhiệm tạo và cấu hình menu chính của ứng dụng. Bao gồm các menu như:
        - "Tệp": Chứa các mục liên quan đến xuất thống kê và thoát chương trình.
        - "Thông tin": Cung cấp thông tin hướng dẫn và thông tin về phần mềm.
        - "Tài khoản": Cung cấp tùy chọn đăng nhập và đăng xuất tài khoản.
        - "Công cụ": Hiển thị các tùy chọn thiết lập và cài đặt công cụ.

        :return: Không có giá trị trả về.
        """
        menu_bar = Menu(self.root)
        self.root.config(menu=menu_bar)

        # Tạo menu "File"
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu_child = Menu(file_menu, tearoff=0)
        file_menu_child.add_command(label="Theo ngày", command=self.open_report_of_day)
        file_menu_child.add_command(label="Theo học phần", command=self.open_report_of_subject)
        file_menu.add_cascade(label="Xuất thống kê", menu=file_menu_child)
        file_menu.add_command(label="...")
        file_menu.add_separator()
        file_menu.add_command(label="Thoát chương trình", command=self.on_window_close)

        # Tạo menu thông tin
        about_menu = Menu(menu_bar, tearoff=0)
        about_menu.add_command(label='Hướng dẫn sử dụng')
        about_menu.add_separator()
        about_menu.add_command(label='Về phần mềm...')

        # Tạo menu tài khoản
        login_menu = Menu(menu_bar, tearoff=0)
        login_menu.add_command(label="Đăng nhập", command=self.run_login)
        login_menu.add_separator()
        login_menu.add_command(label="Đăng xuất", command=self.run_login)

        # Tạo menu công cụ
        tool_menu = Menu(menu_bar, tearoff=0)
        tool_menu.add_command(label="Thiết lập mã hóa", command=self.enco_window)
        tool_menu.add_separator()
        tool_menu.add_command(label="Cài đặt")

        # Gắn các mục vào menu bar
        menu_bar.add_cascade(label="Tệp", menu=file_menu)
        menu_bar.add_cascade(label="Thông tin", menu=about_menu)
        menu_bar.add_cascade(label="Tài khoản", menu=login_menu)
        menu_bar.add_cascade(label="Công cụ", menu=tool_menu)

    def cleanup_resources(self):
        """
        Dừng các tiến trình và giải phóng tài nguyên của ứng dụng.

        Phương thức này sẽ xác minh sự tồn tại của cửa sổ đăng nhập nếu có, và sau đó đóng nó,
        đồng thời hiển thị thông báo rằng phần mềm đã dừng hoạt động.

        :return: Hàm không trả về giá trị nào.
        """
        # Dừng các tiến trình, giải phóng tài nguyên
        if self.login_window:
            self.login_window.destroy()
        print("[CLOSE APPLICATION] Đóng phần mềm")

    def run_login(self):
        """
        Ẩn cửa sổ chính và hiển thị cửa sổ đăng nhập. Nếu cửa sổ đăng nhập đã tồn tại thì sẽ đóng cửa sổ đó
        trước khi tạo và hiển thị lại cửa sổ mới. Hàm này giúp quản lý trạng thái của cửa sổ đăng nhập để
        tránh việc trùng lặp hoặc tạo quá nhiều cửa sổ không cần thiết.

        :param self: Tham chiếu đến đối tượng hiện tại (thường là một lớp trong GUI ứng dụng).
        :type self: object
        """
        # Ẩn cửa sổ chính
        self.root.withdraw()
        if self.main_ui is not None:
            for widget in self.main_ui.winfo_children():
                widget.destroy()
            self.main_ui.destroy()
            self.main_ui.class_id = None
            self.main_ui.subject = None
            self.main_ui.lesson = None
            self.main_ui = None

        if self.login_window is not None:
            self.login_window.destroy()

        # Hiển thị cửa sổ đăng nhập
        self.login_window = LoginWindow(self.root, self.on_login_success)

    def on_login_success(self, user_id):
        """
        Lưu trữ thông tin người dùng sau khi đăng nhập thành công, đóng cửa sổ đăng
        nhập, và hiển thị lại cửa sổ chính của ứng dụng.

        :param user_id: ID của người dùng đã đăng nhập thành công
        :type user_id: str
        """
        # Lưu user_id sau khi đăng nhập thành công
        print(f"[LOGIN SUCCESS] ID đăng nhập: {user_id}")
        self.user_id = user_id

        # Đóng cửa sổ đăng nhập
        if self.login_window is not None:
            self.login_window.destroy()
            self.login_window = None

        # Hiển thị lại cửa sổ chính
        self.root.deiconify()
        self.root.after(30, self.show_main_window)

    def show_main_window(self):
        """
        Tạo và hiển thị giao diện chính của ứng dụng.

        Phương thức này chịu trách nhiệm kích hoạt giao diện chính bằng cách
        khởi tạo đối tượng MainUI với các tham số liên quan và hiển thị nó
        trên cửa sổ chính của ứng dụng.

        :return: Không trả về kết quả nào.
        """
        # Tạo và hiển thị giao diện chính
        print("[CREATE UI] Kích hoạt giao diện chính...")
        self.main_ui = MainUI(self.root, self.user_id, self.class_id, self.subject, self.lesson, self.schedule_date)  # Khởi tạo đối tượng MainUI
        self.main_ui.pack(fill="both", expand=True)  # Đảm bảo giao diện được hiển thị trên cửa sổ chính

    def enco_window(self):
        """
        Hiển thị cửa sổ nhận diện khuôn mặt hoặc đưa ra cảnh báo nếu camera đang hoạt động.

        Nếu camera đang hoạt động, một thông báo cảnh báo sẽ được hiển thị để yêu cầu tắt camera
        trước khi thực hiện hành động này. Nếu không, mở cửa sổ nhận diện khuôn mặt.

        :raises RuntimeError: Nếu gặp sự cố khi đóng camera.
        """
        if self.main_ui.get_runningcamera():
            if CTkMessagebox(title="Cảnh báo!",message="Hãy tắt CAMERA trước khi thực hiện thao tác này!", icon="warning", option_1="Tắt Camera").get()=="Tắt Camera":
                self.main_ui.close_camera()
        else:
            FaceRecognition(self)

    def open_report_of_day(self):
        """
        Mở báo cáo dựa trên kiểm tra thông tin điểm danh và quyết định có tạo báo cáo trong ngày hay không.
        Nếu thông tin điểm danh không tồn tại hoặc chưa đúng, hiển thị thông báo lỗi và dừng quá trình
        xử lý.

        :raises AttributeError: nếu không có thuộc tính report_window để hủy cửa sổ báo cáo
        """
        value = get_attendance_report_of_day(self.main_ui.class_id, self.main_ui.user_id, self.main_ui.subject, self.main_ui.lesson, self.main_ui.schedule_date)
        if value and value[0] not in [None, ""]:
            ReportOfDay(self.main_ui.user_id, self.main_ui.class_id, self.main_ui.subject, self.main_ui.lesson, self.main_ui.schedule_date,
                        self)
        else:
            CTkMessagebox(title="Thao tác lỗi", message='Chưa có dữ liệu hoặc thông tin chưa được chọn (Gợi ý: Hãy kiểm tra thông tin hoặc xuất báo cáo sau khi điểm danh!)',
                          icon="warning", option_1="Đã hiểu")
            if hasattr(self, 'report_window'):
                self.report_window.destroy()
            print("[STOP REPORT] Dừng tạo báo cáo")

    def open_report_of_subject(self):

        ReportOfSubject(self.main_ui.user_id, self.main_ui.class_id, self.main_ui.subject, self.main_ui.lesson, self.main_ui.schedule_date,
                        self)

    def loading_ui(self):
        """
        Hiển thị nhãn và đặt tại trung tâm màn hình.

        :return: Không trả về giá trị.
        """
        CTkLabel(
            master=self.root,
            text='Đang tải giao diện ...'
        ).place(
            relx=0.5,
            rely=0.5,
            anchor=CENTER)

    def run(self):
        """
        Quản lý vòng lặp chính của ứng dụng GUI. Sử dụng phương pháp `mainloop` của đối tượng
        root để khởi động giao diện đồ họa và giữ nó hoạt động cho đến khi được đóng.

        :return: None

        """
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp(user_id=None, class_id=None, subject=None, lesson=None, schedule_date=None)
    app.run()



