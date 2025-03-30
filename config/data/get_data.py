from CTkMessagebox import CTkMessagebox
import mysql.connector
import datetime

from pyexpat.errors import messages

from config.settings.connectdb import connect_database

if connect_database():
    print("[CONNECTION TO DATABASE SUCCESSFULLY]")
else:
    print("[CONNECTION TO DATABASE FAILED]")


# Các hàm sử dụng kết nối từ pool
def login(entry_user, entry_password, on_success_calback):
    """
    Thực hiện đăng nhập người dùng là cán bộ hoặc admin phần mềm
    :param entry_user: Lưu trữ giá trị là một chuỗi id người dùng trong cơ sở dữ liệu
    :param entry_password: Lưu trữ giá trị là mật khẩu đăng nhập đã được lưu trong cơ sở dữ liệu
    :param on_success_calback: giá trị trả về là id người dùng khi đăng nhập thành công, dùng để thưucj hiện các thao tác tiếp
    :return: Trả về id người dùng trong hàm 'on_success_callback()', nếu không thì thông báo lỗi.
    """
    u = entry_user.get().strip()
    p = entry_password.get().strip()
    values = (u, p)
    db = connect_database()

    if db:
        cursor = db.cursor()
        try:
            query = 'SELECT * FROM giangvien WHERE MaCB = %s AND MatKhau = %s'
            cursor.execute(query, values)

            result = cursor.fetchone()
            if result:
                msg = CTkMessagebox(title='Phần mềm xin chào', message="Đăng nhập thành công!", icon="check", option_1="Tiếp tục")
                if msg.get() == "Tiếp tục" and result:
                    on_success_calback(u)
            else:
                CTkMessagebox(title='Thông báo lỗi!', message="Thất bại! Mã cán bộ hoặc mật khẩu sai", icon="cancel", option_1="Thử lại")
        except Error as e:
            CTkMessagebox(title='Thông báo lỗi!', message=f"Lỗi trong quá trình thực thi! \nError: {e}", icon="cancel", option_1="Thử lại")

def get_username(user_id):
    """
    Phương thức lấy tên người dùng hiển thị lên giao diện phần mềm
    :param user_id: Biến lưu trữ id, khi đăng nhập để lấy tên theo id trong cơ sở dữ liệu
    :return: Trả về kết quả là chuỗi tên người dùng, nếu không là 'Unknown' - không xác định
    """
    db = connect_database()
    if db:
        cursor = db.cursor()
        try:
            query = 'SELECT HoTen FROM giangvien WHERE MaCB = %s'
            cursor.execute(query, (user_id,))
            user_name = cursor.fetchone()
            return user_name[0] if user_name else 'Ẩn danh'
        except Error as e:
            print(f"Lỗi truy vấn get_username: {e}")
            CTkMessagebox(message="Lỗi truy xuất người dùng, vui lòng đăng nhập lại", icon="cancel", option_1="OK")
            return "Không tìm thấy tên USER"
        finally:
            cursor.close()
            db.close()
    return 'Không kết nối được cơ sở dữ liệu'

def get_class(user_id, all_class_name):
    """
    Phương thức lấy danh sách tên các lớp dựa vào id đã đăng nhập và lớp đã chọn
    :param user_id: Biến lưu trữ giá trị là id người dùng đã đnawg nhập thành công
    :param all_class_name: Tham số có giá trị mặc định (True/False) dùng để thay đổi các lấy dữ liệu theo 2 trường hợp, là lấy theo id đã đăng nhập hoặc lấy tất cả (dùng cho đăng nhập admin)
    :return:Trả về là danh sách tên các lớp, nếu không là rỗng
    """

    listclass = []
    db = connect_database()
    if db:
        cursor = db.cursor()
        if all_class_name:
            try:
                query = "SELECT DISTINCT MaLop FROM phancong WHERE MaCB = %s"
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                for row in rows:
                    listclass.append(row[0])  # Lưu mã lớp vào danh sách
                # if listclass:
                #     class_id = listclass[0]
                return listclass
            except Error as e:
                print(f"Lỗi truy vấn get_class: {e}")
                return []
            finally:
                cursor.close()
                db.close()
        else:
            try:
                query = "SELECT * FROM lop"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    listclass.append(row[0])  # Lưu mã lớp vào danh sách
                # if listclass:
                #     class_id = listclass[0]
                return listclass
            except Error as e:
                print(f"Lỗi truy vấn get_class: {e}")
                return []
            finally:
                cursor.close()
                db.close()
    return []

