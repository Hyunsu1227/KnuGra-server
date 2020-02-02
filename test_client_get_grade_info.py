import argparse
import json
import socket
import threading

clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSock.connect(('127.0.0.1', 4567))

print('연결 확인 됐습니다.')

dic = {'requestType':"getGradeInfo","id":"","major":"abeek"}
jsonstr = json.dumps(dic)
print(jsonstr)
clientSock.send(jsonstr.encode())

print('메시지를 전송했습니다.')

data = clientSock.recv(4096)
print('받은 데이터 : ', data, type(data))