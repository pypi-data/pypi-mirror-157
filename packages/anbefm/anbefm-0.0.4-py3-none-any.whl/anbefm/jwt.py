'''
Author: liubei
Date: 2021-04-08 17:21:53
LastEditTime: 2021-04-10 11:28:21
Description: 
'''
import json
import hmac
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode

jwt_encode = 'utf-8'
# TODO：可以随机生成secret, secret和jwt的映射关系保存在数据库，解码时获取
secret_str = 'basic_jwt_secret_001'

def create_jwt(payload: dict, secret: str = secret_str) -> str:
    header = json.dumps({
        'alg': 'HS256'
    }).encode(jwt_encode)
    payload = payload if payload else {}
    payload = json.dumps(payload).encode(jwt_encode)

    # base64编码
    header = urlsafe_b64encode(header).decode(jwt_encode)
    payload = urlsafe_b64encode(payload).decode(jwt_encode)

    # 加密
    signature = header + '.' + payload
    signature = hmac.new(
        secret.encode(jwt_encode), signature.encode(jwt_encode), hashlib.sha256).digest()
    signature = urlsafe_b64encode(signature).decode(jwt_encode)

    return header + '.' + payload + '.' + signature


def parse_jwt(jwt_str: str, secret: str = secret_str) -> dict:
    jwt_token = jwt_str.split('.')

    if len(jwt_token) != 3:
        return

    header = jwt_token[0]
    payload = jwt_token[1]
    signature = header + '.' + payload
    signature = hmac.new(
        secret.encode(jwt_encode), signature.encode(jwt_encode), hashlib.sha256).digest()
    signature = urlsafe_b64encode(signature).decode(jwt_encode)

    # jwt被篡改过
    if signature != jwt_token[2]:
        return

    # base64解码
    header = urlsafe_b64decode(header.encode(jwt_encode)).decode(jwt_encode)
    payload = urlsafe_b64decode(payload.encode(jwt_encode)).decode(jwt_encode)

    # 还原出信息
    # header = json.loads(header)
    # payload = json.loads(payload)

    return json.loads(payload)