def get_subject(list_box, user_id, class_id):
    """
    Phương thức lấy tên các môn học dựa vào id cán bộ, lấy theo các môn mà cán bộ đnag giảng dạy
    :param list_box: Tham số truyền vào là 1 dạng ListBox được định sẵn trên giao diện
    :param user_id: Tham số truyền vào là id đã được đăng nhập thành công từ trước
    :param class_id: Thanh số nhận giá trị lớp đã chọn trên giao diện
    :return: Trả về danh sách các môn học trên ListBox, nếu không là danh sách rỗng
    """
    if not list_box is None:
        list_box.delete(0, "END")
    db = connect_database()
    value = (user_id, class_id)
    if db:
        cursor = db.cursor()
        try:
            query = """
                SELECT DISTINCT hp.TenHP 
                FROM hocphan hp 
                JOIN phancong pc ON hp.MaHP = pc.MaHP 
                JOIN lop l ON pc.MaLop = l.MaLop
                WHERE pc.MaCB = %s AND pc.MaLop = %s;
            """
            cursor.execute(query, value)
            rows = cursor.fetchall()
            for index, row in enumerate(rows):
                list_box.insert(index, row[0])
        except Error as e:
            print(f"Lỗi truy vấn get_subject: {e}")
        finally:
            cursor.close()
            db.close()

def get_lesson(list_box_lesson, user_id, class_id, subject):
    """
    Lấy thông tin tiết học dựa trên thông tin người dùng, lớp và môn học chỉ định.

    Thực hiện truy vấn cơ sở dữ liệu để lấy danh sách các tiết học của giảng viên cho môn học
    với mã người dùng và lớp, sau đó cập nhật danh sách tiết và ngày học vào list_box thích hợp.

    :param list_box_lesson: Danh sách để hiển thị tiết học.
    :param user_id: Mã người dùng ký hiệu giảng viên.
    :param class_id: Mã lớp học được chỉ định.
    :param subject: Tên môn học cần lấy thông tin các tiết học.
    :return: Không trả về giá trị nào. Cập nhật trực tiếp vào list_box_lesson và list_box_date.
    """
    list_box_lesson.delete(0, 'end')
    values = (user_id, class_id, subject)
    db = connect_database()
    if db:
        cursor = db.cursor()
        try:
            query = """
                SELECT DISTINCT tiet.TenTiet
                FROM tiet
                JOIN phancong ON tiet.MaTiet = phancong.MaTiet
                JOIN giangvien ON phancong.MaCB = giangvien.MaCB
                JOIN lop ON phancong.MaLop = lop.MaLop
                JOIN hocphan ON phancong.MaHP = hocphan.MaHP
                WHERE giangvien.MaCB = %s AND lop.MaLop = %s AND hocphan.TenHP = %s;
            """
            cursor.execute(query, values)
            rows = cursor.fetchall()
            for index, row in enumerate(rows):
                list_box_lesson.insert(index, row[0])
        except Error as e:
            print(f"Lỗi truy vấn get_lesson: {e}")
        finally:
            cursor.close()
            if db is not None:
                db.close()

def get_schedule_date(list_box_date,  user_id, class_id, subject):
    """
    Lấy lịch học từ cơ sở dữ liệu dựa trên ID người dùng, ID lớp học và môn học chỉ định, sau đó hiển thị kết quả vào list box đã cung cấp.

    :param list_box_date: ListBox dùng để hiển thị danh sách ngày học.
    :param user_id: ID người dùng, thể hiện mã cán bộ giảng viên (str).
    :param class_id: ID lớp học, thể hiện mã lớp (str).
    :param subject: Tên của môn học cần tra cứu (str).
    :return: Không có giá trị trả về.
    """
    list_box_date.delete(0, 'end')
    values = (user_id, class_id, subject)
    db = connect_database()
    if db:
        cursor = db.cursor()
        try:
            query = """
                   SELECT DISTINCT phancong.NgayHoc
                   FROM tiet
                   JOIN phancong ON tiet.MaTiet = phancong.MaTiet
                   JOIN giangvien ON phancong.MaCB = giangvien.MaCB
                   JOIN lop ON phancong.MaLop = lop.MaLop
                   JOIN hocphan ON phancong.MaHP = hocphan.MaHP
                   WHERE giangvien.MaCB = %s AND lop.MaLop = %s AND hocphan.TenHP = %s
                   ORDER BY phancong.NgayHoc DESC;
               """
            cursor.execute(query, values)
            rows = cursor.fetchall()
            for index, row in enumerate(rows):
                list_box_date.insert(index, row[0].strftime("%d-%m-%Y"))
        except Error as e:
            print(f"Lỗi truy vấn get_lesson: {e}")
        finally:
            cursor.close()
            if db is not None:
                db.close()

