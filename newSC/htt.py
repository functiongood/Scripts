import json
import os
import random
import time
from pprint import pprint

import requests


class Htt:

    def __init__(self, user_id, login_id, sensorsdata, register_time, read_token, version_name=None, app_version=None,
                 ua=None):
        self.user_id = user_id
        self.loginid = login_id
        self.sensorsdata = sensorsdata
        self.register_time = register_time
        self.version_name = version_name if version_name else '4.5.0'
        self.app_version = app_version if app_version else 1042
        self.read_token = read_token
        self.ua = ua if ua else 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
        self.is_sign = False

    @classmethod
    def random_wait(cls, a, b, message=None):
        r = a + random.random() * (b - a)
        if message:
            print(message + f',等待{r}s', flush=True)
        time.sleep(r)
        return r

    def request(self, **kw):
        headers_ = kw.get('headers', {})
        headers = {
            'Host': 'api.cashtoutiao.com',
            'accept': '*/*',
            'content-type': 'application/json',
            'user-agent': self.ua,
            'accept-language': 'zh-Hans;q=1',
        }
        headers.update(headers_)
        kw['headers'] = headers
        kw['url'] = 'https://api.cashtoutiao.com' + kw['url'] if kw['url'][0] == '/' else kw['url']

        res = requests.post(**kw)
        if res.url.startswith('https://api.cashtoutiao.com') or res.url.startswith(
                'https://api.easytask.huadongmedia.com'):
            data = res.json()
            if data.get('statusCode') == 200:
                return data
            else:
                raise Exception(res.text)
        return res

    def get_task_list(self):
        """
        获取任务详情
        :return:
        """
        json = {"loginId": self.loginid, "registerTime": self.register_time, "versionName": self.version_name,
                "userId": self.user_id, "appVersion": self.app_version, "platform": 1}
        cookies = {
            'sensorsdata2015jssdkcross': self.sensorsdata,
            'sajssdk_2015_cross_new_user': '1',
        }
        params = {
            'userId': str(self.user_id),
            'loginId': str(self.loginid),
            'appVersion': str(self.app_version),
            'platform': '1',
            'versionName': self.version_name,
        }
        data = self.request(url='/frontend/newbie/task/list', params=params, json=json, cookies=cookies)
        newbie_tasks = data['newbieTaskList']
        for task in newbie_tasks:
            if task.get('state') == 1 and task.get('taskId') != 5:
                self.finish_task(task_id=task.get('taskId'), task_type='newbie')

        json.pop('registerTime')
        data = self.request(url='/frontend/daily/task/revision/list', params=params, json=json, cookies=cookies)
        normal_tasks = data['normalTaskList']
        for task in normal_tasks:
            if task.get('state') == 1:
                self.finish_task(task_id=task.get('taskId'), task_type='normal')

        data = self.request(url='/frontend/sign/record', params=params, json=json, cookies=cookies)
        self.is_sign = data.get('state') != 0

    def hour_reward(self):
        params = {
            'userId': str(self.user_id),
            'loginId': str(self.loginid),
            'appVersion': str(self.app_version),
            'platform': '1',
            'versionName': self.version_name,
        }

        data = {"loginId": self.loginid, "versionName": self.version_name,
                "userId": self.user_id, "appVersion": self.app_version, "platform": 1}

        data = self.request(url='https://api.cashtoutiao.com/frontend/credit/sych/reward/per/hour', params=params,
                            json=data)
        multiple_info = data.get('multipleInfo')
        if multiple_info:
            data = {"multipleInfo": multiple_info, "loginId": self.loginid, "versionName": self.version_name,
                    "userId": self.user_id, "appVersion": self.app_version, "platform": 1}

            data = self.request(url='https://api.cashtoutiao.com/frontend/reward/multiple/draw',
                                params=params, json=data)

    def finish_task(self, task_id, task_type='newbie'):
        cookies = {
            'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%2217a9b5f3a0f345-0b29c0c8da24038-3b176850-370944-17a9b5f3a10667%22%2C%22%24device_id%22%3A%2217a9b5f3a0f345-0b29c0c8da24038-3b176850-370944-17a9b5f3a10667%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D',
        }

        params = {
            'userId': str(self.user_id),
            'loginId': str(self.loginid),
            'appVersion': str(self.app_version),
            'platform': '1',
            'versionName': self.version_name,
        }

        data = {"loginId": self.loginid, "versionName": self.version_name, "taskId": task_id, "userId": self.user_id,
                "appVersion": self.app_version, "platform": 1}

        if task_type == 'newbie':
            data = self.request(url='/frontend/newbie/task/draw', params=params, cookies=cookies, json=data)

        if task_type == 'normal':
            data = requests.post('/frontend/daily/task/revision/draw', params=params, cookies=cookies, json=data)

    def sign(self):
        if self.is_sign:
            return
        params = {
            'userId': str(self.user_id),
            'loginId': str(self.loginid),
            'appVersion': str(self.app_version),
            'platform': '1',
            'versionName': self.version_name,
        }

        json = {"loginId": self.loginid, "versionName": self.version_name,
                "userId": self.user_id, "appVersion": self.app_version, "platform": 1}

        data = self.request(url='/frontend/sign', params=params, json=json)

    def lottery(self):

        headers = {
            'Host': 'api.easytask.huadongmedia.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/json',
            'origin': 'http://page.huadongmedia.com',
            'accept-language': 'zh-cn',
            'user-agent': self.ua,
            'referer': f'http://page.huadongmedia.com/h5/product/lottery/index.html?mediaId=cashtoutiao&userId={self.user_id}',
        }

        json = {"mediaId": "cashtoutiao", "userId": "153137064"}

        for i in range(6):
            self.random_wait(5, 10)
            data = self.request(url='https://api.easytask.huadongmedia.com/task-center/lottery/info', headers=headers,
                                json=json)
            if data['lotteryInfo'].get('nextSessionTime') or not data['lotteryInfo'].get('drawRemainNum', 0):
                return

            data = self.request(url='https://api.easytask.huadongmedia.com/task-center/lottery/draw', headers=headers,
                                json=json)
            reward_id = data['drawInfo']['rewardId']
            token = data['drawInfo']['token']

            self.random_wait(10, 20, message='大转盘抽奖一次')
            try:
                data = {"mediaId": "cashtoutiao", "userId": str(self.user_id), "rewardId": reward_id, "token": token}

                data = self.request(url='https://api.easytask.huadongmedia.com/task-center/lottery/reward',
                                    headers=headers,
                                    json=data)
            except Exception as e:
                pprint(e)

    def get_read_token(self):
        if os.path.exists('.htt.token'):
            with open('.htt.token', 'r') as f:
                data = json.load(f)
                token = data.get(str(self.user_id))
                if token:
                    return token if token > self.read_token else self.read_token
        return self.read_token

    def set_read_token(self, token):
        data = {}
        if os.path.exists('.htt.token'):
            with open('.htt.token', 'r') as f:
                data = json.load(f)
        data[self.user_id] = str(token)
        f = open('.htt.token', 'w')
        json.dump(data, f)

    def read(self):
        for _ in range(random.randint(1, 5)):
            params = {
                'userId': str(self.user_id),
                'loginId': str(self.loginid),
                'appVersion': str(self.app_version),
                'platform': '1',
                'versionName': self.version_name,
            }
            self.random_wait(30, 30, '阅读一次')
            data = {"versionName": self.version_name, "token": self.get_read_token(), "platform": 1, "count": 1,
                    "userId": self.user_id,
                    "multiple": False, "channel": "dongfang", "duration": 30, "appVersion": self.app_version,
                    "loginId": self.loginid,
                    "readActionInfo": {"maxHistorySize": 0, "toolTypes": [0], "moveAvgPressure": random.random(),
                                       "downCount": random.randint(10, 20), "monkey": False,
                                       "moveCount": random.randint(500, 700), "downAvgPressure": 0}}

            data = self.request(url='/frontend/read/sych/duration',
                                params=params,
                                json=data)
            self.set_read_token(data['token'])
            if data.get('state') == 10:
                data = {"versionName": "4.5.0", "token": self.get_read_token(), "platform": 1, "count": 1,
                        "userId": self.user_id,
                        "multiple": False, "channel": "dongfang", "duration": 30, "appVersion": self.app_version,
                        "loginId": self.loginid,
                        "readActionInfo": {"maxHistorySize": 0, "toolTypes": [0], "moveAvgPressure": random.random(),
                                           "downCount": random.randint(10, 20), "monkey": False,
                                           "moveCount": random.randint(500, 700), "downAvgPressure": 0}}

                data = self.request(url='/frontend/read/sych/duration',
                                    params=params,
                                    json=data)
                self.set_read_token(data['token'])

    def video_duration(self):
        cookies = {
            'sensorsdata2015jssdkcross': self.sensorsdata,
        }

        params = {
            'userId': str(self.user_id),
            'loginId': str(self.loginid),
            'appVersion': str(self.app_version),
            'platform': '1',
            'versionName': self.version_name,
        }
        for _ in range(random.randint(2, 10)):
            self.random_wait(30, 30, '看视频30秒')
            data = {"versionName": self.version_name, "token": self.get_read_token(), "platform": 1, "count": 0,
                    "userId": self.user_id, "multiple": False, "channel": "video", "duration": 30,
                    "appVersion": self.app_version, "loginId": self.loginid}

            data = self.request(url='https://api.cashtoutiao.com/frontend/read/sych/duration',
                                params=params, cookies=cookies, json=data)

            self.set_read_token(data['token'])
            if data.get('state') == 10:
                data = {"versionName": "4.5.0", "token": self.get_read_token(), "platform": 1, "count": 1,
                        "userId": self.user_id,
                        "multiple": False, "channel": "dongfang", "duration": 30, "appVersion": self.app_version,
                        "loginId": self.loginid,
                        "readActionInfo": {"maxHistorySize": 0, "toolTypes": [0], "moveAvgPressure": random.random(),
                                           "downCount": random.randint(10, 20), "monkey": False,
                                           "moveCount": random.randint(500, 700), "downAvgPressure": 0}}

                data = self.request(url='/frontend/read/sych/duration',
                                    params=params,
                                    json=data)
                self.set_read_token(data['token'])

        print(data)

    def bottom_ad(self):
        pass


if __name__ == '__main__':

    print('本脚本仅用于学习', flush=True)


    def parse(account):
        params = account.split(';')
        data = {}
        for param in params:
            if '=' in param:
                k, v = param.split('=')
                data[k] = v
        return data


    accounts = os.getenv('HTT_AUTH')
    if not accounts:
        print('请设置环境变量HTT_AUTHH', flush=True)
    print(accounts, flush=True)

    ua = os.getenv('HTT_UA')

    accounts = [parse(account) for account in accounts.split('&') if account]
    accounts = [Htt(**account, ua=ua) for account in accounts]

    for htt in accounts:
        htt.get_task_list()
        htt.sign()
        htt.lottery()
        htt.read()
        htt.video_duration()
        htt.hour_reward()
