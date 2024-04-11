import socket
import select

HOST = '0.0.0.0'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

clients_list = []
clients_details = {}

def broadcast_message(message, channel, sender_socket=None):
    for client_socket in clients_details:
        if clients_details[client_socket]['channel'] == channel and client_socket != sender_socket:
            try:
                client_socket.send(message.encode())
            except:
                client_socket.close()
                clients_list.remove(client_socket)
                del clients_details[client_socket]

def private_message(message, nickname, sender_socket):
    found = False
    for client_socket in clients_details:
        if clients_details[client_socket]['nickname'] == nickname:
            try:
                client_socket.send(message.encode())
                found = True
            except:
                client_socket.close()
                clients_list.remove(client_socket)
                del clients_details[client_socket]
    if not found:
        sender_socket.send(f"User {nickname} not found.".encode())

def handle_client_message(client_socket, message):
    if message.strip() == "/quit":
        # Prepare and send a farewell message
        farewell_message = f"{clients_details[client_socket]['nickname']} has left the chat."
        broadcast_message(farewell_message, clients_details[client_socket]['channel'], sender_socket=client_socket)
        client_socket.send("You are now disconnected from the server.".encode())

        # Close the client socket and clean up
        client_socket.close()
        clients_list.remove(client_socket)
        del clients_details[client_socket]
        return

    tokens = message.split()
    command = tokens[0]
    if command == "/nick":
        old_nickname = clients_details[client_socket]['nickname']
        new_nickname = tokens[1]
        clients_details[client_socket]['nickname'] = new_nickname
        broadcast_message(f"{old_nickname} changed nickname to {new_nickname}", clients_details[client_socket]['channel'])
    elif command == "/join":
        old_channel = clients_details[client_socket]['channel']
        new_channel = tokens[1]
        clients_details[client_socket]['channel'] = new_channel
        broadcast_message(f"{clients_details[client_socket]['nickname']} left the channel", old_channel)
        broadcast_message(f"{clients_details[client_socket]['nickname']} joined the channel", new_channel)
    elif command == "/msg":
        receiver = tokens[1]
        actual_message = ' '.join(tokens[2:])
        formatted_message = f"Private from {clients_details[client_socket]['nickname']}: {actual_message}"
        private_message(formatted_message, receiver, client_socket)
    else:
        channel = clients_details[client_socket]['channel']
        formatted_message = f"{clients_details[client_socket]['nickname']}: {message}"
        broadcast_message(formatted_message, channel, client_socket)

print("Chat server started on port " + str(PORT))

while True:
    read_sockets, _, _ = select.select([server_socket] + clients_list, [], [])
    for sock in read_sockets:
        if sock == server_socket:
            sockfd, addr = server_socket.accept()
            clients_list.append(sockfd)
            clients_details[sockfd] = {'nickname': 'Guest', 'channel': 'general'}
            sockfd.send("Welcome to the chat server! Set your nickname with /nick <name>".encode())
            print(f"New connection from {addr}")
        else:
            try:
                data = sock.recv(4096).decode().strip()
                if data:
                    handle_client_message(sock, data)
                else:
                    if sock in clients_list:
                        clients_list.remove(sock)
                        del clients_details[sock]
            except Exception as e:
                print(f"Error: {e}")
                continue

server_socket.close()
