# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import print_function, unicode_literals
from time import sleep
from xyz_util.crawlutils import Browser
import requests, argparse, json
from random import randrange


def get_args():
    parser = argparse.ArgumentParser(description="媒体浏览")
    parser.add_argument('-t', '--token', default='')
    parser.add_argument('-e', '--endpoint')
    return parser.parse_args()


class Client(object):

    def __init__(self, endpoint, token):
        self.endpoint = endpoint
        self.token = token
        self.headers = {
            'Authorization': 'Token %s' % token,
            'Content-Type': 'application/json'
        }
        self.PC = None
        self.MOBILE = None

    def reset(self):
        self.PC = None
        self.MOBILE = None

    def get_browser(self, mode):
        from xyz_browser.choices import MODE_PC
        if mode == MODE_PC:
            if not self.PC:
                self.PC = Browser()
            return self.PC
        else:
            if not self.MOBILE:
                self.MOBILE = Browser(mobile_mode=True)
            return self.MOBILE

    def apply(self):
        r = requests.patch('%s/apply/' % self.endpoint, headers=self.headers)
        rs = r.json()
        if r.status_code != 200:
            print(rs['detail'])
            return
        if rs:
            return rs[0]

    def report(self, task, data):
        r = requests.patch('%s/%d/report/' % (self.endpoint, task['id']),
                           json.dumps(dict(salt=task['salt'], data=data)),
                           headers=self.headers)
        rs = r.json()
        if r.status_code != 200:
            print(rs['detail'])
            return
        return rs

    def run(self):
        task = self.apply()
        if not task:
            return
        project = task['project']
        print(project['name'], task['url'])
        b = self.get_browser(project['mode'])
        b.get(task['url'])
        b.start_extract()
        b.run_script(project['script'])
        rs = self.report(task, b.extracted_data)
        return rs


if __name__ == '__main__':
    args = get_args()
    client = Client(args.endpoint, args.token)
    c = 0
    while True:
        c += 1
        try:
            b = client.run()
            if b:
                print('成功:', b)
        except:
            import traceback

            error = traceback.format_exc()
            if 'session deleted because of page crash' in error:
                client.reset()
            print(error)
            b = False
        sleep(randrange(5, 10) if b else 10)