def get_list_student(user_id, class_id, select_of_user_id):
    """
    Phương thức lấy danh sách các sinh viên của 1 lớp, nhằm report một giao diện cho cán bộ nếu một xem danh sách lớp đó.
    :param user_id: Tham số truyền vào là id của cán bộ đã đăng nhập
    :param class_id:Tham số truyền vào là id của lớp đã được chọn từ trước
    :param select_of_user_id: Tham số mặc định (True/False) dùng để mặc định thể hiện danh sách trong trường hợp admin đăng nhập và xem danh sách tất cả sinh viên
    :return: Trả về là 1 danh sách sinh viên có gồm Mã số và Tên, nếu không là rỗng
    """
    lststudent = []
    db = connect_database()
    if db:
        cursor = db.cursor()
        if select_of_user_id:
            try:
                query = """
                SELECT distinct MaSV, HoTenSV 
                FROM sinhvien sv 
                JOIN lop l ON sv.MaLop = l.MaLop 
                JOIN phancong pc ON l.MaLop = pc.MaLop
                WHERE pc.MaCB = %s AND pc.MaLop = %s
                """
                cursor.execute(query, (user_id, class_id))
                rows = cursor.fetchall()
                for row in rows:
                    lststudent.append(row)
                return lststudent
            except Error as e:
                print(f"Lỗi truy vấn get_list_student: {e}")
                return []
            finally:
                cursor.close()
                db.close()
        else:
            try:
                query = "SELECT MaSV, HoTenSV FROM sinhvien sv JOIN lop l ON sv.MaLop = l.MaLop WHERE l.MaLop = %s"
                cursor.execute(query, (class_id,))
                rows = cursor.fetchall()
                for row in rows:
                    lststudent.append(row)
                return lststudent
            except Error as e:
                print(f"Lỗi truy vấn get_list_student: {e}")
                return []
            finally:
                cursor.close()
                db.close()
    return []

def check_diemdanh(user_id, class_id, subject, lesson, schedule_date):
    """
    Phương thức thực hiện truy vấn xem các dữ liệu có khớp với cơ sở dữ liệu trước khi thực hiện điểm danh.
    :param user_id: Tham số truyền id cán bộ
    :param class_id: Tham só truyền id của lớp
    :param subject: Tham số truyền vào môn học được chọn
    :param lesson: Tham số truyền vào tiết học được chọn
    :param schedule_date: Tham số truyền vào ngày học được chọn
    :return: Trả về là giá trị True nếu khớp dữ liệu, hoặc Flase nếu dữ liệu không đúng hoặc không có trong cở sở dữ liệu. Đồng thời trả về mã Phân công, là mã của bảng lưu trữ phân công điểm danh đã được lưu nếu khớp dữ liệu.
    """
    db = connect_database()
    date_format = datetime.datetime.strptime(schedule_date, "%d-%m-%Y")
    values = (class_id, user_id, lesson, subject, date_format.strftime("%Y-%m-%d"))
    if db:
        cursor = db.cursor()
        try:
            query = (
                """
                SELECT phancong.MaPC
                FROM phancong
                JOIN lop ON phancong.MaLop = lop.MaLop
                JOIN giangvien ON phancong.MaCB = giangvien.MaCB
                JOIN tiet ON phancong.MaTiet = tiet.MaTiet
                JOIN hocphan ON phancong.MaHP = hocphan.MaHP
                WHERE lop.MaLop = %s
                  AND giangvien.MaCB = %s
                  AND tiet.TenTiet = %s
                  AND hocphan.TenHP = %s
                  AND phancong.NgayHoc = %s;
                """
            )

            cursor.execute(query, values)

            row = cursor.fetchone()
            if not row:
                CTkMessagebox(
                    title='Cảnh báo dữ liệu',
                    message='Yêu cầu chọn đúng các thông tin hợp lệ (Gợi ý: Kiểm tra lại các thông tin rồi nhấn kiểm tra!)',
                    icon="cancel",
                    option_1="Đã hiểu"
                )
                return False, None
            else:
                return True, row[0]
        except Error as e:
            print(f"[ERROR] Lỗi thực hiện: {e}")
            return False, None
        finally:
            cursor.close()
            db.close()

