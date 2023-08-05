import asyncio, os, json, uuid
from tornado.web import RequestHandler

class HandleUploadFile(RequestHandler):
    '''
    将上传的文件保存到指定的目录
    '''
    upload_dir = './' # 子类需指定该属性
    origin_file_name = ''
    file_name = ''
    upload_file_error_msg = ''
    file_type = ''
    file_size = 0

    async def prepare(self):
        fut = super().prepare()

        if asyncio.coroutines.iscoroutine(fut):
            await fut

        f = self.request.files['file'] if 'file' in self.request.files else None

        if not f or len(f) < 1:
            self.upload_file_error_msg = '缺少上传文件'
            return

        dirpath = self.upload_dir

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        self.origin_file_name = f[0].get('filename')
        self.file_type = os.path.splitext(f[0].get('filename'))[-1]
        self.file_name = str(uuid.uuid1()) + self.file_type
        self.file_size = len(f[0].get('body'))

        with open(dirpath + self.file_name, mode='wb') as sf:
            try:
                sf.write(f[0].get('body'))
            except Exception as e:
                self.upload_file_error_msg = '写入文件失败'
                raise e
