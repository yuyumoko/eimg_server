import sys

from werkzeug.serving import WSGIRequestHandler
from flask import Flask, Response, abort, jsonify, request
from flask_cors import CORS
from .config import get_config
from .mem_data import get_image_cache
from .ncnn import add_routes as add_ncnn_routes

if not sys.gettrace():
    WSGIRequestHandler.log_request = lambda *args: None

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app, resources=r"/*")


@app.route("/check_md5/<md5>", methods=["GET"])
def check_md5(md5):
    ret = {"retcode": -1}
    if not md5:
        return jsonify(ret)
    file = get_image_cache(md5.lower())
    if not file:
        return jsonify(ret)

    ret["retcode"] = 0
    ret["file"] = file["file"]

    return jsonify(ret)


def run_server():
    server_host = get_config("global", "server_host")
    server_port = get_config("global", "server_port")
    add_ncnn_routes(app)
    app.run(host=server_host, port=server_port)
