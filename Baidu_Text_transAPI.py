# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
from hashlib import md5
from config.baidu_config import APP_ID, APP_KEY

from_lang = 'en'
to_lang = 'zh'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


def translate_text(query, source_lang='auto', target_lang='zh'):
    if not query:
        return ''
    salt = random.randint(32768, 65536)
    sign = make_md5(APP_ID + query + str(salt) + APP_KEY)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'appid': APP_ID,
        'q': query,
        'from': source_lang,
        'to': target_lang,
        'salt': salt,
        'sign': sign,
    }
    response = requests.post(url, params=payload, headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    if 'error_code' in result:
        raise Exception(json.dumps(result, ensure_ascii=False))
    trans_result = result.get('trans_result')
    if not trans_result:
        return ''
    return '\n'.join(item.get('dst', '') for item in trans_result)


if __name__ == '__main__':
    sample_query = 'Hello World! This is 1st paragraph.\nThis is 2nd paragraph.'
    print(translate_text(sample_query, from_lang, to_lang))
