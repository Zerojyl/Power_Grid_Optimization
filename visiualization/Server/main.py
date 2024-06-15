from flask import Flask, Response
from flask_cors import CORS
import json
import time, os

app = Flask(__name__)
CORS(app)  # 添加这一行来启用 CORS
data_source = "data.json"


@app.route('/')
def index():
    return "Server is running"


@app.route('/data')
def events():
    return Response(stream_data(), content_type='text/event-stream')


def stream_data():
    with open(data_source, "r") as file:
        data = json.load(file)
        yield "data: {}\n\n".format(json.dumps(data))
    last_modified = os.path.getmtime(data_source)
    while True:
        current_modified = os.path.getmtime(data_source)
        if current_modified > last_modified:
            with open(data_source, "r") as file:
                data = json.load(file)
                yield "data: {}\n\n".format(json.dumps(data))
            last_modified = current_modified
        time.sleep(1)



if __name__ == '__main__':
    app.run(debug=True)

