import base64
import json
from django.http import JsonResponse, HttpResponse
from hhycommon import HHYAES


def hhy_net_response(code, msg, data={}, debug=1):
    ret_json = {
        'code': code,
        'msg': msg,
        'data': data
    }
    if debug:
        return JsonResponse(ret_json, safe=False)
    json_str = json.dumps(ret_json)
    aes_encrypt_data = HHYAES.aes_encrypt(json_str)
    ret = base64.b64encode(json.dumps(aes_encrypt_data).encode(encoding='utf-8'))
    return HttpResponse(ret)
