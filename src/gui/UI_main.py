from tkinter import *
import customtkinter
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from CTkListbox import *
from tkinter import ttk
from customtkinter import CTkImage
import cv2
import face_recognition
from PIL import Image as PILImage
from config.data.get_data import *
from src.authentication.face_authentication import FaceAuthentication

class MainUI(Frame):
    """
    Triển khai giao diện chính cho module.

    Lớp chịu trách nhiệm sinh và cấu hình giao diện cho ứng dụng quản lý điểm danh.
    Tất cả các thành phần giao diện được khởi tạo và thiết lập trong lớp này, giúp hiển
    thị thông tin lớp học, giảng viên, môn học, tiết học, và các chức năng kiểm tra danh
    sách điểm danh, trạng thái xác thực và điều khiển camera.

    Cho phép tương tác với các widget đồ họa và các tùy chỉnh cụ thể qua framework cung cấp,
    với mục đích hỗ trợ hiệu quả đối với các thao tác liên quan đến quản lý điểm danh sinh viên.

    :ivar tree: Cấu hình bảng chính (Treeview) hiển thị danh sách, tương tác với dữ liệu điểm danh.
    :ivar attendance_tree: Bảng hiển thị danh sách sinh viên đã điểm danh.
    :ivar lstbox_date: "Listbox" hiển thị thông tin về ngày học.
    :ivar lstbox_lesson: "Listbox" hiển thị thông tin về tiết học.
    :ivar lstbox_subject: "Listbox" hiển thị thông tin về môn học.
    :ivar lbl_date: Nhãn hiển thị ngày học đã chọn.
    :ivar lbl_section: Nhãn hiển thị tiết học đã chọn.
    :ivar lbl_subject: Nhãn hiển thị môn học đã chọn.
    :ivar lbl_class: Nhãn hiển thị lớp học.
    :ivar user_id: ID của người dùng (giảng viên) đang hoạt động.
    :ivar class_id: ID của lớp học được quản lý.
    :ivar subject: Môn học được điểm danh.
    :ivar lesson: Tiết học được chọn trong danh sách.
    :ivar schedule_date: Lịch học được chỉ định.
    :ivar cap: Đối tượng xử lý camera từ cv2.VideoCapture.
    :ivar left_frame: Khung bên trái của cửa sổ chính, chứa các tùy chọn thông tin.
    :ivar right_top_frame: Khung trên bên phải để hiển thị thông tin giảng viên/lớp học.
    :ivar right_bot_frame: Khung dưới bên phải hiển thị danh sách sinh viên và trạng thái camera.
    :ivar lbl_video: Nhãn hiển thị luồng camera trực tiếp.
    :ivar lbl_gif: Nhãn hiển thị các hình ảnh GIF minh họa.
    :ivar lbl_status_attendance_check: Nhãn hiển thị trạng thái xác thực điểm danh.
    :ivar lbl_name_student: Nhãn hiển thị tên sinh viên đang điểm danh.
    :ivar cbx_class: Combobox lựa chọn thông tin lớp học.
    :ivar lbl_check_info: Nhãn hiển thị thông báo kiểm tra thông tin.
    :ivar table: Khung bảng bổ sung sẽ được sử dụng nếu cần.
    :ivar current_image: Ảnh đang được xử lý hiện tại (từ camera).
    :ivar runningcamera: Biến trạng thái điều khiển camera hoạt động hay không.
    :ivar current_frame: Lưu trữ khung hình/video đang được hiển thị.
    :ivar face_authentication_instance: Đối tượng chịu trách nhiệm xác thực nhận diện khuôn mặt.
    :ivar main_root: Cửa sổ chính của ứng dụng GUI dựa trên CTk.
    :ivar my_font: Định nghĩa cấu hình font chữ chính cho giao diện.
    :ivar font_title: Định nghĩa font sử dụng cho tiêu đề chính.
    :ivar font_title_2: Định nghĩa font sử dụng cho các tiêu đề phụ.
    :ivar primary_color: Màu sắc chính được sử dụng trong giao diện.
    :ivar second_color: Màu sắc phụ hỗ trợ màu chính.
    :ivar text_color: Màu văn bản mặc định trong giao diện.
    :ivar text_color_light: Màu văn bản sáng khác, dùng cho nền đặc biệt.
    :ivar placeholder_text_color: Màu gợi nhắc ban đầu khi chưa nhập.
    :ivar btn_color_hover: Màu khi di chuột qua nút bấm.
    :ivar btn_color: Màu nền mặc định của nút bấm.
    :ivar style_treeview: Định nghĩa kiểu dáng cho các bảng dữ liệu Treeview.
    """
    def __init__(self, parent, user_id, class_id, subject, lesson, schedule_date):
        super().__init__(parent)  # Sử dụng super() để kế thừa từ Frame
        self.tree = None
        self.attendance_tree = None
        self.lstbox_date = None
        self.lstbox_lesson = None
        self.lstbox_subject = None
        self.lbl_date = None
        self.lbl_section = None
        self.lbl_subject = None
        self.lbl_class = None
        self.user_id = user_id
        self.class_id = class_id
        self.subject = subject
        self.lesson = lesson
        self.schedule_date = schedule_date
        self.schedule_date = "01-01-2000"
        self.del_val_click_tb_student_attendance_check = None
        self.cap = cv2.VideoCapture(0)
        self.left_frame = None
        self.right_top_frame = None
        self.right_bot_frame = None
        self.lbl_video = None
        self.lbl_gif = None
        self.lbl_status_attendance_check = None
        self.lbl_name_student = None
        self.cbx_class = None
        self.lbl_check_info = None
        self.table = None
        self.current_image = None
        self.runningcamera = False
        self.current_frame = None
        self.face_authentication_instance = None
        self.main_root = CTk()  # Khởi tạo cửa sổ chính
        self.my_font = CTkFont(family='Open sans', size=13)  # Khai báo font
        self.font_title = CTkFont(family='Open sans', size=18, weight='bold')
        self.font_title_2 = CTkFont(family='Open sans', size=16)
        self.runningcamera = False
        # Khai báo biến lưu trữ màu sắc
        self.primary_color = '#1974d3'
        self.second_color = '#0b4568'
        self.text_color = '#fff7d9'
        self.text_color_light = '#ffcc98'
        self.placeholder_text_color = '#989898'
        self.btn_color_hover = '#000181'
        self.btn_color = '#ffe6b6'
        self.style_treeview = ttk.Style()
        self.style_treeview.configure('Treeview', rowheight=25, font=("times new roman", 13))
        self.style_treeview.configure('Treeview.heading', font=("times new roman", 16, "bold"))

        self.setup_frame_ui()

    def setup_frame_ui(self):
        """
        Cấu hình và tạo giao diện người dùng cho ứng dụng.

        Giao diện này bao gồm các thành phần chính như khung bên trái, khung phía trên bên phải,
        và khung phía dưới bên phải. Các nhãn, nút bấm, và combobox được tạo để hiển thị thông tin
        về điểm danh, thông tin giảng viên, lớp học, ngày tháng, cũng như sử dụng camera để phục vụ
        cho việc điểm danh sinh viên.

        Giao diện được tuỳ chỉnh để hiển thị thông tin chi tiết về lớp học, học phần, tiết học, và
        trạng thái xác nhận điểm danh, đồng thời cũng cho phép bật/tắt camera và thực hiện điểm danh
        bằng phương pháp xác thực khuôn mặt.

        :param self: Đối tượng đang thao tác, thường là instance của lớp chứa phương thức này.

        :return: Không trả về giá trị nào.
        """
        # Tạo giao diện chính
        main_frame = customtkinter.CTkFrame(master=self, width=1024, height=560, corner_radius=0)
        main_frame.pack(fill="both", expand=True)

        # Chia nhỏ giao diện
        self.left_frame = customtkinter.CTkFrame(master=main_frame, width=400, height=560, fg_color=self.primary_color,
                                                 corner_radius=0)
        self.left_frame.grid(column=0, row=0, rowspan=2, sticky="nsew")

        self.right_top_frame = customtkinter.CTkFrame(master=main_frame, width=805, height=260,
                                                      fg_color=self.primary_color, corner_radius=0)
        self.right_top_frame.grid(column=1, row=0, sticky="nsew")

        self.right_bot_frame = customtkinter.CTkFrame(master=main_frame, width=805, height=300,
                                                      fg_color=self.text_color_light, corner_radius=0)
        self.right_bot_frame.grid(column=1, row=1, sticky="nsew")

        # Thêm nội dung phần bên phải
        CTkLabel(
            master=self.right_top_frame,
            text='THÔNG TIN ĐIỂM DANH:',
            font=self.font_title,
            text_color=self.second_color,
        ).place(x=20, y=10)

        CTkLabel(
            master=self.right_top_frame,
            text=f"Giảng Viên: {get_username(self.user_id)}",
            font=self.font_title_2,
            width= 300,
            anchor= "w",
            text_color=self.text_color
        ).place(x=20, y=40)

        # Gọi nhóm các tiện ích chọn
        self.group_combobox()

        # Các nhãn thông tin hiển thị
        CTkLabel(
            master=self.right_bot_frame,
            text="Danh sinh viên đã điểm danh: ",
            font=self.font_title_2,
            text_color=self.second_color
        ).place(x=10, y=10)
        if not hasattr(self, "lbl_student_attendance_check"):
            self.tb_student_attendance_check()


        CTkLabel(
            master=self.right_top_frame,
            text="LỚP: ",
            font=self.font_title,
            text_color=self.second_color
        ).place(x=370, y=10)

        CTkLabel(
            master=self.right_top_frame,
            text="Học phần: ",
            font=self.font_title,
            text_color=self.second_color
        ).place(x=370, y=40)

        CTkLabel(
            master=self.right_top_frame,
            text="Tiết: ",
            font=self.font_title,
            text_color=self.second_color
        ).place(x=670, y=40)

        CTkLabel(
            master=self.right_top_frame,
            text="Ngày: ",
            font=self.font_title,
            text_color=self.second_color
        ).place(x=570, y=10)

        if hasattr(self, 'lbl_class'):
            self.lbl_class = CTkLabel(
                master=self.right_top_frame,
                text=".......................",
                font=('Open sans', 16, 'bold'),
                text_color='white'
            )
            self.lbl_class.place(x=420, y=10)
        if hasattr(self, 'lbl_subject'):
            self.lbl_subject = CTkLabel(
                master=self.right_top_frame,
                text="..............................................",
                font=('Open sans', 13, 'bold'),
                text_color='white'
            )
            self.lbl_subject.place(x=460, y=40)
        if hasattr(self, "lbl_section"):
            self.lbl_section = CTkLabel(
                master=self.right_top_frame,
                text="............",
                font=('Open sans', 16, 'bold'),
                text_color='white'
            )
            self.lbl_section.place(x=715, y=40)
        if hasattr(self, "lbl_date"):
            self.lbl_date = CTkLabel(
                master=self.right_top_frame,
                text=".............................",
                font=('Open sans', 16, 'bold'),
                text_color='white'
            )
            self.lbl_date.place(x=630, y=10)

        # Nút kiểm tra thông tin đã chọn
        CTkButton(
            master=self.right_top_frame,
            text='KIỂM TRA',
            text_color=self.second_color,
            font=("Open sans", 15, "bold"),
            border_color=self.text_color_light,
            corner_radius=0,
            border_width=10,
            height=50,
            fg_color="light yellow",
            hover_color="yellow",
            bg_color=self.primary_color,

            command=lambda: self.check_info()
        ).place(x=600, y=190)

        # Nút xóa điểm danh sinh viên
        CTkButton(
            master=self.right_bot_frame,
            text='XÓA ĐIỂM DANH',
            text_color="white",
            font=("Open sans", 15, "bold"),
            border_color="white",
            corner_radius=10,
            border_width=5,
            height=50,
            fg_color=self.primary_color,
            hover_color=self.second_color,
            bg_color=self.primary_color,
            command=self.del_student_attendance_check
        ).place(x=620, y=200)

        # Nhãn in thông tin đã kiểm tra
        if hasattr(self, "lbl_check_info"):
            self.lbl_check_info = CTkLabel(
                master=self.right_bot_frame,
                text='Thông tin xác nhận điểm danh được ghi chú tại đây!',
                font=("Open sans", 9, "italic"),
                text_color=self.second_color,
            )
            self.lbl_check_info.place(x=10, y=270)

        #   NHÃN HIỂN THỊ KHUNG HÌNH ẢNH TRÊN GIAO DIỆN CHÍNH
        if not hasattr(self, "lbl_video") or self.lbl_video is None:
            self.lbl_video = CTkLabel(
                master=self.left_frame,
                text='Camera đã tắt',
                height=300,
                width=400,
                bg_color=self.second_color,
                text_color='green',
                font=("Open sans", 25, "italic")
            )
            self.lbl_video.place(x=0, y=0)

        # Nút mở và tắt camera
        CTkButton(
            master=self.left_frame,
            text='Mở Camera',
            text_color=self.second_color,
            font=("Open sans", 15, "bold"),
            border_color=self.text_color_light,
            corner_radius=0,
            border_width=0,
            height=40,
            fg_color="light yellow",
            hover_color="yellow",
            bg_color=self.primary_color,
            command=lambda: self.open_camera()
        ).place(x=50, y=340)
        CTkButton(
            master=self.left_frame,
            text='Tắt Camera',
            text_color=self.second_color,
            font=("Open sans", 15, "bold"),
            border_color=self.text_color_light,
            corner_radius=0,
            border_width=0,
            height=40,
            fg_color="light yellow",
            hover_color="yellow",
            bg_color=self.primary_color,
            command=lambda: self.close_camera()
        ).place(x=210, y=340)

        # NÚT ĐIỂM DANH
        CTkButton(
            master=self.left_frame,
            text='ĐIỂM DANH',
            text_color=self.text_color,
            font=("Open sans", 20, "bold"),
            corner_radius=20,
            border_color=self.second_color,
            border_width=4,
            height=60,
            width=300,
            fg_color=self.second_color,
            hover_color=self.primary_color,
            bg_color=self.primary_color,
            command=lambda: self.active_face_authencation()
        ).place(x=50, y=400)

        # Nhãn animation hiển thị khi quá trình điểm danh hoạt động
        if hasattr(self, "lbl_gif"):
            self.lbl_gif=Label(
                master=self.left_frame,
                text="",
                borderwidth=0,
                background=self.primary_color,
                foreground=self.primary_color
            )
            self.lbl_gif.place(x=70, y=470)
        if hasattr(self, "lbl_status_attendance_check"):
            self.lbl_status_attendance_check = CTkLabel(
                master=self.left_frame,
                text="",
                text_color=self.text_color,
                font=("Open sans", 14, "italic"),
                width=120,
                height=60,

            )
            self.lbl_status_attendance_check.place(x=150, y=470)

        # Nhãn hiểm thị tên của sinh viển khi điểm danh thành công
        self.lbl_name_student = CTkLabel(
            master=self.left_frame,
            text="Sinh viên:              _____",
            text_color='yellow',
            font=("Open sans", 15, "bold"),
            width=350,
            height=20,
            anchor="w"
        )
        self.lbl_name_student.place(x=50, y=310)

    def close_program(self):
        """
        Đóng ứng dụng và hủy tất cả cửa sổ đang mở.

        Phương thức này thực hiện việc đóng tất cả các cửa sổ liên quan đến
        chương trình, bao gồm cửa sổ chính và cửa sổ đăng nhập. Nếu cửa sổ
        đăng nhập tồn tại, nó sẽ được hủy. Sau đó, phương thức sẽ thực hiện
        việc thoát khỏi vòng lặp giao diện đồ họa của cửa sổ chính.

        :raises AttributeError: Nếu một thuộc tính bắt buộc không tồn tại trong đối tượng.

        """
        try:
            if hasattr(self, 'login_window') and self.login_window.winfo_exists():
                self.login_window.destroy()  # Đóng cửa sổ đăng nhập nếu nó tồn tại
        except AttributeError:
            pass
        self.main_root.quit() # Đóng cửa sổ chính

    def setup_user_info(self):
        """
        Cấu hình và hiển thị thông tin người dùng dựa trên ID của người dùng.

        Hàm này lấy tên người dùng từ ID người dùng, sau đó hiển thị thông tin bao gồm
        ID người dùng và tên người dùng trong giao diện người dùng.

        :return: Không trả về giá trị nào, chỉ thực hiện cấu hình và hiển thị thông tin.
        """
        user_name = get_username(self.user_id)
        CTkLabel(self.master, text=f'{self.user_id}, {user_name}', font=self.my_font).pack(pady=10)

    def run(self):
        """
        Đoạn mã này thực thi vòng lặp chính của ứng dụng bằng phương pháp ``mainloop`` trong
        ``main_root``.

        :return: Không trả về giá trị nào vì phương thức này khởi động vòng lặp chính
            và tiếp tục hoạt động cho đến khi ứng dụng kết thúc.
        """
        self.main_root.mainloop()

    def group_combobox(self):
        """
        Tạo và cấu hình các giao diện combobox, listbox, và nút trong phần quản lý lớp học.

        Phần này bao gồm các thành phần như combobox để chọn lớp, listbox cho các học phần, tiết, và
        ngày học. Một nút được cung cấp để tìm kiếm danh sách lớp dựa trên dữ liệu người dùng.
        Các giao diện được định nghĩa rõ ràng với phong cách thiết kế và chức năng tương ứng.

        :raises AttributeError: Nếu các thuộc tính cần thiết (lstbox_subject, lstbox_lesson,
          lstbox_date) chưa được khai báo hoặc không tồn tại trong đối tượng.

        :rtype: None
        """
        # combobox chọn lớp
        CTkLabel(
            master=self.right_top_frame,
            text='Lớp: ',
            text_color=self.text_color,
            font=self.my_font
        ).place(x=20, y=80)

        self.cbx_class = CTkComboBox(
            master=self.right_top_frame,
            width=230,
            values=get_class(self.user_id, True),
            dropdown_font=self.my_font,
            dropdown_hover_color=self.primary_color,
            button_color=self.text_color_light,
            button_hover_color=self.second_color,
            border_color=self.text_color_light,
            command=self.combobox_class
        )
        self.cbx_class.place(x=90, y=80)

        # List bõ chọn học phần
        CTkLabel(
            master=self.right_top_frame,
            text='Học phần: ',
            text_color=self.text_color,
            font=self.my_font
        ).place(x=20, y=160)
        if hasattr(self, 'lstbox_subject'):
            self.lstbox_subject = CTkListbox(
                master=self.right_top_frame,
                height=70,
                width=200,
                fg_color='white',
                border_color=self.text_color_light,
                hover_color=self.primary_color,
                command=self.select_subject
            )
            self.lstbox_subject.place(x=90, y=160)
        get_subject(self.lstbox_subject, self.user_id, self.class_id)

        # List box chọn lớp học

        CTkLabel(
            master=self.right_top_frame,
            text='Tiết: ',
            text_color=self.text_color,
            font=self.my_font
        ).place(x=340, y=80)

        if hasattr(self, 'lstbox_lesson'):
            self.lstbox_lesson = CTkListbox(
                master=self.right_top_frame,
                height=50,
                fg_color='white',
                border_color=self.text_color_light,
                hover_color=self.primary_color,
                command=self.select_section
            )
            self.lstbox_lesson.insert(0, 'Vui lòng chọn 1 môn')
            self.lstbox_lesson.place(x=370, y=80)

        # List box chọn ngày học
        CTkLabel(
            master=self.right_top_frame,
            text='Ngày: ',
            text_color=self.text_color,
            font=self.my_font
        ).place(x=330, y=160)
        if hasattr(self, 'lstbox_date'):
            self.lstbox_date = CTkListbox(
                master=self.right_top_frame,
                height=70,
                fg_color='white',
                border_color=self.text_color_light,
                hover_color=self.primary_color,
                command=self.select_date
            )
            self.lstbox_date.insert(0, 'Vui lòng chọn 1 tiết!')
            self.lstbox_date.place(x=370, y=160)

        btn_search_student = CTkButton(
            master=self.right_top_frame,
            text="Lấy danh sách lớp",
            text_color='black',
            font=self.my_font,
            border_color=self.text_color_light,
            border_width=2,
            width=230,
            fg_color="white",
            hover_color=self.second_color,
            bg_color=self.primary_color,

            command=lambda: self.search_class()
        )
        btn_search_student.place(x=90, y=115)

    def combobox_class(self, choice):
        """
        Thay đổi lớp học được lựa chọn và cập nhật các thông tin liên quan như môn học, bài học
        và giao diện hiển thị. Phương thức này cũng gọi hàm để tạo danh sách môn học dựa trên
        lớp được chọn.

        :param choice: Giá trị đại diện cho lớp học được chọn
        :type choice: str
        """
        self.class_id = choice
        self.subject = ''
        self.lesson = ''
        print(f"[SELECTED CLASS] {self.class_id}")
        get_subject(self.lstbox_subject, self.user_id, self.class_id)
        self.lbl_class.configure(text=self.class_id)

    def select_subject(self, selected_option):
        """
        Chọn môn học và thiết lập dữ liệu liên quan đến môn học được chọn.
        Cập nhật nhãn hiển thị môn học, đồng thời đặt lại bài học.
        Tự động cập nhật danh sách bài học và ngày học dựa trên môn học mới được chọn.

        :param selected_option: Môn học được chọn
        :type selected_option: str
        """
        self.subject = selected_option
        self.lesson = ''  # Reset lesson when subject changes
        print(f"[SELECTED SUBJECT] {self.subject}")
        get_lesson(self.lstbox_lesson,self.user_id, self.class_id, self.subject)
        get_schedule_date(self.lstbox_date, self.user_id, self.class_id, self.subject)
        self.lbl_subject.configure(text=self.subject)

    def select_section(self, selected_option):
        """
        Cập nhật bài học với mục được chọn và hiển thị thông tin mục đã chọn trên label.

        :param selected_option: Mục được chọn
        :type selected_option: str
        :return: Không trả về giá trị
        """
        self.lesson = selected_option
        print(f"[SELECTED SECTION] {self.lesson}")
        self.lbl_section.configure(text=self.lesson)

    def select_date(self, select_option):
        """
        Lựa chọn ngày và cập nhật giao diện theo ngày đã chọn.

        :param select_option: Tùy chọn ngày được chọn.
        :type select_option: str
        :return: None
        """
        self.schedule_date = select_option
        print(f"[SELECTED DATE] {self.schedule_date}")
        self.lbl_date.configure(text=self.schedule_date)

    def search_class(self):
        """
        Tìm kiếm và hiển thị danh sách các lớp học cụ thể dựa trên `class_id`.

        Nếu `class_id` chưa được chỉ định, thông báo lỗi sẽ hiển thị yêu cầu người
        dùng chọn lớp. Trong trường hợp lớp đã được chỉ định và bảng (table) chưa
        tồn tại, một bảng mới sẽ được tạo để hiển thị danh sách lớp. Ngược lại,
        một cửa sổ mới có chứa bảng sẽ được tạo để hiển thị danh sách lớp học.

        :raises AttributeError: Nếu `self.class_id` không tồn tại trong trường hợp kiểm tra thuộc tính.
        :raises TypeError: Nếu bảng đã được tạo nhưng `self.update_table` bị gọi sai cách.
        :param class_id: Mã định danh của lớp học cần tìm kiếm.
            Thuộc tính phải được gán trước khi gọi phương thức này.
        :type class_id: str
        """
        if not self.class_id:
            CTkMessagebox(title='Thông báo lỗi!', message='Hãy chọn lớp để lấy danh sách!', icon='cancel',
                          option_1='Thử lại')
        else:
            if not hasattr(self, 'table'):
                self.update_table()
            else:
                # Tạo mới cửa sổ table
                self.table = Toplevel(self.main_root)
                self.table.title(f'Danh sách lớp {self.class_id}')
                self.table.geometry("500x400")
                self.table.protocol("WM_DELETE_WINDOW", self.table.destroy)
                self.create_table(self.table)

    def check_info(self):
        """
        Kiểm tra thông tin điểm danh và hiển thị thông báo phù hợp.

        Hàm `check_info` được sử dụng để xác nhận thông tin được chọn bởi người dùng tại
        một số trường trong ứng dụng, đảm bảo dữ liệu đó hợp lệ hoặc thông báo lỗi khi
        có sai sót. Hàm kiểm tra xem thông tin về mã lớp, môn học, tiết học và ngày có
        được điền đầy đủ hay không, đồng thời kiểm tra khả năng khớp thông tin với
        cơ sở dữ liệu điểm danh.

        :raises CTkMessagebox: Hiển thị thông báo bằng hộp thoại thông tin tùy thuộc vào
                               từng trường hợp cụ thể bao gồm cảnh báo về dữ liệu thiếu
                               sót, lựa chọn không hợp lệ hoặc xác nhận thành công.
        """
        if (self.class_id is None
                or self.subject is None
                or self.lesson is None
                or self.schedule_date is None):
            CTkMessagebox(
                title="Cảnh báo",
                message="Vui lòng chọn đầy đủ thông tin trong các trường để tiếp tục!",
                icon="warning",
                option_1="OK"
            )
        elif not check_diemdanh(self.user_id, self.class_id, self.subject, self.lesson, self.schedule_date):
            CTkMessagebox(
                title="Cảnh báo",
                message="Lỗi! Thông tin chọn không đúng hoặc chưa chính xác!",
                icon="warning",
                option_1="Chọn lại"
            )
        else:
            CTkMessagebox(
                title="Thành công",
                message="Thông tin chọn khớp với cơ sở dữ liệu điểm danh!",
                icon="check",
                option_1="Tiếp tục"
            )
            self.lbl_check_info.configure(
            text=f"Thực hiện điểm danh lớp: {self.class_id} - Học phần: {self.subject} - Tiết: {self.lesson} - Ngày: {self.schedule_date}.")
            self.update_attendance_data()

    def on_table_close(self):
        """
        Xử lý khi cửa sổ table bị đóng. Phương thức này thực hiện việc phá hủy cửa sổ table
        và loại bỏ tham chiếu đến nó để giải phóng bộ nhớ.

        :return: None
        """
        self.table.destroy()
        del self.table

    def create_table(self, parent):
        """
        Tạo bảng Treeview với các cột, tiêu đề cột và thanh cuộn dọc được gắn kết. Bảng hiển thị thông tin sinh viên bao gồm
        số thứ tự (STT), mã số sinh viên (MSSV) và họ tên với các cột được định dạng theo chiều rộng và căn chỉnh.

        :param parent: Đối tượng widget cha trong giao diện ứng dụng, là nơi nút Treeview sẽ được gắn kết.
        :type parent: Tkinter widget
        :return: Không có giá trị trả về.
        """
        self.tree = ttk.Treeview(parent, columns=("stt", "MaSV", "HoTen"), show='headings', height=20)
        self.tree.column("stt", width=50, anchor="center")
        self.tree.heading('stt', text='STT')
        self.tree.column("MaSV", width=90, anchor="center")
        self.tree.column("HoTen", width=250, anchor="w")
        self.tree.heading('MaSV', text='MSSV')
        self.tree.heading('HoTen', text='Họ và Tên')
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        verscrlbar = ttk.Scrollbar(parent, orient='vertical', command=self.tree.yview)
        verscrlbar.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscrollcommand=verscrlbar.set)
        self.update_table()

    def update_table(self):
        """
        Xóa nội dung bảng hiện tại và cập nhật dữ liệu mới từ danh sách sinh viên.
        Hàm này sử dụng phương thức `get_list_student` để lấy dữ liệu sinh viên theo ID người dùng
        và ID lớp học, sau đó chèn dữ liệu vào bảng cây.

        :raises: ValueError nếu có lỗi xảy ra trong quá trình lấy hoặc cập nhật dữ liệu.
        """
        # Xóa toàn bộ nội dung bảng hiện tại
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Thêm dữ liệu mới vào bảng
        value = get_list_student(self.user_id, self.class_id, True)
        for index, i in enumerate(value):
            self.tree.insert('', 'end', values=(index + 1, i[0], i[1]))

    def tb_student_attendance_check(self):
        """
        Khởi tạo và cấu hình giao diện Treeview cho việc kiểm tra danh sách điểm danh
        của sinh viên, bao gồm các cột, tiêu đề, và thanh cuộn. Nội dung được cập nhật
        thông qua phương thức bổ sung dữ liệu.

        :Attributes:
            attendance_tree (ttk.Treeview): Thuộc tính lưu tham chiếu đến thành phần
            Treeview, phục vụ cho việc thao tác và cập nhật dữ liệu điểm danh.
        """
        self.tb_student = ttk.Treeview(
            self.right_bot_frame,
            columns=("stt", "MaSV", "HoTen", "NgayThang"),
            show='headings',
            height=20
        )
        self.tb_student.column("stt", width=50, anchor="center")
        self.tb_student.heading('stt', text='STT')
        self.tb_student.column("MaSV", width=90, anchor="center")
        self.tb_student.column("HoTen", width=250, anchor="w")
        self.tb_student.heading('MaSV', text='MSSV')
        self.tb_student.heading('HoTen', text='Họ và Tên')
        self.tb_student.column("NgayThang", width=200, anchor="w")
        self.tb_student.heading('NgayThang', text='Thời gian điểm danh')

        # Đặt vị trí cho Treeview
        self.tb_student.place(x=10, y=40, width=590, height=220)

        # Tạo và đặt Scrollbar
        verscrlbar = ttk.Scrollbar(self.right_bot_frame, orient='vertical', command=self.tb_student.yview)
        verscrlbar.place(x=590, y=40, width=20, height=220)

        # Kết nối Scrollbar với Treeview
        self.tb_student.configure(yscrollcommand=verscrlbar.set)

        # Lưu trữ tham chiếu đến Treeview trong thuộc tính của class
        self.attendance_tree = self.tb_student
        # Xóa toàn bộ dữ liệu trước khi thêm mới
        self.tb_student.delete(*self.tb_student.get_children())
        self.tb_student.bind("<ButtonRelease-1>", self.click_tb_student_attendance_check)

        self.update_attendance_data()  # Gọi hàm cập nhật dữ liệu lần đầu

    def click_tb_student_attendance_check(self, event):
        select_item = self.tb_student.focus()
        if select_item:
            self.del_val_click_tb_student_attendance_check = self.tb_student.item(select_item, 'values')
            print(f"[SELECT TABLE] {self.del_val_click_tb_student_attendance_check}")

    def del_student_attendance_check(self):
            if(self.del_val_click_tb_student_attendance_check is None):
                CTkMessagebox(
                    title="Cảnh báo",
                    message="Vui lòng chọn một sinh viên để xóa, nêú chưa thấy dữ liệu hãy chọn kiểm tra trước hành động này!",
                    icon="warning",
                    option_1="OK"
                )
                return
            else:
                # Hiển thị hộp thoại xác nhận trước khi xóa
                confirm = CTkMessagebox(
                    title="Xác nhận xóa",
                    message=f"Bạn có chắc muốn xóa sinh viên {self.del_val_click_tb_student_attendance_check[2]} vào lúc {self.del_val_click_tb_student_attendance_check[3]} không?",
                    icon="question",
                    option_1="OK",
                    option_2="Cancel"
                ).get()

                # Nếu chọn "OK" thì mới xóa, còn "Cancel" thì không làm gì
                if confirm == "OK":
                    student_id, schedule_date = self.del_val_click_tb_student_attendance_check[1],self.del_val_click_tb_student_attendance_check[3]
                    mess = del_attendance(student_id, schedule_date)
                    if mess:
                        CTkMessagebox(
                            title="Thao tác thành công",
                            message=f"Bạn đã xóa thành công sinh viên {self.del_val_click_tb_student_attendance_check[2]}",
                            icon="check",
                            option_1="OK"
                        )
                        self.update_attendance_data()
                    else:
                        CTkMessagebox(
                            title="Cảnh báo",
                            message="Chưa xóa được sinh viên được chọn, vui lòng thử lại sau!",
                            icon="cancel",
                            option_1="OK"
                        )
                    self.update_attendance_data()

    def update_attendance_data(self):
        """
        Cập nhật dữ liệu điểm danh trong cây giao diện bằng cách xóa các bản ghi hiện tại và
        chèn các bản ghi mới lấy từ kết quả của hàm `get_attendance_check`. Nếu không có
        dữ liệu, in ra thông báo rằng không có dữ liệu trong bảng điểm danh.

        :param None: Hàm này không nhận tham số đầu vào.
        :type None:

        :raises None: Không có lỗi nào được mô tả.

        :return: Hàm không trả về kết quả nào.
        """
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)

        values = get_attendance_report_of_day(self.class_id, self.user_id, self.subject, self.lesson, self.schedule_date)

        if values:
            for index, i in enumerate(values):
                self.attendance_tree.insert('', 'end', values=(index + 1, i[0], i[1], i[2]))
                self.main_root.update_idletasks()
        else:
            print("[NO DATA IN TABLE] Không có dữ liệu trong table điểm danh.")

    def open_camera(self):
        """
        Mở và cập nhật hình ảnh từ camera.

        Hàm này thực hiện cấu hình và khởi tạo camera, sau đó bắt đầu quá trình
        cập nhật hình ảnh từ camera để hiển thị. Trạng thái của camera đang chạy
        sẽ được cập nhật tương ứng.

        :raises RuntimeError: Khi không thể mở camera.
        """
        self.lbl_video.configure(text='')
        self.cap = cv2.VideoCapture(0)  # Mở camera
        self.runningcamera = True
        self.set_runningcamera(True)
        print(f"[RUNNING CAMERA] {self.runningcamera}")
        self.update_video()  # Bắt đầu cập nhật hình ảnh từ camera

    def update_video(self):
        """
        Cập nhật và hiển thị video trên giao diện.

        Hàm này thực hiện việc xử lý luồng video từ camera, phát hiện khuôn mặt,
        vẽ khung xung quanh các khuôn mặt được phát hiện, chuyển đổi định dạng
        hình ảnh để tích hợp vào giao diện và tiếp tục hiển thị video theo chu kỳ.

        Các bước chính bao gồm:
        1. Kiểm tra và đưa ra cảnh báo nếu thuộc tính `lbl_video` không tồn tại
           hoặc chưa được khởi tạo.
        2. Kiểm tra trạng thái camera và đưa ra thông báo lỗi nếu không mở được.
        3. Đọc khung hình từ camera và xử lý hình ảnh:
           - Lật khung hình theo chiều ngang để phản chiếu.
           - Phát hiện vị trí khuôn mặt trong khung hình.
           - Vẽ khung hình chữ nhật quanh các khuôn mặt.
           - Chuyển đổi định dạng khung hình để hiển thị trên giao diện.
        4. Cập nhật hình ảnh hiển thị trên giao diện nếu hợp lệ.
        5. Tiếp tục chu kỳ xử lý nếu camera vẫn đang chạy.

        Note rằng hàm này xử lý bất đồng bộ với chu kỳ khoảng 30ms để cập nhật khung hình.

        :param self: Đối tượng thực thi chức năng cập nhật video. Phải có các thuộc tính
            `lbl_video`, `cap`, `runningcamera`, và `main_root` để hàm hoạt động đúng cách.
        """
        if not hasattr(self, 'lbl_video') or self.lbl_video is None:
            print("lbl_video không tồn tại hoặc chưa được khởi tạo.")
            return

        if not hasattr(self, 'cap') or not self.cap.isOpened():
            print(f"[CLOSE CAMERA] {self.cap} không được mở.")
            return

        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(frame_rgb)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame_rgb, (left, top), (right, bottom), (0, 255, 0), 2)

            pil_image = PILImage.fromarray(frame_rgb)
            img = CTkImage(pil_image, size=(400, 300))

            # Lưu và cập nhật hình ảnh
            self.current_image = img
            self.lbl_video.configure(image=self.current_image)
        else:
            print("[ERROR] Không thể đọc dữ liệu từ camera.")

        if self.runningcamera:
            self.main_root.after(30, self.update_video)

    def close_camera(self):
        """
        Tắt camera và giải phóng tài nguyên liên quan.

        Phương thức này đảm nhiệm việc tắt camera, giải phóng kết nối hiện tại với
        camera và thiết lập lại trạng thái liên quan đến camera. Sau khi tắt, camera
        sẽ được giải phóng và giao diện sẽ được cập nhật để phản ánh trạng thái "đã tắt".

        :raises AttributeError: Nếu thuộc tính `cap` không tồn tại.
        """
        self.runningcamera = False
        self.set_runningcamera(False)
        self.current_frame = None
        if self.cap is not None:
            self.cap.release()  # Giải phóng camera
        self.lbl_video.configure(text='Camera đã tắt')
        print(f"[CLOSED CAMERA] {self.runningcamera} - Tắt camera.")

    def get_runningcamera(self):
        """
        Trả về giá trị của thuộc tính ``runningcamera``.

        .. note::
            Giá trị này đại diện cho camera đang chạy trong đối tượng hiện tại.

        :return: Giá trị của thuộc tính ``runningcamera``
        :rtype: bool
        """
        return self.runningcamera

    def set_runningcamera(self, value):
        """
        Đặt giá trị cho thuộc tính `runningcamera`.

        :param value: Giá trị cần đặt cho `runningcamera`.
        :type value: Bất kỳ kiểu dữ liệu nào
        """
        self.runningcamera = value

    def get_current_frame(self):
        """
        Trích xuất khung hình hiện tại từ luồng camera. Phương thức này kiểm tra trạng thái
        của camera và cố gắng đọc một khung hình từ thiết bị camera đã mở. Nếu thành công,
        khung hình hiện tại sẽ được lưu trữ dưới dạng thuộc tính `current_frame` của đối tượng.

        :param self: Đối tượng lớp chứa phương thức này.
        :return: Khung hình hiện tại được trích xuất từ camera hoặc `None` nếu quá trình
                 đọc thất bại hoặc camera đã đóng.
        :rtype: numpy.ndarray hoặc None
        """
        if self.cap is None:
            print("[CLOSED CAMERA] Camera đã đóng!")
            return None
        if not self.cap.isOpened():
            print("[CLOSED CAMERA] Camera đã đóng!")
            return None
        ret, frame = self.cap.read()
        if not ret:
            print("[RET IS FALSE] Không tìm thấy khung hình được chụp!")
            return None

        print("[SUCCESSFULLY - Frame] Đọc dữ liệu hình ảnh thành công!")
        self.current_frame = frame
        return frame

    def active_face_authencation(self):
        """
        Kích hoạt chức năng xác thực khuôn mặt của hệ thống. Phương thức này yêu cầu khởi động camera và cung cấp đầy đủ các thông tin
        cần thiết trước khi thực hiện sự kiện.

        :return: Thể hiện của lớp `FaceAuthentication` hoặc `None` nếu không thể thực hiện xác thực.
        :rtype: FaceAuthentication hoặc None
        :raises CTkMessagebox: Khi camera chưa bật hoặc thông tin cần thiết chưa được cung cấp.
        """
        if not self.runningcamera:
            CTkMessagebox(title="Cảnh báo", message="Hãy mở CAMERA trước khi thực hiện thao tác này!", icon="warning",
                          option_1="Đã hiểu")
            return

        if not all([self.user_id, self.class_id, self.schedule_date, self.lesson, self.subject]):
            CTkMessagebox(title="Cảnh báo", message="Vui lòng chọn các thông tin trước khi ĐIỂM DANH!", icon="warning",
                          option_1="Đã hiểu")
            return

        self.face_authentication_instance = FaceAuthentication(self.user_id, self.class_id, self.subject, self.lesson, self.schedule_date,
                                self)
        return self.face_authentication_instance

    def deactive_face_authencation(self):
        """
        Dừng cơ chế xác thực khuôn mặt hiện tại và trả về thể hiện đối tượng sau khi đã dừng.

        :returns: Thể hiện của `face_authentication_instance` sau khi đã dừng xác thực.
        """
        self.face_authentication_instance.stop_attendance()
        return self.face_authentication_instance