from tornado import web
from tornado import gen
from tornado.options import define, options, parse_command_line
from tornado import ioloop
from tornado import httpserver
# from tornado import template

from tornado.escape import json_decode, json_encode, url_unescape

from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from os.path import join, dirname

from vip_tools import vip_page as vpd
import uuid


from vip_tools.solver2 import VipLink, ServerHandlerError, SoupFindError
from vip_tools.downloader import Downloader
from vip_tools.saver import FileSaver
from constants import Action
from models import DownList, Bookmarks

PORT=8000


define("port", default=PORT, help="run on the given port", type=int)


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
        for raw in params['links']:
            DownList.create(source=params['source'], raw=raw, set=params['set'], uid=uuid.uuid4().hex)
        w = json_encode('Done')
        self.write(w)


class Params:
    def __init__(self, request):
        j = json_decode(url_unescape(request.query))
        self.direction = j.get('di')
        self.raw = j.get('ra')
        self.source = j.get('so')
        self.set = j.get('se')


class RawPageHandler(web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=5)

    @run_on_executor
    def background_task(self, params):
        try:
            v = VipLink(params.raw)
            s = []
            if params.direction & Action.TAB == Action.TAB:
                self.set_header("Content-type",  "image/jpg")
                s.append(self)
            if params.direction & Action.FILE == Action.FILE:
                s.append(FileSaver(v, params.set))
            if params.direction & Action.DB == Action.DB:
                DownList.create(source=params.source, raw=params.raw, set=params.set, uid=params.set)
                self.write('Done')
            if s:
                d = Downloader(v, *s)
                d.download()
        except SoupFindError as e:
            self.write(str(e))
        except ServerHandlerError as e:
            self.write(str(e))
 
    @gen.coroutine
    def get(self):
        p = self.background_task(Params(self.request))
        yield p
        c = p.exception()
        if c:pass
            # print(c)

    @gen.coroutine
    def post(self):
        p = self.background_task(Params(self.request))
        yield p
        c = p.exception()
        if c:pass
            # print(c)


class PageHandler(web.RequestHandler):
    def get(self, addr):
        vip_dict = vpd.get(addr)
        self.render('viper.html', page=vip_dict)




def start():
    parse_command_line()
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
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

