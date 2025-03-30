import mysql.connector


def connect_database():
    """
    Kết nối đến cơ sở dữ liệu và trả về kết nối nếu thực hiện thành công.
    Nếu có lỗi xảy ra, hiển thị thông báo lỗi và trả về None.

    :return: Đối tượng kết nối đến cơ sở dữ liệu hoặc None nếu xảy ra lỗi.
    :rtype: Optional[mysql.connector.connection.MySQLConnection]
    """
    try:
        db = mysql.connector.connection.MySQLConnection(
            host='127.0.0.1',
            user='root',
            password='12345678',
            database='quanlydiemdanh'
        )
        return db
    except Error as e:
        print(f"[CODE ERROR] {e}")
        return None