def get_name_student(class_id, student_id):
    """
    Phương thức lấy tên của sinh viên, nhằm hiển thị tên và lấy tên để lưu trữ điểm danh.
    :param class_id: Tham số nhận được của lớp được chọn điểm danh
    :param student_id: Tham số nhận được khi phân tích file lưu trữ, là một mã sinh viên được thiết kết lưu trữ từ trước
    :return: Trả về là chuỗi tên sinh viên, nếu không là rỗng
    """
    db = connect_database()
    values = (student_id, class_id)
    try:
        if db:
            cursor = db.cursor()
            query = """
                SELECT HoTenSV
                FROM sinhvien
                WHERE MaSV = %s
                    AND MaLop = %s
                """
            cursor.execute(query, values)
            name = cursor.fetchall()
            if name:
                return name[0][0] if name else "unknown"
            else:
                return "unknown"
        else:
            return None
    except Error as e:
        print(f"Lỗi khi lấy tên sinh viên: {e}")
        return None
    finally:
        if db:
            db.close()

def insert_attendance_check( id_of_assignment, id_of_student):
    """
    Phương thức thêm sinh viên được nhận diện thành công vào cơ sở dữ liệu.
    :param id_of_assignment: Tham số truyền vào là mã bảng phân công được truy vấn từ phương thức 'chechk_diemdanh()'
    :param id_of_student: Tham số truyền vào là id của sinh viên được nhận diện thành công
    :return: Trả về thông báo thêm thành công nếu sinh viên chưa điểm danh, ngược lại thông báo sinh viên đã điểm danh rồi.
    """
    db = connect_database()
    time_now = datetime.datetime.now()
    time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
    if db:
        cursor = db.cursor()
        try:
            query_check = """
            SELECT ThoiGianDiemDanh
            FROM diemdanh 
            WHERE MaPC = %s 
              AND MaSV = %s 
              AND DATE(ThoiGianDiemDanh) = DATE(%s)
              AND TIMESTAMPDIFF(HOUR, ThoiGianDiemDanh, %s) < 2
            """
            cursor.execute(query_check, (id_of_assignment, id_of_student, time_now, time_now))
            existing_record = cursor.fetchone()

            if existing_record:
                print("[Warning] Sinh viên đã điểm danh trong môn học này trong vòng 2 giờ qua.")
                return False

            query = """
                INSERT INTO diemdanh(MaPC, MaSV, ThoiGianDiemDanh)
                VALUES (%s, %s, %s)
                """
            values = (id_of_assignment, id_of_student, time_now)
            cursor.execute(query, values)
            db.commit()
            print(f"[INSERT TO DATABASE COMPLETE] [ID: {id_of_assignment}, STUDENT: {id_of_student}]")
            return True
        except Error as e:
            print(f"[ERROR] Lỗi khi thêm điểm danh: {e}")
        finally:
            cursor.close()
            db.close()

