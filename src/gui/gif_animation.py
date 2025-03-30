import tkinter as tk
import time
from PIL import Image, ImageTk

class GifPlay:
    """
    Quản lý và phát hình ảnh động định dạng GIF.

    Lớp này cung cấp chức năng để tải, hiển thị và phát các tệp GIF trên một nhãn
    giao diện người dùng, với hỗ trợ thay đổi kích thước khung hình và kiểm soát
    hoạt động của ảnh GIF.

    :ivar label: Nhãn giao diện người dùng nơi ảnh GIF sẽ được hiển thị.
    :type label: tkinter.Label
    :ivar giffile: Đường dẫn tệp tới ảnh GIF cần hiển thị.
    :type giffile: str
    :ivar delay: Thời gian trễ giữa các khung hình, tính bằng giây.
    :type delay: float
    :ivar width: Chiều rộng mong muốn của các khung hình GIF. Mặc định là None.
    :type width: int | None
    :ivar height: Chiều cao mong muốn của các khung hình GIF. Mặc định là None.
    :type height: int | None
    :ivar frames: Danh sách các khung hình GIF đã được xử lý.
    :type frames: list[ImageTk.PhotoImage]
    :ivar current_frame: Khung hình hiện hành được hiển thị trong GIF.
    :type current_frame: int
    :ivar playing: Trạng thái hiện tại của GIF: đang chơi hoặc dừng.
    :type playing: bool
    :ivar total_frames: Tổng số khung hình trong GIF, trừ đi 1 (do chỉ mục 0).
    :type total_frames: int
    """
    def __init__(self, label, giffile, delay, width=None, height=None):
        self.label = label  # Corrected: Use self.label consistently
        self.giffile = giffile
        self.delay = delay
        self.width = width
        self.height = height
        self.frames = []
        self.current_frame = 0
        self.playing = False

        try:
            gif = Image.open(giffile)
            for frame_index in range(gif.n_frames):
                gif.seek(frame_index)
                frame = gif.convert("RGBA")

                if self.width is not None and self.height is not None:
                    frame = frame.resize((self.width, self.height), Image.LANCZOS)

                image = ImageTk.PhotoImage(frame)
                self.frames.append(image)

            self.total_frames = len(self.frames) - 1  # Corrected variable name
            self.label.config(image=self.frames[0]) # Corrected: Use self.label
            self.label.image = self.frames  # Keep a reference

        except FileNotFoundError:
            print(f"GIF file not found: {giffile}")
        except Exception as e:
            print(f"Error loading GIF: {e}")

    def play(self):
        self.playing = True
        self._animate()  # Start animation on the main thread

    def _animate(self):
        if self.playing:
            self.label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % (self.total_frames + 1)
            self.label.after(int(self.delay * 1000), self._animate)  # Use after for main thread animation

    def stop(self):
        self.playing = False
        self.label.config(image="")  # Clear the image
        self.label.image = None # Release the image from memory (important!)