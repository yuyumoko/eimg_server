import sys
from urllib import parse
from werkzeug.serving import WSGIRequestHandler
from flask import Flask, Response, abort, jsonify, request
from flask_cors import CORS
from .config import get_config
from .mem_data import get_image_cache
from .ncnn import create_convert_image_from_url_task
from .ncnn.helps import ncnn_result_dir, get_image_info

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


running_tasks = {}


@app.route("/ncnn_vulkan", methods=["POST"])
def ncnn_vulkan():
    ret = {"retcode": -1}
    scale = int(request.form.get("scale", 2))
    url = request.form.get("url")

    if not url:
        ret["msg"] = "错误: 未找到图片"
        return jsonify(ret)

    file_name, task_id, thread, ok = create_convert_image_from_url_task(url, scale)
    if not ok:
        ret["msg"] = "错误: 不支持的文件类型"
        return jsonify(ret)
    running_tasks[task_id] = {"file_name": file_name, "scale": scale, "thread": thread}

    ret["retcode"] = 0
    ret["task_id"] = task_id
    ret["msg"] = "正在处理中, 请稍等"

    return jsonify(ret)


@app.route("/get_ncnn_vulkan_status/<task_id>", methods=["GET"])
def get_ncnn_vulkan_status(task_id):
    ret = {"retcode": -1}
    if not task_id:
        return jsonify(ret)

    if task_id in running_tasks:
        ret["retcode"] = 0

        thread = running_tasks[task_id]["thread"]
        if thread.is_alive():
            ret["msg"] = "正在处理中, 请稍等"
            return jsonify(ret)
        else:
            result_image = ncnn_result_dir / running_tasks[task_id]["file_name"]
            scale = running_tasks[task_id]["scale"]
            running_tasks.pop(task_id)
            if not result_image.exists():
                ret["msg"] = "处理失败, 请重试"
                return jsonify(ret)

            width, height, format, size = get_image_info(result_image)

            ret["msg"] = f"{scale}倍放大处理完成"
            ret["info"] = {
                "name": result_image.name,
                "path": str(result_image),
                "width": width,
                "height": height,
                "format": format,
                "size": size,
                "scale": scale,
            }

            return jsonify(ret)

    ret["msg"] = "未找到任务"
    return jsonify(ret)


@app.route("/ncnn_result_image/<file_name>", methods=["GET"])
def ncnn_result_image(file_name):  # pragma: no cover
    if not file_name:
        abort(404)

    result_image = ncnn_result_dir / parse.quote(file_name)
    if not result_image.exists():
        abort(404)

    return Response(result_image.read_bytes(), mimetype="image/jpeg")


def run_server():
    server_host = get_config("global", "server_host")
    server_port = get_config("global", "server_port")
    app.run(host=server_host, port=server_port)