def get_attendance_report_of_day(class_id, user_id, subject, lesson, schedule_date):
    """
    Truy xuất danh sách sinh viên đã điểm danh của một ngày cụ thể trong một lớp học,
    cùng với thông tin chi tiết về sinh viên và thời gian điểm danh.

    :param class_id: Mã định danh lớp học được sử dụng trong truy vấn dữ liệu.
    :param user_id: Mã định danh của người dùng (giảng viên) thực hiện yêu cầu truy xuất.
    :param subject: Tên môn học liên kết với lớp học cần lấy thông tin điểm danh.
    :param lesson: Tên tiết học cụ thể cần truy vấn dữ liệu.
    :param schedule_date: Ngày học của lớp, sử dụng định dạng "dd-mm-yyyy".
    :return: Danh sách các sinh viên đã được điểm danh cùng với thông tin cần thiết
             (mã số sinh viên, họ tên sinh viên, và thời gian điểm danh).
    """
    db = connect_database()
    date_format = datetime.datetime.strptime(schedule_date, "%d-%m-%Y")
    list_student = []
    if db:
        cursor = db.cursor()
        try:
            query = """
                 SELECT sv.MaSV,
                       sv.HoTenSV,
                       dd.ThoiGianDiemDanh
                FROM diemdanh dd
                JOIN sinhvien sv ON dd.MaSV = sv.MaSV
                JOIN lop l on sv.MaLop = l.MaLop
                JOIN phancong pc ON l.MaLop = pc.MaLop
                JOIN hocphan hp ON pc.MaHP = hp.MaHP
                JOIN tiet t ON pc.MaTiet = t.MaTiet
                WHERE pc.NgayHoc = %s
                  AND pc.MaCB = %s
                  AND t.TenTiet = %s
                  AND pc.MaLop = %s
                  AND hp.TenHP = %s
                  AND dd.MaPC = pc.MaPC;
            """
            # # Kiểm tra các tham số
            # print(f"Parameters: {date_format.strftime('%Y-%m-%d')}, {user_id}, {lesson}, {class_id}, {subject}")

            cursor.execute(query, (date_format.strftime("%Y-%m-%d"), user_id, lesson, class_id, subject))

            rows = cursor.fetchall()
            for row in rows:
                list_student.append(row)
            return list_student
        except Error as e:
            print(f"[ERROR] Không thể lấy thông tin đã điểm danh: {e}")
            return []
        finally:
            cursor.close()
            db.close()

def get_attendance_report_of_subject(user_id, subject):
    """
    Lấy báo cáo điểm danh của một môn học cụ thể dựa trên ID của người dùng và tên môn học.

    Báo cáo trả về danh sách sinh viên kèm theo số ngày học và số ngày điểm danh đã tham gia
    trong môn học cụ thể. Chức năng này thực hiện các thao tác trên cơ sở dữ liệu để truy xuất
    và tính toán thông tin cần thiết.

    :param user_id: ID của người dùng thuộc kiểu dữ liệu phù hợp với cơ sở dữ liệu, ví dụ: chuỗi hoặc số.
    :param subject: Tên của môn học, là một chuỗi thể hiện tên môn học cần lấy báo cáo.
    :return: Danh sách các sinh viên được biểu diễn qua các dòng chứa thông tin của mỗi sinh viên
        bao gồm mã sinh viên, họ tên, số ngày học và số ngày đã điểm danh. Nếu xảy ra lỗi hoặc không
        có dữ liệu, sẽ trả về danh sách rỗng.
    """
    db = connect_database()
    values = (user_id, subject)
    list_student = []
    if db:
        cursor = db.cursor()
        try:
          query = """
                SELECT 
                    sv.MaSV, 
                    sv.HoTenSV,
                    COUNT(DISTINCT pc.NgayHoc) AS SoNgayHoc,
                    COUNT(DISTINCT dd.ThoiGianDiemDanh) AS SoNgayDiemDanh
                FROM sinhvien sv
                JOIN lop l ON sv.MaLop = l.MaLop
                JOIN phancong pc ON l.MaLop = pc.MaLop
                LEFT JOIN diemdanh dd ON sv.MaSV = dd.MaSV AND pc.MaPC = dd.MaPC
                JOIN hocphan hp ON pc.MaHP = hp.MaHP
                WHERE pc.MaCB = %s
                AND hp.TenHP = %s
                GROUP BY sv.MaSV, sv.HoTenSV
                ORDER BY sv.MaSV;
          """
          cursor.execute(query, values)
          rows = cursor.fetchall()
          for row in rows:
              list_student.append(row)
          return list_student
        except Error as e:
            print(f"[REPORT FAILED] Lỗi: {e}]")
            return []
        finally:
            cursor.close()
            db.close()
    return []

def del_attendance(student_id, schedule_date):
    db = connect_database()
    values = (student_id, schedule_date)

    if db:
        cursor = db.cursor()
        try:
            query = "DELETE FROM diemdanh WHERE MaSV = %s AND ThoiGianDiemDanh = %s;"
            cursor.execute(query, values)
            db.commit()

            if cursor.rowcount > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"[DELETE FAILED] Lỗi: {e}")
            return False
        finally:
            cursor.close()
            db.close()
    return False

if __name__ == "__main__":
    get_list_student("012345", "22TINTT", True)