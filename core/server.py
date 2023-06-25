import sys

from flask import Flask, Response, abort, jsonify, request
from flask_cors import CORS
from werkzeug.serving import WSGIRequestHandler

from .config import get_config
from .mem_data import ImgDB
from .ncnn import add_routes as add_ncnn_routes

if not sys.gettrace():
    WSGIRequestHandler.log_request = lambda *args: None

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
CORS(app, resources=r"/*")

DB = ImgDB()

@app.route("/check_md5/<md5>", methods=["GET"])
def check_md5(md5):
    ret = {"retcode": -1}
    if not md5:
        return jsonify(ret)
    file = DB.get_data(md5.lower())
    if not file:
        return jsonify(ret)

    ret["retcode"] = 0
    ret.update(file.dict())

    return jsonify(ret)


def run_server():
    server_host = get_config("global", "server_host")
    server_port = get_config("global", "server_port")
    add_ncnn_routes(app)

    if sys.gettrace():
        app.run(host=server_host, port=server_port)
    else:
        from gevent import pywsgi

        from utils import logger

        logger.info("server start at %s:%s" % (server_host, server_port))
        server = pywsgi.WSGIServer((server_host, int(server_port)), app, log=None)
        server.serve_forever()
