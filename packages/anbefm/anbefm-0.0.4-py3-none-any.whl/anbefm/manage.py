'''
Author: liubei
Date: 2021-04-09 09:15:30
LastEditTime: 2021-07-02 16:01:18
Description: 
'''
import pprint
import glob
import os
import importlib
import re
import click
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from .base.utils import iswin
from config import configs

class TestHandler(RequestHandler):
    def get(self):
        return self.write('test')

def create_app(routes = []):
    pprint.pprint(routes)
    return Application([('/test', TestHandler), *routes], debug=True)

def parse_handler_path(handler_path):
    # '.\\app1\\test_handler.py'
    restful = True if '_restful_handler.py' in handler_path else False
    # 去除restful修饰
    clsname = os.path.basename(handler_path.replace('_restful_handler.py', '_handler.py')).replace('.py', '')
    # TestHandler
    clsname = ''.join(map(lambda x:x.capitalize(), clsname.split("_")))
    # '/app1/test'
    path = handler_path.replace('_restful_handler.py', '') \
            .replace('_handler.py', '') \
            .replace('.\\', '/') \
            .replace('\\', '/')
    # 'app1.test_handler'
    module_path = handler_path.replace('.py', '').replace('.\\', '').replace('\\', '.')

    return clsname, path, module_path, restful

def parse_handler_path_linux(handler_path):
    # './app1/test_handler.py'
    restful = True if '_restful_handler.py' in handler_path else False
    # 去除restful修饰
    clsname = os.path.basename(handler_path.replace('_restful_handler.py', '_handler.py')).replace('.py', '')
    # TestHandler
    clsname = ''.join(map(lambda x:x.capitalize(), clsname.split("_")))
    # '/app1/test'
    path = handler_path.replace('_restful_handler.py', '') \
            .replace('_handler.py', '') \
            .replace('./', '/')
    # 'app1.test_handler'
    module_path = handler_path.replace('.py', '').replace('./', '').replace('/', '.')

    return clsname, path, module_path, restful

def build_routes(apps):
    # [.\\app1, ...]
    sub_dirs = glob.glob('./*')
    handlers = []

    for d in sub_dirs:
        if os.path.isdir(d) and (d.replace('./', '') in apps or d.replace('.\\', '') in apps):
            # ['.\\app1\\test_handler.py', ...]
            handlers.extend(find_handlers(d))

    routes = []

    for h in handlers:
        clsname, path, module_path, restful = parse_handler_path(h) if iswin() else parse_handler_path_linux(h)
        m = importlib.import_module(module_path)

        if hasattr(m, clsname):
            routes.append((path, getattr(m, clsname)))

            if restful:
                routes.append((f'{path}/(.*)', getattr(m, clsname)))

    return routes

def find_handlers(dirname):
    handlers = glob.glob(f'{dirname}/*_handler.py')
    # print(handlers)

    return handlers

@click.group()
def cli1():
    '''
    app相关命令
    '''

@cli1.command()
@click.option('--port', default=9001, type=int, help='默认端口8001')
@click.option('--app', type=str, help='启动的app')
def startapp(port, app):
    if not app or app not in configs['apps']:
        print(f'app: {app} 在config中不存在！')
        exit(1)

    print(f'startApp at {port}...')
    app = create_app(build_routes(configs['apps'][app]))
    app.listen(port)
    IOLoop.current().start()


if __name__ == '__main__':
    print('hi!')
    cli1()
