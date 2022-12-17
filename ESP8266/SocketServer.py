import socket
import time 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 8585 ))
s.listen(0)                 
 
while True:
    client, addr = s.accept()
    client.settimeout(5)
    # nếu mở gửi 1 , đóng gửi 0
    if 1: 
       client.send(b'1')
    else:
       client.send(b'0')  
    client.close()   
