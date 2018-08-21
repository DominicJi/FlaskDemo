from flask import Flask,render_template,request,jsonify
from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import json
app=Flask(__name__)

@app.route('/',strict_slashes=False)
def temp():
    return render_template('单聊.html')



user_dict={}
#获取客户端用户名
@app.route('/ws/<username>',strict_slashes=False)
def index(username):
    while True:
        user_socket=request.environ.get('wsgi.websocket') # type:WebSocket
        if user_socket==None:
            return '不要给我发http请求了,老子这里只认websocket请求'
        user_dict[username]=user_socket
        while True:
            try:
                #获取客户端数据
                user_msg=user_socket.receive()
                #序列化数据
                user_msg=json.loads(user_msg)
                #获取目标客户端的通信对象
                to_user_socket=user_dict.get(user_msg.get('to_user'))
                #构建数据结构
                send_msg={
                    "send_msg":user_msg.get('send_msg'),
                    "send_user":username
                }
                #朝目标通信对象中传入数据
                to_user_socket.send(json.dumps(send_msg))
            except Exception as a:
                user_dict.pop(username)
                break

if __name__ == '__main__':
    http_server=WSGIServer(('0.0.0.0',8000),app,handler_class=WebSocketHandler)
    http_server.serve_forever()