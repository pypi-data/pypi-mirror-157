'''
Author: liubei
Date: 2021-04-08 17:21:53
LastEditTime: 2021-04-09 11:48:44
Description: 
'''
import asyncio
import json
from tornado.web import RequestHandler


class PayloadParams():
    ...


class HandlePayload(RequestHandler):
    payload: dict = {}

    async def prepare(self):
        fut = super().prepare()

        if asyncio.coroutines.iscoroutine(fut):
            await fut

        if 'application/json' in self.request.headers.get('Content-type', '') and self.request.body:
            res = '{}'
            print(self.request.body)
            try:
                res = self.request.body.decode('utf-8')
            except:
                res = self.request.body.decode('gbk')

            print(res)
            self.payload = json.loads(res) or {}
