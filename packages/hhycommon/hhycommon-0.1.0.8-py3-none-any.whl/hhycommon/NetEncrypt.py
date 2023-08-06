import base64
import json

from django.conf import settings

from hhycommon import HHYAES
from hhycommon.NetResponse import hhy_net_response


class NetEncrypt(object):

    def process_request(request):
        # print('收到请求-------------------')
        if request.method == 'GET':
            # 解密之后验证解密数据
            params = request.GET.get("params")
            if not params:
                # 静态网页放过
                pass
            else:
                try:
                    params_bytes = base64.b64decode(params)
                    if not params_bytes or params_bytes == -1:
                        return hhy_net_response(603, "授权错误")

                    aes_decrypt_data = HHYAES.aes_decrypt(params_bytes.decode(encoding='utf-8'))
                    ret_json = json.loads(aes_decrypt_data)
                    if not ret_json or ret_json.get('hhid') != 'hehuoya':
                        return hhy_net_response(304, '系统异常', {})
                    request.ret_json = ret_json
                except Exception as e:
                    print(e)
                    return hhy_net_response(604, "异常失败")
        elif request.method == 'POST':
            body = request.body
            if request.path == '/githook/':
                pass
            elif not body:
                return hhy_net_response(602, request.path)
            else:
                try:
                    params_bytes = base64.b64decode(body)
                    if not params_bytes or params_bytes == -1:
                        return hhy_net_response(606, "授权错误")
                    aes_decrypt_data = HHYAES.aes_decrypt(params_bytes.decode(encoding='utf-8'))
                    ret_json = json.loads(aes_decrypt_data)
                    if not ret_json or ret_json.get('hhid') != 'hehuoya':
                        return hhy_net_response(304, '系统异常', {})
                    request.ret_json = ret_json
                except Exception as e:
                    print(e)
                    return hhy_net_response(607, e.__str__())
        else:
            return hhy_net_response(608, "异常失败")
