from urllib import parse

from flask import Flask, Response, abort, jsonify, request

from ..config import get_config, get_items
from .helps import get_image_info, ncnn_result_dir
from .vulkan import create_convert_image_from_url_task

running_tasks = {}

ncnn_list = get_config("ncnn", "list").split()


# 处理图片
def ncnn_vulkan():
    ret = {"retcode": -1}
    scale = int(request.form.get("scale", 2))
    modal = request.form.get("modal", "realcugan")
    url = request.form.get("url")

    if not url:
        ret["msg"] = "错误: 未找到图片"
        return jsonify(ret)

    file_name, task_id, thread, ok = create_convert_image_from_url_task(
        url, scale, modal
    )
    if not ok:
        ret["msg"] = "错误: 不支持的文件类型"
        return jsonify(ret)
    running_tasks[task_id] = {"file_name": file_name, "scale": scale, "thread": thread}

    ret["retcode"] = 0
    ret["task_id"] = task_id
    ret["msg"] = "正在处理中, 请稍等"

    return jsonify(ret)


# 获取处理状态
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


# 获取处理成功的图片
def ncnn_result_image(file_name):
    if not file_name:
        abort(404)

    result_image = ncnn_result_dir / parse.quote(file_name)
    if not result_image.exists():
        abort(404)

    return Response(result_image.read_bytes(), mimetype="image/jpeg")


def ncnn_config():
    ret = {"retcode": -1}
    if not ncnn_list:
        ret["msg"] = "尚未配置超分模型列表, 位于config.ini的ncnn->list"
        return jsonify(ret)

    ncnn_scales = {}

    for modal_name in ncnn_list:
        info = get_items(modal_name)
        ncnn_scales[modal_name] = dict(info)

    return jsonify(ncnn_scales)


def add_routes(app: Flask):
    app.add_url_rule("/ncnn_config", "ncnn_config", ncnn_config, methods=["GET"])
    app.add_url_rule("/ncnn_vulkan", "ncnn_vulkan", ncnn_vulkan, methods=["POST"])
    app.add_url_rule(
        "/get_ncnn_vulkan_status/<task_id>",
        "get_ncnn_vulkan_status",
        get_ncnn_vulkan_status,
        methods=["GET"],
    )
    app.add_url_rule(
        "/ncnn_result_image/<file_name>",
        "ncnn_result_image",
        ncnn_result_image,
        methods=["GET"],
    )
