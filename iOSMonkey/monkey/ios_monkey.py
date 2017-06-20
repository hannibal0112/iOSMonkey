#-*- encoding: utf-8 -*-
from wda import *
import random
from threading import Thread, Lock
import datetime
import time
# 需要指定端口
#
#

actions = ['_random_tap', '_random_swipe']
#actions = ['_random_tap', '_random_swipe', '_check_close_wnd']


mutex = Lock()
class CheckFinished(Thread):

    def __init__(self, minutes):
        super(CheckFinished, self).__init__()
        self._is_finished_task = False
        self._minutes = minutes


    def status(self):
        try:
            mutex.acquire()
            r = self._is_finished_task
            return self._is_finished_task
        finally:
            mutex.release()


    def set_status(self, value):
        try:
            mutex.acquire()
            self._is_finished_task = value
        finally:
            mutex.release()

    def run(self):
        total_seonds = self._minutes * 60
        start_time = time.time()
        while True:
            end_time = time.time()
            past_time = (end_time - start_time)

            if past_time >= total_seonds:
                self.set_status(True)
                break
        end_time = time.time()
        print("运行了{0}秒".format((end_time - start_time)))


class CaptureImage(Thread):

    def __init__(self, interval, check_finished):
        Thread.__init__(self)
        self._interval = interval
        self._check_finished = check_finished

    def run(self):
        while True:
            if self._check_finished.status:
                break





class Monkey(object):
    def __init__(self, port = 8100, host = '192.168.0.169', protocol='http://', bundle_id = "com.netdragon.quicktest" ,session = None):
        self._port = port
        self._host = host
        self._protocol = protocol
        self._target = '{0}{1}:{2}'.format(protocol, host, port)
        self._client = Client(self._target)
        self._bundle_id = bundle_id
        if session == None:
            self._session = self._client.session(bundle_id)
        else:
            self._session = session


    def start_app(self, bundle_id):
        self._session = self._client.session(bundle_id)


    def start_monkey(self, image_store_path, running_time = 5, capture_interval = 5,
                                          check_close_wnd = None, check_close_seconds = 5):

        if image_store_path.endswith("/"):
            self._image_store_path = image_store_path
        else:
            self._image_store_path = image_store_path + "/"
        self._runing_time = running_time
        self._capture_interval = capture_interval
        self._check_close_seconds = check_close_seconds

        check_task = CheckFinished(minutes=running_time + 0.1)
        check_task.start()

        self._start_time = time.time()
        self._start_check_time = time.time()
        self._size = self._session.window_size()
        while True:
            if check_task.isAlive() == False:
                break
            self._screenshot()
            action_index = random.randint(0, len(actions) - 1)
            action_str = actions[action_index]
            if hasattr(self, action_str):
                func = getattr(self, action_str)
                func()

    def _check_close_wnd(self, func):
        end_time = time.time()
        past_time = end_time - self._start_check_time
        if past_time >= self._check_close_seconds:
            self._start_check_time = time.time()
            func()

    def _screenshot(self):
        end_time = time.time()
        past_time = end_time - self._start_time
        if past_time >= self._capture_interval:
            self._start_time = time.time()
            img_name = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')

            name = self._image_store_path + img_name + ".png"
            self._client.screenshot(name)


    def _random_tap(self):
        x = random.randint(1, self._size.width)
        y = random.randint(1, self._size.height)
        self._session.tap(x, y)

    def _random_swipe(self):
        x1 = random.randint(1, self._size.width)
        y1 = random.randint(1, self._size.height)
        x2 = random.randint(1, self._size.width)
        y2 = random.randint(1, self._size.height)
        self._session.swipe(x1, y1, x2, y2)


if __name__ == '__main__':
    monkey = Monkey(bundle_id="com.htc.drugmaster.ios")
    monkey.start_monkey(image_store_path='/tmp',
                        running_time=0.2,
                        capture_interval=5)

    # print(monkey._target)
else:
    print('import monkey module')
