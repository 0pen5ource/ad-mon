import math
import time

from flask import Flask, request, render_template
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)


@app.route('/')
def index():
    return render_template('index.html')

@sock.route('/echo')
def echo(sock):
    while True:
        if len(dispatch):
            # count = dispatch.pop(0)
            avg = sum(dispatch)/len(dispatch)
            dispatch.clear()
            sock.send(str(math.floor(avg)))
        time.sleep(1)

dispatch = []

@app.route('/sensor', methods=['POST'])
def sensor():
    global dispatch
    content = request.json
    count = content['count']
    print(count)
    #if len(dispatch) and dispatch[-1] != count:
    dispatch.append(count)
    return 'ok'



app.run()