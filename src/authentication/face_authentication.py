import face_recognition
import cv2
import pickle
import os
import numpy as np
import time
import threading
from config.data.get_data import *
from src.gui.gif_animation import GifPlay

class FaceAuthentication:
    """
    Thực hiện nhận diện khuôn mặt để điểm danh.

    Lớp hỗ trợ nhận diện khuôn mặt từ hình ảnh/video và đối chiếu với dữ liệu mã hóa khuôn mặt
    được lưu trữ trước đó. Dùng để quản lý và xác thực danh tính sinh viên tham gia lớp học.

    :ivar list_student_ids: Danh sách mã số sinh viên cần điểm danh.
    :type list_student_ids: set
    :ivar face_encodings_dict: Bộ mã hóa khuôn mặt của sinh viên theo lớp học.
    :type face_encodings_dict: dict
    :ivar user_id: ID của người dùng (giáo viên hoặc quản trị viên).
    :type user_id: str
    :ivar class_id: ID của lớp học cần điểm danh.
    :type class_id: str
    :ivar subject: Tên môn học hiện tại.
    :type subject: str
    :ivar lesson: Tên bài giảng hoặc tiết học.
    :type lesson: str
    :ivar schedule_date: Ngày giờ thực hiện điểm danh.
    :type schedule_date: datetime
    :ivar main_ui: Tham chiếu đến giao diện chính của ứng dụng.
    :type main_ui: object
    :ivar cap: Nguồn cấp dữ liệu camera từ giao diện chính.
    :type cap: object
    :ivar gif: Điều khiển hiển thị hoạt ảnh trong quá trình nhận diện.
    :type gif: object
    :ivar recognized: Cờ đánh dấu đã nhận diện thành công.
    :type recognized: bool
    :ivar face_cache: Bộ cache lưu trữ dữ liệu mã hóa khuôn mặt theo lớp học.
    :type face_cache: dict
    """
    def __init__(self, user_id, class_id, subject, lesson, schedule_date, main_ui):
        self.list_student_ids = None
        self.face_encodings_dict = None
        self.user_id = user_id
        self.class_id = class_id
        self.subject = subject
        self.lesson = lesson
        self.schedule_date = schedule_date
        self.main_ui = main_ui
        self.cap = main_ui.cap
        self.gif = None
        self.recognized = False

        # Cache dữ liệu mã hóa khuôn mặt, được load 1 lần từ thư mục con cho từng lớp
        self.face_cache = {}
        self._load_face_cache_once()  # Load cache một lần khi khởi tạo

        self.face_authentication()  # Bắt đầu nhận diện

    def _load_face_cache_once(self):
        """
        Hàm này tải dữ liệu khuôn mặt từ các tệp đã mã hoá và lưu trữ dữ liệu vào bộ nhớ đệm `face_cache`.
        Hàm được thiết kế để chạy một lần nhằm đọc toàn bộ dữ liệu từ tệp vào bộ nhớ nội bộ của đối tượng.
        Nó duyệt qua một thư mục cụ thể, kiểm tra các thư mục con và tệp, chịu trách nhiệm đọc dữ liệu đã mã hóa
        của từng sinh viên bao gồm kiểm tra tính hợp lệ của dữ liệu.

        :param self: Tham chiếu tới đối tượng lớp đang gọi phương thức
                     để quản lý và lưu trữ dữ liệu bộ nhớ đệm.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        encoded_face_dir = os.path.join(base_dir, "assets", "encoded_face")
        self.face_cache = {}

        for class_folder in os.listdir(encoded_face_dir):
            folder_path = os.path.join(encoded_face_dir, class_folder)
            if os.path.isdir(folder_path) and class_folder.startswith("class_"):
                class_id = class_folder.replace("class_", "")
                self.face_cache[class_id] = {}

                for file in os.listdir(folder_path):
                    if file.endswith(".pkl"):
                        file_path = os.path.join(folder_path, file)
                        try:
                            with open(file_path, "rb") as f:
                                face_data = pickle.load(f)
                                if face_data is None or not isinstance(face_data, np.ndarray) or face_data.size == 0:
                                    print(f"[LOAD] Cảnh báo: File {file_path} không chứa dữ liệu hợp lệ!")
                                    continue
                                student_id = file.replace("faces_", "").replace(".pkl", "")
                                self.face_cache[class_id][student_id] = face_data
                                print(f"[LOAD] Đã load dữ liệu của sinh viên {student_id} từ file {file_path}")
                        except Exception as e:
                            print(f"[LOAD] Lỗi khi load file {file_path}: {e}")

    def prepare_face_encodings_for_class(self):
        """
        Prepares face encodings for a specific class by loading and processing data from the face cache.
        The method ensures conversion of face encodings to numpy arrays and retains a dictionary of
        valid encodings for students in the class.

        :raises Exception: Raised when a face encoding cannot be converted to a numpy array.
        """
        self.face_encodings_dict = {}
        class_face_data = self.face_cache.get(self.class_id, {})
        print(f"[PREPARE] Số lượng sinh viên của lớp {self.class_id}: {len(class_face_data)}")

        for student_id, face_encoding in class_face_data.items():
            if not isinstance(face_encoding, np.ndarray):
                try:
                    converted = np.array(face_encoding)
                    if converted.ndim > 0:
                        face_encoding = converted
                        print(f"[PREPARE] Đã chuyển đổi face encoding của sinh viên {student_id} sang numpy array.")
                    else:
                        print(f"[WARNING PREPARE] Dữ liệu của sinh viên {student_id} không thể chuyển đổi thành numpy array.")
                        continue
                except Exception as e:
                    print(f"[ERROR PREPARE] Không thể chuyển đổi face encoding của sinh viên {student_id}: {e}")
                    continue
            self.face_encodings_dict[student_id] = face_encoding

    def face_authentication(self):
        """
        Xác thực sinh viên qua nhận diện khuôn mặt.

        Hàm này thực hiện quy trình xác thực danh tính sinh viên thông qua việc sử dụng hệ thống
        nhận diện khuôn mặt. Nó kiểm tra thông tin đầu vào, chuẩn bị danh sách sinh viên cần điểm danh,
        chuẩn bị dữ liệu khuôn mặt và kích hoạt luồng xử lý nhận diện khuôn mặt. Nếu thông tin đầu vào
        không hợp lệ, thông báo sẽ được gửi tới người dùng.

        :param self: Referencing the current class instance.

        :raises ValueError: Nếu thông tin đầu vào không đầy đủ hoặc không hợp lệ.
        :return: Không trả về giá trị. Toàn bộ quy trình được thực hiện qua các tác vụ định nghĩa.
        """
        if check_diemdanh(self.user_id, self.class_id, self.subject, self.lesson, self.schedule_date):
            self.list_student_ids = set(self.list_id_student())
            print(f"[AUTH] Số sinh viên cần điểm danh: {len(self.list_student_ids)}")
            self.prepare_face_encodings_for_class()

            self.gif = GifPlay(self.main_ui.lbl_gif, '../../assets/systems/loading_GIF_05.gif', 0.02, width=90,
                               height=70)
            self.gif.play()
            self.main_ui.lbl_status_attendance_check.configure(text='Đang điểm danh ...')

            self.main_ui.after(1000, lambda: threading.Thread(target=self._run_face_recognition, daemon=True).start())
        else:
            CTkMessagebox(message="Chưa thể điểm danh, vui lòng kiểm tra lại thông tin!")

    def _run_face_recognition(self):
        """
        Nhận diện khuôn mặt từ video hiện tại và kiểm tra danh tính so với danh sách khuôn mặt đã biết.
        Hàm sẽ kết thúc nếu nhận diện thành công hoặc đạt giới hạn thời gian.

        :return: Không trả về giá trị nào
        """
        timeout_duration = 10
        start_time = time.time()

        while time.time() - start_time < timeout_duration and not self.recognized:
            frame = self.main_ui.get_current_frame()
            if frame is None:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(frame_rgb)
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

            if face_encodings:
                encode_frame = face_encodings[0]
                best_match_id = None
                min_distance = float('inf')

                for student_id, face_encoding in self.face_encodings_dict.items():
                    distance = np.linalg.norm(encode_frame - face_encoding)
                    if distance < min_distance:
                        min_distance = distance
                        best_match_id = student_id

                if best_match_id is not None and min_distance < 0.6:
                    name = get_name_student(self.class_id, best_match_id)

                    print(f"[RECOGNITION] Khớp khuôn mặt của sinh viên {best_match_id} - {name}")
                    self.list_student_ids.discard(best_match_id)
                    self.main_ui.after(10, self.update_attendance, best_match_id, name)
                    self.main_ui.after(10, self.main_ui.tb_student_attendance_check)
                    self.recognized=True
                    break

            time.sleep(0.5)

        self.main_ui.after(0, self._finish_attendance)

    def update_attendance(self, student_id, name):
        """
        Cập nhật trạng thái điểm danh cho sinh viên dựa trên ID sinh viên và tên.

        Hàm này thực hiện việc kiểm tra điểm danh cho một sinh viên dựa trên các thông tin
        về người dùng, lớp học, môn học, buổi học, và lịch học. Nếu xác định được điểm
        danh đã tồn tại, ID phân công sẽ được lấy và việc thêm thông tin điểm danh sẽ
        được thực hiện. Nếu điểm danh thành công, giao diện người dùng sẽ cập nhật trạng
        thái, nếu không, thông báo lỗi sẽ được hiển thị.

        :param student_id: ID của sinh viên cần điểm danh
        :type student_id: str
        :param name: Tên của sinh viên cần điểm danh
        :type name: str
        :return: None
        """
        print(f"[UPDATE] Đã điểm danh cho sinh viên {student_id} - {name}!")
        print('+-----------------------------------------------------------------------------------+')
        result = check_diemdanh(self.user_id, self.class_id, self.subject, self.lesson, self.schedule_date)
        if result is not None:
            id_of_assignment = result[1]
            value = insert_attendance_check(id_of_assignment, student_id)
            if value:
                self.main_ui.lbl_name_student.configure(text=f"Đã điểm danh: {name}")
            else:
                self.main_ui.lbl_name_student.configure(text=f"{name} đã điểm danh rồi!")
        else:
            print("[ERROR] Không thể lấy ID phân công.")

    def _finish_attendance(self):
        """
        Dừng toàn bộ các quy trình quét và hiển thị liên quan đến điểm danh; đồng thời,
        thiết lập lại các giao diện người dùng về trạng thái ban đầu.

        :raises AttributeError: Nếu đối tượng không có thuộc tính `gif`.
        """
        if hasattr(self, 'gif') and self.gif:
            self.gif.stop()
            self.main_ui.lbl_gif.configure(image='')
        self.main_ui.lbl_status_attendance_check.configure(text='')
        self.main_ui.lbl_name_student.configure(text='')

        self.face_encodings_dict = {}

    def list_id_student(self):
        """
        Trả về danh sách mã số sinh viên từ dữ liệu lọc theo user_id và class_id.

        Dữ liệu sinh viên được lấy thông qua hàm ``get_list_student`` với các tham số
        đầu vào là ``user_id`` và ``class_id``. Sau đó, trả về danh sách mã số sinh viên
        dựa trên kết quả lọc từ hàm này.

        :return: Danh sách mã số sinh viên
        :rtype: list[str]
        """
        list_student = get_list_student(self.user_id, self.class_id, select_of_user_id=True)
        return [mssv for mssv, _ in list_student]
