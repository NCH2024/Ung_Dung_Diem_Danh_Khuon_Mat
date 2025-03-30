from tkinter import *
import pandas as pd
from config.data.get_data import *
from customtkinter import *

class ReportOfSubject:
    def __init__(self, user_id, class_id, subject, lesson, schedule_date, main_ui):
        self.user_id = user_id
        self.class_id = class_id
        self.subject = subject
        self.lesson = lesson
        self.schedule_date = schedule_date
        self.main_ui = main_ui


        self.report_window = Toplevel()
        self.report_window.geometry("500x220")
        self.report_window.attributes("-topmost", TRUE)
        self.report_window.attributes("-toolwindow", TRUE)

        CTkLabel(master=self.report_window,
                 text=f"Xuất báo cáo học phần: {self.subject}.",
                 font=("Open sans", 16, "italic"),
                 text_color="black",
                 height=20).place(x=15, y=20)

        CTkLabel(master=self.report_window,
                 text="Đường dẫn lưu báo cáo:",
                 font=("Open sans", 15, "bold"),
                 text_color="blue",
                 height=20).place(x=15, y=50)
        self.entry_path = CTkEntry(master=self.report_window,
                                   placeholder_text="Chọn đường dẫn lưu file...",
                                   font=("Open sans", 13, "italic"),
                                   width=320,
                                   text_color='black',
                                   fg_color='light gray',
                                   height=30)
        self.entry_path.place(x=15, y=100)
        self.btn_select_path = CTkButton(master=self.report_window,
                                         text="Chọn thư mục",
                                         text_color="white",
                                         fg_color="blue",
                                         font=("Open sans", 15, "bold"),
                                         height=30,
                                         width=120,
                                         command=self.select_path)
        self.btn_select_path.place(x=350, y=100)
        self.btn_save = CTkButton(master=self.report_window,
                                         text="Xuất báo cáo",
                                         text_color="white",
                                         fg_color="light green",
                                         font=("Open sans", 15, "bold"),
                                         height=30,
                                         width=320,
                                  command=self.import_data)
        self.btn_save.place(x=15, y=150)
        self.btn_cancel = CTkButton(master=self.report_window,
                                  text="Thoát",
                                  text_color="white",
                                  fg_color="red",
                                  font=("Open sans", 15, "bold"),
                                  height=30,
                                  width=120,
                                    command=self.cancel_report)
        self.btn_cancel.place(x=350, y=150)

    def cancel_report(self):
        self.report_window.destroy()

    def select_path(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx"),
                                                       ("All files", "*.*")])
        if path:
            self.entry_path.delete(0, END)
            self.entry_path.insert(0, path)
            print(f"[FILE PATH SAVE] Đường dẫn được chọn: {path}")

    def get_data_of_subject(self):
        data = get_attendance_report_of_subject(self.user_id, self.subject)
        if not data:
            return pd.DataFrame()
        data_format = {
            'STT': [],
            'MÃ SINH VIÊN': [],
            'HỌ VÀ TÊN': [],
            'SỐ NGÀY HỌC': [],
            'SỐ NGÀY ĐIỂM DANH': []
        }
        for index, row in enumerate(data):
            data_format['STT'].append(index + 1)
            data_format['MÃ SINH VIÊN'].append(row[0])
            data_format['HỌ VÀ TÊN'].append(row[1])
            data_format['SỐ NGÀY HỌC'].append(row[2])
            data_format['SỐ NGÀY ĐIỂM DANH'].append(row[3])
        return pd.DataFrame(data_format)

    def import_data(self):
        df = self.get_data_of_subject()
        if df is not None and not df.empty:
            with pd.ExcelWriter(self.entry_path.get(), engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=f'DiemDanh{self.class_id}', startrow=4, index=False)

                workbook = writer.book
                worksheet = writer.sheets[f'DiemDanh{self.class_id}']

                num_cols = len(df.columns)
                end_col_letter = chr(65 + num_cols - 1)

                merge_range = f'A1:{end_col_letter}1'
                title_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 15,
                    'font_name': 'Times New Roman'
                })

                subtitle_format = workbook.add_format({
                    'bold': False,
                    'align': 'center',
                    'valign': 'vcenter',
                    'font_size': 13,
                    'font_name': 'Times New Roman'
                })
                # Gộp vùng và ghi tiêu đề chính
                worksheet.merge_range(f'A1:{end_col_letter}1', f'DANH SÁCH ĐIỂM DANH LỚP {self.class_id}', title_format)
                # Gộp vùng và ghi tiêu đề phụ
                worksheet.merge_range(f'A2:{end_col_letter}2', f'Môn: {self.subject}', subtitle_format)
                worksheet.merge_range(f'A3:{end_col_letter}3', f'Giảng viên: {get_username(self.user_id)}',
                                      subtitle_format)
                # Thiết lập độ rộng của các cột
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(),
                                  len(col)) + 2  # Độ dài tối đa của nội dung cộng thêm khoảng cách
                    worksheet.set_column(i, i, max_len)
                if CTkMessagebox(title="Thao tác thành công", message=f"Đã lưu file tại: {self.entry_path.get()}",
                                 icon="check", option_1="OK").get() == "OK":
                    self.cancel_report()
        else:
            print(f"[EMPTY DATA] Không có dữ liệu để tạo file")
