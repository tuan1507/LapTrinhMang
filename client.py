import socket
import tkinter as tk
from tkinter import messagebox
import threading

# Cấu hình kết nối server
host = '127.0.0.1'
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tên người dùng toàn cục, gán sau khi đăng nhập thành công
username = None

# Kết nối tới server và gửi tên người dùng và mật khẩu
def connect_to_server(username, password):
    client_socket.connect((host, port))
    client_socket.send(f"{username},{password}".encode())  # Gửi cả tên và mật khẩu
    receive_thread = threading.Thread(target=receive_message)
    receive_thread.start()

# Nhận tin nhắn từ server và hiển thị trong giao diện
def receive_message():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            chat_area.insert(tk.END, message + '\n')
            chat_area.yview(tk.END)
        except:
            break

# Gửi tin nhắn cho server
def send_message():
    message = message_entry.get()
    if message:
        client_socket.send(message.encode())
        message_entry.delete(0, tk.END)

# Giao diện Chat
def chat_window():
    global username  # Chắc chắn rằng sử dụng biến toàn cục

    # Giao diện chính của ứng dụng chat
    chat_root = tk.Tk()  # Khởi tạo lại cửa sổ chat
    chat_root.title(f"Chào mừng {username}")  # Hiển thị tên người dùng
    chat_root.geometry("500x500")

    # Hiển thị khu vực chat
    global chat_area
    chat_area = tk.Text(chat_root, height=20, width=60)
    chat_area.pack(pady=10)

    # Ô nhập tin nhắn
    global message_entry
    message_entry = tk.Entry(chat_root, width=50)
    message_entry.pack(pady=10)

    send_button = tk.Button(chat_root, text="Gửi", command=send_message)
    send_button.pack(pady=5)

    # Bắt đầu nhận và gửi tin nhắn
    message_entry.focus()
    chat_root.mainloop()

# Kiểm tra và lưu thông tin đăng ký vào file
def register_user(username, password):
    try:
        with open('accounts.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                stored_username = line.split(',')[0].strip()
                if stored_username == username:
                    messagebox.showwarning("Cảnh báo", "Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")
                    return False  # Trả về False nếu tên người dùng đã tồn tại
    except FileNotFoundError:
        pass  # Nếu file không tồn tại, không làm gì cả

    # Nếu tên người dùng chưa tồn tại, lưu thông tin vào file
    with open('accounts.txt', 'a') as file:
        file.write(f"{username},{password}\n")

    messagebox.showinfo("Thông báo", "Đăng ký thành công! Vui lòng đăng nhập.")
    return True

# Giao diện đăng ký và đăng nhập
def login_register_gui():
    def handle_register():
        global username  # Chắc chắn rằng sử dụng biến toàn cục

        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            if register_user(username, password):
                # Nếu đăng ký thành công, chuyển sang giao diện chat
                login_win.quit()  # Đóng cửa sổ đăng nhập và mở giao diện chat
                connect_to_server(username, password)
                chat_window()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")

    def handle_login():
        global username  # Chắc chắn rằng sử dụng biến toàn cục

        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            connect_to_server(username, password)
            login_win.quit()  # Đóng cửa sổ đăng nhập và mở giao diện chat
            chat_window()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên người dùng và mật khẩu.")

    login_win = tk.Tk()
    login_win.title("Đăng ký / Đăng nhập")
    login_win.geometry("300x300")

    tk.Label(login_win, text="Tên người dùng:").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Mật khẩu:").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    register_button = tk.Button(login_win, text="Đăng ký", command=handle_register)
    register_button.pack(pady=10)

    login_button = tk.Button(login_win, text="Đăng nhập", command=handle_login)
    login_button.pack(pady=10)

    login_win.mainloop()

# Chạy giao diện đăng ký và đăng nhập
login_register_gui()