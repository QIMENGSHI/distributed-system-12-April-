import socket
import select
import sys
import os  

def prompt():
    sys.stdout.write('<You> ')
    sys.stdout.flush()

# Setup server connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if 'last_ip.txt' in os.listdir():
    with open('last_ip.txt', 'r') as file:
        IP_address = file.read().strip()
else:
    IP_address = input("Enter server IP address: ")
    with open('last_ip.txt', 'w') as file:
        file.write(IP_address)

Port = 12345
server.connect((IP_address, Port))

# Print initial connection and instruction messages
print("Connected to chat server at IP " + IP_address + " on port " + str(Port))
print("Type '/nick your_nickname' to set your nickname.")
print("Join a channel with '/join channel_name'.")
print("Send private messages with '/msg recipient_nickname message'.")
print("Type your message and press Enter to send a public message to the current channel.")
print("Type '/quit' to disconnect from the server.")

while True:
    sockets_list = [sys.stdin, server]
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])
    
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048).decode()
            if message == "You are now disconnected from the server.":
                print("\n" + message)
                server.close()
                print("Connection closed. Press enter to exit...")
                input()
                sys.exit()
            else:
                print("\n" + message)
                prompt()
        else:
            message = sys.stdin.readline().strip()
            if message == "/quit":
                server.send(message.encode())
                continue
            server.send(message.encode())
            prompt()


server.close()
