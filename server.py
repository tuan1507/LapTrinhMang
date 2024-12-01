import socket
import threading
import tkinter as tk

clients = []
client_usernames = {}
chats = {}  # Lưu trữ các đoạn chat giữa các client


# Kết nối mới từ client
def handle_client(client_socket, client_address):
    username_password = client_socket.recv(1024).decode().split(',')
    username, password = username_password[0], username_password[1]  # Tách tên và mật khẩu
    client_usernames[client_socket] = username
    clients.append(client_socket)
    chats[username] = []  # Mỗi client có một đoạn chat riêng

    update_client_list()  # Cập nhật danh sách client khi có kết nối mới

    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message:
                if message.startswith('admin:'):
                    # Gửi tin nhắn admin
                    admin_message = message.replace('admin:', '', 1)
                    send_admin_message(admin_message)
                else:
                    broadcast_message(username, message)
            else:
                break
    except:
        pass
    finally:
        # Xử lý khi client ngắt kết nối
        if client_socket in clients:
            clients.remove(client_socket)
        if username in chats:
            del chats[username]
        del client_usernames[client_socket]
        update_client_list()
        broadcast_message("Server", f"{username} đã rời khỏi phòng chat.")


# Phát tin nhắn cho tất cả các client
def broadcast_message(username, message):
    for client in clients:
        try:
            client.send(f"{username}: {message}".encode())
        except:
            clients.remove(client)
            client.close()


# Gửi tin nhắn từ admin
def send_admin_message(message):
    for client in clients:
        try:
            client.send(f"Admin: {message}".encode())
        except:
            clients.remove(client)
            client.close()


# Cập nhật danh sách client trên giao diện
def update_client_list():
    client_list_box.delete(0, tk.END)
    for client_socket in clients:
        username = client_usernames.get(client_socket, "Không xác định")
        client_list_box.insert(tk.END, username)


import tkinter as tk
from tkinter import ttk

# Giao diện quản lý server
def server_gui():
    server_window = tk.Tk()
    server_window.title("Giao diện Quản lý Server")
    server_window.geometry("600x500")  # Kích thước cố định
    server_window.configure(bg="#f5f5f5")  # Màu nền nhẹ nhàng

    # Tiêu đề chính
    main_title = tk.Label(
        server_window,
        text="Quản Lý Server Chat",
        font=("Arial", 18, "bold"),
        bg="#f5f5f5",
        fg="#333",
    )
    main_title.pack(pady=15)

    # Khung hiển thị danh sách client
    client_frame = tk.Frame(server_window, bg="#f5f5f5")
    client_frame.pack(pady=10, fill=tk.X, padx=20)

    client_title = tk.Label(
        client_frame,
        text="Danh sách các client",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#555",
    )
    client_title.pack(anchor="w")

    global client_list_box
    client_list_box = tk.Listbox(client_frame, height=8, width=40, font=("Arial", 12))
    client_list_box.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

    # Khung hiển thị khu vực chat
    chat_frame = tk.Frame(server_window, bg="#f5f5f5")
    chat_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

    chat_title = tk.Label(
        chat_frame,
        text="Nội dung Chat",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#555",
    )
    chat_title.pack(anchor="w")

    global server_chat_area
    server_chat_area = tk.Text(
    chat_frame,
    height=15,  # Chiều cao (số dòng)
    width=30,   # Chiều rộng (số ký tự)
    font=("Arial", 12),
    bg="#fff",
    fg="#333",
    relief=tk.GROOVE,
    wrap=tk.WORD,  # Tự động xuống dòng khi vượt chiều rộng
)
    server_chat_area.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
    server_chat_area.config(state=tk.DISABLED)  # Không cho phép chỉnh sửa trực tiếp

    # Khung nhập tin nhắn admin
    admin_frame = tk.Frame(server_window, bg="#f5f5f5")
    admin_frame.pack(pady=10, fill=tk.X, padx=20)

    admin_title = tk.Label(
        admin_frame,
        text="Nhập tin nhắn:",
        font=("Arial", 14, "bold"),
        bg="#f5f5f5",
        fg="#555",
    )
    admin_title.pack(anchor="w")

    admin_message_entry = tk.Entry(admin_frame, font=("Arial", 12), width=40)
    admin_message_entry.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)

    def send_admin_msg():
        message = admin_message_entry.get()
        if message:
            send_admin_message(message)
            admin_message_entry.delete(0, tk.END)
            server_chat_area.config(state=tk.NORMAL)
            server_chat_area.insert(tk.END, f"Admin: {message}\n")
            server_chat_area.config(state=tk.DISABLED)
            server_chat_area.yview(tk.END)

    send_button = tk.Button(
        admin_frame,
        text="Gửi",
        command=send_admin_msg,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12, "bold"),
        relief=tk.FLAT,
        padx=10,
        pady=5,
    )
    send_button.pack(side=tk.RIGHT, padx=10, pady=5)

    # Nút tắt server
    shutdown_button = tk.Button(
        server_window,
        text="Đóng Server",
        command=server_window.quit,
        bg="#F44336",
        fg="white",
        font=("Arial", 12, "bold"),
        relief=tk.FLAT,
        padx=10,
        pady=5,
    )
    shutdown_button.pack(pady=10)

    update_client_list()

    server_window.mainloop()



# Chạy server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(5)
    print("Server đang chờ kết nối...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Kết nối mới từ {client_address}")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()


if __name__ == "__main__":
    # Chạy server trong một thread riêng
    threading.Thread(target=start_server, daemon=True).start()
    # Chạy giao diện server
    server_gui()