

from flask import jsonify

from api.utils.setting_utils import RetCode

from flask import json
##解决json 中文字符乱码的情况
json.provider.DefaultJSONProvider.ensure_ascii = False


def get_json_result(retcode=RetCode.SUCCESS, retmsg='success', data=None):
    response = {"retcode": retcode, "retmsg": retmsg, "data": data}
    return jsonify(response)

def server_error_response(e):
    # stat_logger.exception(e)
    try:
        if e.code == 401:
            return get_json_result(retcode=401, retmsg=repr(e))
    except BaseException:
        pass
    if len(e.args) > 1:
        return get_json_result(
            retcode=RetCode.EXCEPTION_ERROR, retmsg=repr(e.args[0]), data=e.args[1])
    if repr(e).find("index_not_found_exception") >= 0:
        return get_json_result(retcode=RetCode.EXCEPTION_ERROR, retmsg="No chunk found, please upload file and parse it.")

    return get_json_result(retcode=RetCode.EXCEPTION_ERROR, retmsg=repr(e))