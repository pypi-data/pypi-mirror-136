from django.core.cache import cache


def baseN(num, b=31):
    return ((num == 0) and "0") or \
           (baseN(num // b, b).lstrip("0") + "23456789abcdefghjkmnpqrstuvwxyz"[num % b])


def getRecommendCode():
    # cache.delete('recommend_code')
    origin_num = cache.get('recommend_code', 21100300)
    print('recommend_code = %s' % origin_num)
    code = 'qwf8v'
    if (origin_num == 21100300):
        cache.set('recommend_code', origin_num + 1)
        print('code ', code)
    else:
        next_num = origin_num + 1
        code = baseN(next_num)
        cache.set('recommend_code', next_num)
    return code.upper()
