import socket
import threading
import tkinter as tk
from tkinter import messagebox

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
        clients.remove(client_socket)
        client_socket.close()
        del client_usernames[client_socket]
        del chats[username]
        update_client_list()  # Cập nhật lại danh sách client khi có client ngắt kết nối
        broadcast_message(username, f"{username} đã rời khỏi phòng chat.")
    
# Phát tin nhắn cho tất cả các client
def broadcast_message(username, message):
    for client in clients:
        try:
            client.send(f"{username}: {message}".encode())
            # Lưu tin nhắn vào đoạn chat
            if username in client_usernames.values():
                chats[username].append(f"{username}: {message}")
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
        client_list_box.insert(tk.END, f"{username}")

# Giao diện quản lý server
def server_gui():
    server_window = tk.Tk()
    server_window.title("Giao diện Server")
    server_window.geometry("500x400")

    # Hiển thị khu vực chat
    global server_chat_area
    server_chat_area = tk.Text(server_window, height=10, width=60)
    server_chat_area.pack(pady=10)

    # Danh sách các client
    global client_list_box
    client_list_box = tk.Listbox(server_window, height=10, width=50)
    client_list_box.pack(pady=10)

    # Nhập tin nhắn admin
    admin_message_entry = tk.Entry(server_window, width=50)
    admin_message_entry.pack(pady=5)

    # Nút gửi tin nhắn admin
    def send_admin_msg():
        message = admin_message_entry.get()
        if message:
            send_admin_message(message)
            admin_message_entry.delete(0, tk.END)
            server_chat_area.insert(tk.END, f"Admin: {message}\n")
            server_chat_area.yview(tk.END)

    send_button = tk.Button(server_window, text="Gửi tin nhắn admin", command=send_admin_msg)
    send_button.pack(pady=5)

    # Nút shutdown server
    def shutdown_server():
        for client in clients:
            client.send("Server đang đóng...".encode())
            client.close()
        server_window.quit()
        server_window.destroy()

    shutdown_button = tk.Button(server_window, text="Đóng server", command=shutdown_server)
    shutdown_button.pack(pady=10)

    # Cập nhật danh sách client ban đầu
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
    threading.Thread(target=start_server).start()
    # Chạy giao diện server
    server_gui()
