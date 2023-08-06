import base64
import time
from hhycommon import HHYAES
 

class AuthCheck(object):

    # 解析用户token信息
    def parseToken(utoken):
        # base64解密
        utoken = str(base64.b64decode(utoken), 'utf-8')
        if not utoken:
            raise Exception('11008 空值错误')
        aes_decrypt_data = HHYAES.aes_decrypt(utoken)
        utoken_segs = aes_decrypt_data.split('>')
        if len(utoken_segs) < 1:
            raise Exception('解析token失败')

        return utoken_segs

    # 时间戳比60s大就有问题
    def checkToken(utoken):
        utoken_segs = AuthCheck.parseToken(utoken=utoken)
        uid = utoken_segs[0]
        if not uid:
            raise Exception('10098')
        timestmp = utoken_segs[1]
        if int(round(time.time() * 1000)) - int(timestmp) > 60:
            # print(int(round(time.time() * 1000)))
            # print(timestmp)
            raise Exception("t error")
        else:
            return (uid,timestmp)

