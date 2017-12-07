from tornado import web
from tornado import gen
from tornado import ioloop
from tornado import httpserver
# from tornado import template

from tornado.escape import json_decode, json_encode, url_unescape, url_escape

from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from urllib.parse import urlparse
from os.path import join, dirname

from vip_tools import vip_page as vpd
import uuid


from vip_tools.solver import VLink, ServerHandlerError, SoupFindError
from vip_tools.downloader import Downloader
from vip_tools.saver import FileSaver
from constants import Action
from models import DownList, Bookmarks
from config import CONFIG


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class BookmarksPageHandler(web.RequestHandler):
    def get(self):
        delete_url = self.get_query_argument('delete', None)
        if delete_url:
            d = Bookmarks.delete().where(Bookmarks.url == delete_url)
            d.execute()
        offset = self.get_query_argument('offset', 1)
        if offset:
            offset = int(offset)
        self.render('bookmarks.html', offset=offset)


class ReportPageHandler(web.RequestHandler):
    def get(self):
        self.render('viper/ereport.html')


class TestHandler(web.RequestHandler):
    def get(self):
        vip_dict = vpd.get('file:///home/soni/pyprojects/viper_server/vip/static/test/test.html')
        print(vip_dict)
        self.render('viper.html', page=vip_dict)
    def post(self):
        self.render("test.html")


class SetHandler(web.RequestHandler):
    def post(self):
        params = json_decode(url_unescape(self.request.body))
        source = urlparse(self.request.headers['Referer']).path
        set = params['set']
        resize = params['resize']
        uid = uuid.uuid4().hex
        for raw in params['links']:
            DownList.create(source=source, raw=raw, set=set, uid=uid, resize=resize)
        w = json_encode('{}'.format(len(params['links'])))
        self.write(w)



class RawPageHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=5)

    @run_on_executor
    def background_task(self, direction, vlink):
        try:
            s = []
            if direction & Action.TAB == Action.TAB:
                self.set_header("Content-type",  "image/jpg")
                s.append(self)
            if direction & Action.FILE == Action.FILE:
                s.append(FileSaver(vlink))
            if direction & Action.DB == Action.DB:
                DownList.create(source=vlink.source, raw=vlink.raw, set=vlink.set, uid=vlink.set, resize=vlink.resize)
                self.write('Done')
            if s:
                d = Downloader(vlink, *s)
                d.download()
        except SoupFindError as e:
            self.write(str(e))
        except ServerHandlerError as e:
            self.write(str(e))
 
    @gen.coroutine
    def get(self):
        # try:
        try:
            direction = int(self.get_argument('di'))
            raw = url_unescape(self.get_argument('ra'))
            resize = bool(int(self.get_argument('re', '1')))
            source = urlparse(self.get_argument('so')).path
            # host = self.request.host
            # method = self.request.method
            set = url_unescape(self.get_argument('se'))
        except web.MissingArgumentError as e:
            self.write(str(e))
            self.finish()
            return

        vlink = VLink(raw, set, source, resize)
        p = self.background_task(direction, vlink)
        yield p
        c = p.exception()
        if c:pass
            # print(c)

    @gen.coroutine
    def post(self):
        j = json_decode(self.request.body)
        direction = j.get('di')
        raw = url_unescape(j.get('ra'))
        source = urlparse(j.get('so')).path
        set = url_unescape(j.get('se'))
        resize = j.get('re', True)

        vlink = VLink(raw, set, source, resize)
        p = self.background_task(direction, vlink)
        yield p
        c = p.exception()
        if c:pass
            # print(c)


class PageHandler(web.RequestHandler):
    def get(self, addr):
        vip_dict = vpd.get(addr)
        self.render('vip.html', page=vip_dict)




def start():
    # parse_command_line()
    # settings = {
    #     "ui_modules": [UIModules]
    # }
    app = web.Application(
        handlers=[
            (r'/', IndexHandler), 
            (r'/test', TestHandler),
            # (r'/bookmarks', BookmarksPageHandler),
            (r'/page/([^/]+)', PageHandler),
            # (r'/ereport', ReportPageHandler),
            (r'/raw2', RawPageHandler),
            (r'/set', SetHandler),
            ],
        template_path=join(dirname(__file__), "templates"),
        static_path=join(dirname(__file__), "static"),
        debug=True,
        # **settings
    )
    http_server = httpserver.HTTPServer(app)
    http_server.listen(CONFIG['server.port'])
    ioloop.IOLoop.instance().start()

