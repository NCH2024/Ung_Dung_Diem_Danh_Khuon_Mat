from customtkinter import *
from customtkinter import CTkImage
import pickle
from tkinter import ttk
import cv2
from PIL import Image
from tkinter import Toplevel
import face_recognition
from CTkMessagebox import CTkMessagebox
import os
from config.data.get_data import get_class, get_list_student
import numpy as np


class FaceRecognition:
    """
    Nhận diện và mã hóa khuôn mặt.

    Lớp này chịu trách nhiệm quản lý quá trình nhận diện và mã hóa khuôn mặt trong một ứng
    dụng với giao diện đồ họa. Nó bao gồm các thành phần như cấu hình giao diện, kết nối
    với camera, hiển thị thông tin và điều khiển các sự kiện liên quan đến nhận diện khuôn
    mặt. Lớp này được xây dựng để tích hợp với một hệ thống quản lý sinh viên theo lớp.

    :ivar students_face_encode_dir: Đường dẫn lưu trữ mã hóa khuôn mặt sinh viên.
    :type students_face_encode_dir: str
    :ivar students_face_dir: Đường dẫn lưu trữ hình ảnh khuôn mặt sinh viên.
    :type students_face_dir: str
    :ivar tree: Bảng hiển thị danh sách sinh viên theo lớp.
    :type tree: ttk.Treeview
    :ivar lbl_take_photo: Nhãn để hiển thị thông tin hướng dẫn khi chụp ảnh.
    :type lbl_take_photo: CTkLabel
    :ivar video_label: Nhãn để hiển thị video từ camera.
    :type video_label: CTkLabel
    :ivar cbx_class: ComboBox để chọn lớp học.
    :type cbx_class: CTkComboBox
    :ivar main_app: Tham chiếu tới cửa sổ chính (MainWindow) của ứng dụng.
    :type main_app: MainWindow
    :ivar user_id: ID của người dùng ứng dụng.
    :type user_id: str
    :ivar runningcamera: Trạng thái chạy của camera.
    :type runningcamera: bool
    :ivar class_id: Biến lưu tên mã lớp học được chọn.
    :type class_id: str
    :ivar varStudent: Biến lưu thông tin sinh viên được chọn.
    :type varStudent: dict
    :ivar BASE_DIR: Thư mục gốc của dự án.
    :type BASE_DIR: str
    :ivar font_label: Font được sử dụng cho các nhãn chính trong giao diện.
    :type font_label: CTkFont
    :ivar my_font: Font được sử dụng cho các thành phần khác trong giao diện.
    :type my_font: CTkFont
    :ivar primary_color: Màu chính được sử dụng trong giao diện.
    :type primary_color: str
    :ivar second_color: Màu phụ được sử dụng trong giao diện.
    :type second_color: str
    :ivar text_color: Màu chữ chính được sử dụng.
    :type text_color: str
    :ivar text_color_light: Màu chữ sáng được sử dụng.
    :type text_color_light: str
    :ivar placeholder_text_color: Màu placeholder text được sử dụng.
    :type placeholder_text_color: str
    :ivar btn_color_hover: Màu của nút khi hover.
    :type btn_color_hover: str
    :ivar btn_color: Màu của nút.
    :type btn_color: str
    :ivar toplevel: Cửa sổ con (Toplevel) của giao diện.
    :type toplevel: Toplevel
    :ivar cap: Đối tượng VideoCapture để kết nối với camera.
    :type cap: cv2.VideoCapture
    """
    def __init__(self, main_app):
        self.students_face_encode_dir = None
        self.students_face_dir = None
        self.tree = None
        self.lbl_take_photo = None
        self.video_label = None
        self.cbx_class = None
        self.main_app = main_app  # Lưu tham chiếu tới MainWindow
        self.user_id = main_app.user_id # Lấy id_user từ MainWindow
        self.runningcamera = True
        self.class_id = None # biến lưu tên lớp
        self.varStudent = None # biến lưu sinh viên

        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        # Các cài đặt biến
        self.font_label = CTkFont('Open sans', 18, 'bold')
        self.my_font = CTkFont(family='Open sans', size=16)

        # Khai baos biến lưu trữ màu sắc:
        self.primary_color = '#1974d3'
        self.second_color = '#0b4568'
        self.text_color = '#fff7d9'
        self.text_color_light = '#ffcc98'
        self.placeholder_text_color = '#989898'
        self.btn_color_hover = '#000181'
        self.btn_color = '#ffe6b6'

        # Tạo cửa sổ Toplevel
        self.toplevel = Toplevel()
        self.toplevel.title("Mã hóa nhận dạng khuôn mặt")
        self.toplevel.geometry("1000x600")
        self.toplevel.option_add('*Font', "Roboto 16")
        #self.toplevel.configure(background=self.primary_color)

        # Quản lý việc đóng cửa sổ
        self.toplevel.protocol("WM_DELETE_WINDOW", self.close_toplevel)

        # Gọi hàm tạo giao diện
        self.frame_ui()

        # Thiết lập mở cam bằng OpenCV
        self.cap = cv2.VideoCapture(0)

        # Gọi hàm mở cam tren label
        self.open_camera()

    def close_toplevel(self):
        """
        Đóng cửa sổ Toplevel và giải phóng tài nguyên liên quan đến camera.

        Summary:
        Hàm này dừng việc chạy camera nếu đang chạy, giải phóng tài nguyên liên
        quan đến camera nếu cần, đồng thời đóng và đặt lại trạng thái của cửa
        sổ Toplevel.

        Attributes:
        - runningcamera (bool): Cờ trạng thái hiển thị việc camera có đang chạy hay không.
        - cap (`cv2.VideoCapture`, optional): Đối tượng quản lý kết nối với camera đang
          được sử dụng.
        - toplevel (tkinter.Toplevel, optional): Một cửa sổ Toplevel trong giao diện
          người dùng tkinter.

        Raises:
        - AttributeError: Nếu `cap` hoặc `toplevel` không được đặt đúng.

        :return: None
        """
        # Đóng cửa sổ và dọn sạch tài nguyên
        self.runningcamera = False
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release() # giải phóng cái cam
        self.toplevel.destroy() # đóng của sổ toplevel
        self.toplevel = None  # Đặt lại trạng thái

    def frame_ui(self):
        """
        Tạo giao diện người dùng cho một cửa sổ phụ của ứng dụng chính. Giao diện này bao gồm
        các thành phần như nhãn, combobox để chọn lớp, nút nhấn về nhận dạng, nút thoát, và
        một nhãn hiển thị camera. Ngoài ra, giao diện còn hiển thị các thông báo liên quan đến
        quy trình chụp ảnh và mã hóa dữ liệu khuôn mặt.

        :param self: Tham chiếu đối tượng đến instance của lớp chứa phương thức này.

        :raises AttributeError: Nếu thuộc tính hoặc thành phần cần thiết không có trong instance.
        :raises TypeError: Nếu kiểu dữ liệu không phù hợp với các thuộc tính hoặc tham số của các
            lớp hoặc hàm được sử dụng.
        """
        # Tạo giao diện cho cửa sổ
        user_name = self.main_app.user_id
        CTkLabel(
            master=self.toplevel,
            text=f'Đang thực hiện bởi: {user_name}',
            font=self.font_label,
            text_color=self.second_color
        ).place(x=20, y=20)


        """Tạo combobox chọn lớp"""
        CTkLabel(
            master=self.toplevel,
            text='Lớp: ',
            text_color=self.second_color,
            font=self.font_label
        ).place(x=20, y=80)

        self.cbx_class = CTkComboBox(
            master=self.toplevel,
            width=230,
            values=get_class(self.user_id, False),
            dropdown_font=self.my_font,
            dropdown_hover_color=self.primary_color,
            button_color=self.text_color_light,
            button_hover_color=self.second_color,
            border_color=self.text_color_light,
            command=self.select_class
        )
        self.cbx_class.place(x=90, y=80)

        CTkLabel(
            master=self.toplevel,
            text='"Vui lòng chọn một lớp để tiếp tục"',
            font=self.my_font,
            text_color=self.primary_color
        ).place(x=50, y=200)

        btn_recognition = CTkButton(
            master=self.toplevel,
            text="Nhận dạng và mã hóa",
            font=self.font_label,
            height=60,
            width=300,
            border_width=2,
            border_color=self.second_color,
            text_color=self.second_color,
            hover_color='yellow',
            fg_color=self.text_color_light,
            corner_radius=0,

            command=lambda: self.take_photo()
        )
        btn_recognition.place(x=50, y=500)

        btn_cancel = CTkButton(
            master=self.toplevel,
            text="Thoát",
            font=self.font_label,
            height=60,
            width=80,
            border_width=2,
            border_color=self.second_color,
            text_color=self.second_color,
            hover_color='yellow',
            fg_color=self.text_color_light,
            corner_radius=0,
            command=lambda: self.close_toplevel()
        )
        btn_cancel.place(x=370, y=500)

        """Thẻ label hiển thị camera"""
        self.video_label = CTkLabel(
            master=self.toplevel,
            text='',
            fg_color=self.primary_color
        )
        self.video_label.place(x=500, y=20)

        """Hiển thị các thông tin như chụp ảnh và quá trình mã hóa"""
        if hasattr(self, "lbl_take_photo"):
            self.lbl_take_photo = CTkLabel(
                master=self.toplevel,
                height=50,
                width=400,
                text='Không được di chuyển mặt ra ngoài trong lúc mã hóa\nXoay nhẹ mặt để nhận dạng tốt hơn',
                text_color='yellow',
                bg_color=self.primary_color,
                font=self.font_label,
                anchor="center"
            )
            self.lbl_take_photo.place(x=500, y=400)

    def select_class(self, choice):
        """
        Lựa chọn lớp học và thực hiện các hành động liên quan.

        Hàm này có nhiệm vụ xử lý việc chọn lớp học và sau đó cập nhật danh sách sinh viên trong
        lớp được chọn. Đồng thời, nó cũng sẽ gọi hàm hiển thị bảng danh sách sinh viên cho lớp
        học này.

        :param choice: Lựa chọn lớp học của người dùng.
        :type choice: int
        :return: Không trả về giá trị nào.
        """
        self.class_id = None
        self.class_id = choice
        get_list_student(self.user_id, self.class_id, False)
        self.table()

    def tree_selection(self, event):
        """
        Xử lý sự kiện khi người dùng chọn một dòng trong cây (Treeview) và lấy dữ liệu từ dòng được chọn.

        :param event: Thông tin sự kiện khi một dòng trong Treeview được chọn.
        :type event: Event
        :return: Không có giá trị trả về.
        """
        selected_item = self.tree.selection()[0]  # Lấy ID của dòng được chọn
        record = self.tree.item(selected_item)['values']  # Lấy dữ liệu của dòng

        # Lưu dữ liệu vào biến
        self.varStudent = record
        print(f"ID: {record[1]}, HoTen: {record[2]}")

    def table(self):
        """
        Tạo giao diện bảng Treeview hiển thị danh sách sinh viên với các chức năng kèm theo.

        :raises: Bất kỳ lỗi tiềm tàng nào từ việc truy xuất danh sách sinh viên
            hoặc cấu hình Treeview.
        """
        self.tree = ttk.Treeview(
            self.toplevel,
            columns=("stt", "MaSV", "HoTen", "NgayThang"),
            show='headings',
            height=20
        )
        self.tree.column("stt", width=50, anchor="center")
        self.tree.heading('stt', text='STT')
        self.tree.column("MaSV", width=90, anchor="center")
        self.tree.column("HoTen", width=250, anchor="w")
        self.tree.heading('MaSV', text='MSSV')
        self.tree.heading('HoTen', text='Họ và Tên')

        # Đặt vị trí cho Treeview
        self.tree.place(x=20, y=150, width=390, height=320)

        # Tạo và đặt Scrollbar
        verscrlbar = ttk.Scrollbar(self.toplevel, orient='vertical', command=self.tree.yview)
        verscrlbar.place(x=390, y=150, width=20, height=320)

        # Kết nối Scrollbar với Treeview
        self.tree.configure(yscrollcommand=verscrlbar.set)

        # Thêm dữ liệu vào Treeview
        value = get_list_student(self.user_id, self.class_id, False)
        for index, i in enumerate(value):
            self.tree.insert('', 'end', values=(index + 1, i[0], i[1]))

        self.tree.bind("<<TreeviewSelect>>", self.tree_selection)

    """Hàm ghi hình ảnh lên label mặc định"""
    def open_camera(self):
        """
        Nhận diện và xử lý hình ảnh từ camera để phát hiện khuôn mặt và hiển thị kết quả. Hàm mở camera,
        lật hình ảnh theo chiều ngang thành dạng gương, chuyển đổi định dạng màu sắc của hình ảnh, nhận diện
        khuôn mặt, vẽ khung nhận diện khuôn mặt, và hiển thị hình ảnh kết quả lên giao diện người dùng. Nếu
        camera không khả dụng, in ra một thông báo lỗi. Hàm cũng hỗ trợ cập nhật hình ảnh theo chu kỳ 30ms
        khi camera vẫn đang hoạt động.

        :param self: Tham chiếu đến đối tượng hiện tại của lớp.

        :raises RuntimeError: Nếu không thể truy cập camera.
        """
        ret, frame = self.cap.read()
        if ret:
            # Lật hình ảnh theo chiều ngang (giống gương)
            frame = cv2.flip(frame, 1)
            # chuyển đổi sang RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Nhận diện khuôn mặt
            face_locations = face_recognition.face_locations(frame_rgb)
            for (top, right, bottom, left) in face_locations:
                # Vẽ khung quanh khuôn mặt
                cv2.rectangle(frame_rgb, (left, top), (right, bottom), (0, 255, 0), 2)

            # Tạo ảnh với CTkImage
            img_pil = Image.fromarray(frame_rgb)
            img_ctk = CTkImage(light_image=img_pil, size=(400, 300))  # Kích thước ảnh

            # Hiển thị lên label
            self.video_label.configure(image=img_ctk)
            self.video_label.image = img_ctk  # Lưu để tránh giải phóng bộ nhớ
        else:
            print("Không thể truy cập camera!")

        # Cập nhật lại sau 10ms
        if self.runningcamera:
            self.toplevel.after(30, self.open_camera)

    def take_photo(self):
        """
        Thực hiện chức năng chụp ảnh, lưu trữ và xử lý các ảnh khuôn mặt của một sinh viên được chọn.
        Ảnh khuôn mặt được trích xuất từ camera và được lưu vào thư mục được tạo
        tự động theo mã định danh của sinh viên trong một lớp học.

        :raises Exception: Nếu không thể tạo được thư mục lưu trữ hoặc gặp lỗi khởi tạo biến cho sinh viên.
        :raises SystemExit: Khi không chọn sinh viên trước khi thực hiện thao tác, hoặc khi không nhận diện
            được khuôn mặt nào từ hình ảnh.

        :ivar students_face_dir: Đường dẫn thư mục lưu trữ các ảnh khuôn mặt của sinh viên được chọn.
            Biến này được tạo tự động theo mã định danh sinh viên.
        :ivar lbl_take_photo: Trạng thái nhãn hiển thị thông báo trong giao diện.
        :ivar BASE_DIR: Đường dẫn cơ sở của thư mục dữ liệu chính.
        :ivar varStudent: Dữ liệu của sinh viên được chọn, bao gồm các thuộc tính như mã sinh viên.
        :ivar cap: Đối tượng camera đang được sử dụng để đọc frame video.
        :return: None.
        """
        # Tạo biến đếm
        count = 0

        # Lấy đường dẫn lưu file và tạo tệp theo mã sinh viên
        try:
            if not self.varStudent[1]:
                CTkMessagebox(
                    title='Thông báo lỗi!',
                    message='Hãy chọn sinh viên cần lưu trữ nhận dạng, trước khi thực hiện thao tác này!',
                    icon='cancel',
                    option_1='Đã hiểu'
                )
                return  # Nếu chưa chọn sinh viên thì dừng lại ở đây
            self.students_face_dir = os.path.join(self.BASE_DIR, "assets", "students_face", f"class_{self.class_id}", f"student_{self.varStudent[1]}")
            print("Đường dẫn sinh viên:", self.students_face_dir)

            if not os.path.exists(self.students_face_dir):
                os.makedirs(self.students_face_dir, exist_ok=True)
                print(f"[CREATING FOLDER] {self.students_face_dir}")
            else:
                print(f"[CREAED FOLDER] {self.students_face_dir} [ALREADY EXISTS]")

        except Exception as e:
            CTkMessagebox(
                title='Thông báo lỗi!',
                message='Hãy chọn sinh viên cần lưu trữ nhận dạng, trước khi thực hiện thao tác này!',
                icon='cancel',
                option_1='Đã hiểu'
            )
            print(f'[ERROR] {e}]')

        # Nếu save_path vẫn là None thì không tiếp tục
        if not self.students_face_dir:
            return

        while count < 20:
            ret, frame = self.cap.read()
            if not ret:
                print(f"[ERROR CAMERA] {self.cap.get(cv2.CAP_PROP_POS_FRAMES)} lỗi khung hình.")
                break
            # Chuyển RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Nhận diện khuôn mặt
            face_locations = face_recognition.face_locations(rgb_frame)

            if not face_locations:
                count = 0
                CTkMessagebox(
                    title='Thông báo lỗi!',
                    message="Không phát hiện khuôn mặt. Vui lòng thử lại!",
                    icon="cancel",
                    option_1="Đã hiểu"
                )
                self.lbl_take_photo.configure(text="Vui lòng nhận dạng lại!")
                return

            else:
                for (top, right, bottom, left) in face_locations:
                    # Cắt ảnh khuôn mặt
                    face_image = frame[top:bottom, left:right]
                    count += 1

                    # Lưu ảnh khuôn mặt
                    img_filename = os.path.join(self.students_face_dir, f"image_{self.varStudent[1]}_{count}.jpg")
                    cv2.imwrite(img_filename, face_image)
                    print(f"Lưu ảnh khuôn mặt {img_filename}")

                    # Vẽ khung bao quanh khuôn mặt
                    cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)

                print(f"Lấy ảnh số {count}")
                self.lbl_take_photo.configure(text=f"Lấy ảnh số {count}")
                self.toplevel.update()
        self.lbl_take_photo.configure(text="Quá trình CHỤP ẢNH hoàn tất!")
        self.toplevel.update() # Cập nhật liên tục của sổ để trách luồng dữ liệu bị thất thoát
        self.encode_faces(self.varStudent[1])

    def encode_faces(self, student_id):
        """
        Mã hóa khuôn mặt của sinh viên dựa trên các ảnh trong thư mục tương ứng. Quá trình
        bao gồm đọc ảnh, trích xuất mã hóa khuôn mặt, tính toán trung bình của các mã hóa
        trích xuất được và lưu trữ kết quả vào file.

        Các bước quan trọng:
        1. Kiểm tra sự tồn tại của thư mục chứa ảnh.
        2. Lặp qua các file ảnh, thực hiện mã hóa khuôn mặt.
        3. Lưu trữ mã hóa đã tính toán vào file `.pkl`.

        :param student_id: ID của sinh viên cần lấy mẫu khuôn mặt.
        :type student_id: str
        :return: Không có giá trị trả về.
        """
        # Kiểm tra nếu thư mục không tồn tại
        if not os.path.exists(self.students_face_dir):
            CTkMessagebox(
                title='Thông báo lỗi!',
                message='Không tìm thấy ảnh của sinh viên này!',
                icon='cancel',
                option_1='Đã hiểu'
            )
            return

        encoded_faces = []

        # Lặp qua các file trong thư mục
        for img_file in os.listdir(self.students_face_dir):
            try:
                # Tạo đường dẫn đầy đủ đến ảnh
                img_path = os.path.join(self.students_face_dir, img_file)

                # Đọc ảnh và mã hóa khuôn mặt
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    encoded_faces.append(encodings[0])  # Lưu mẫu đầu tiên từ ảnh
                else:
                    print(f"[FILTERING...] Loại bỏ khuôn mặt không tìm thấy {self.students_face_dir}/*.jpg")
            except Exception as e:
                print(f"[ERROR photo] {img_file}: {e}")

        # Tạo nơi lưu trữ mã hóa
        self.students_face_encode_dir = os.path.join(self.BASE_DIR, "assets", "encoded_face", f"class_{self.class_id}")
        file_name = f'faces_{student_id}.pkl'
        save_path = os.path.join(self.students_face_encode_dir, file_name)

        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(self.students_face_encode_dir):
            os.makedirs(self.students_face_encode_dir, exist_ok=True)
            print(f"[CREATING FOLDER] {self.students_face_encode_dir}]")
        else:
            print(f"[CREAED FOLDER] {self.students_face_encode_dir} [ALREADY EXISTS]")

        # Nếu có mã hóa khuôn mặt, tổng hợp và lưu chúng vào file .pkl
        if encoded_faces:
            try:
                # Tính trung bình của các encoding
                final_encoding = np.mean(encoded_faces, axis=0)
                with open(save_path, 'wb') as file:
                    pickle.dump(final_encoding, file)  # Ghi đè nếu file đã tồn tại
                print(f"[SAVED] {save_path}")
            except PermissionError:
                print(f"[PERMISSION ERROR] {save_path} [CANNOT WRITE]")
        else:
            print("[NONE FACE FOUND] - Không có mẫu khuôn mặt nào để mã hóa!")

        self.lbl_take_photo.configure(text=f"Quá trình MÃ HÓA sinh viên {student_id} hoàn tất!")
        self.toplevel.update()