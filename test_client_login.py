import argparse
import json
import socket
import threading

clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect(('127.0.0.1', 3456))

print('연결 확인 됐습니다.')

dic = {'requestType':"login","id":"", "pwd":""}
jsonstr = json.dumps(dic)
print(jsonstr)
clientSock.send(jsonstr.encode())

print('메시지를 전송했습니다.')

data = clientSock.recv(1024)
print('받은 데이터 : ', data, type(data))