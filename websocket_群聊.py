from flask import Flask,request,render_template,jsonify,send_file
from geventwebsocket.websocket import WebSocket
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import json
app=Flask(__name__)
@app.route('/',strict_slashes='/')
def home():
    return render_template('ws交互.html')


#设置在线用户名单列表
user_socket_dict={}

#获取客户端用户名
@app.route('/ws/<username>',strict_slashes=False)
def ws(username):
    #连接循环
    while True:
        #获取链接对象
        user_socket=request.environ.get('wsgi.websocket') #type:WebSocket
        if user_socket==None:
            return "不要给我发http请求了，发websocket请求！！！"
        #是websocket请求则添加到用户在线用户字典中
        user_socket_dict[username]=user_socket
        #通信循环
        while True:
            try:
                #接收客户端消息
                user_msg = user_socket.receive()
                #循环在线用户字典
                for user,socket_conn in user_socket_dict.items():
                    #构造数据结构
                    who_send_msg={
                        "send_user":username,
                        "send_msg":user_msg
                    }
                    #如果当前发消息的客户端与循环匹配上，则直接跳过，不给该用户发消息
                    if user_socket==socket_conn:
                        continue
                    #给其他在线客户端都发送该消息
                    socket_conn.send(json.dumps(who_send_msg))
            except Exception as a:
                #清除该客户端链接
                user_socket_dict.pop(username)
                break

if __name__ == '__main__':
    http_server=WSGIServer(('0.0.0.0',8000),app,handler_class=WebSocketHandler)
    http_server.serve_forever()
