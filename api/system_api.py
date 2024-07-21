#!/usr/bin/python3
# -*- coding:utf-8 -*-
# uDocParser
# PyCharm
# @Author:gaojing
# @Time: 2024/7/21 22:12

from timeit import default_timer as timer

from api.utils.api_utils import get_json_result


@manager.route('/status', methods=['GET'])
def status():
    res = {}
    st = timer()
    try:
        res["es"] = "ELASTICSEARCH.health()"
        res["es"]["elapsed"] = "{:.1f}".format((timer() - st)*1000.)
    except Exception as e:
        res["es"] = {"status": "red", "elapsed": "{:.1f}".format((timer() - st)*1000.), "error": str(e)}


    st = timer()
    try:
        oss_health = "MINIO.health()"
        res["minio"] = {"status": "green", "elapsed": "{:.1f}".format((timer() - st)*1000.)}
    except Exception as e:
        res["minio"] = {"status": "red", "elapsed": "{:.1f}".format((timer() - st)*1000.), "error": str(e)}

    return get_json_result(data=res)