import datetime
import json
import os
import random
import time

import requests

from furl import furl


class UCPig:

    def __init__(self, uid, task_info, task_req, task_req2, award, userinfo, exchange, tx_body, headers, pig_url,
                 pig_award_body, coin_url):
        self.uid = uid
        self.host = furl(coin_url).host
        self.exchange_url = f'https://{self.host}/piggybank/withdraw/exchange'
        self.tx_url = 'https://ucwallet.uc.cn/exchange/submitExchange'
        self.exchange_amount = 0
        self.pig_award_body = pig_award_body
        self.pig_url = pig_url
        self.task_info = task_info
        self._task_req = task_req
        self._task_req2 = task_req2
        self.award = award
        self.userinfo = userinfo
        self.exchange = exchange
        self.coin_url = coin_url
        self.tx_body = tx_body
        self.headers = headers
        self.ignore_task = []
        self.first_time = self.get_first_date()
        self.day = (datetime.datetime.now() - self.first_time).days % 2 + 1
        if self.day == 1:
            self.task_req = task_req
        else:
            self.task_req = task_req2

    def get_first_date(self):
        ts = []
        for url in self._task_req.values():
            f = furl(url)
            t = f.args.get('__t')
            if t:
                ts.append(t)
        if ts:
            date = datetime.datetime.fromtimestamp(int(min(ts)[:-3]))
            return date
        else:
            return datetime.datetime.strptime('20210725 00:00:00', '%Y%m%d %H:%M:%S')

    @classmethod
    def random_wait(cls, a, b, message=None):
        r = a + random.random() * (b - a)
        if message:
            print(message + f',等待{r}s', flush=True)
        time.sleep(r)
        return r

    def request(self, url, data=None, method='get'):
        # f = furl(url)
        # host = f.host
        headers = self.headers
        f = furl(url)
        headers['Host'] = f.host
        if method == 'get':
            res = requests.get(url, headers=headers)
        else:
            headers['content-type'] = 'application/x-www-form-urlencoded'
            res = requests.post(url, data=data, headers=headers)
        data = res.json()
        # pprint(data)
        if data['code'] == 'OK':
            return data['data']
        return data

    @staticmethod
    def parse(account):
        params = account.split(';')
        data = {}
        for param in params:
            if '=' in param:
                k, v = param.split('=')
                data[k] = v
        return data

    @classmethod
    def get_accounts(cls):
        dn_sn_map = {}

        accounts = os.getenv('UCPIG_AUTH', '')
        if not accounts:
            print('请检查环境变量UCPIG_AUTH，示例:uid=xxx;', flush=True)
        accounts = [cls.parse(account) for account in accounts.split('&') if account]
        accounts = {
            account['uid']: {'pig_award_body': '', 'pig_url': '', 'uid': account['uid'], 'task_info': [],
                             'task_req': {},
                             'task_req2': {}, 'award': {}, 'userinfo': '', 'exchange': [], 'tx_body': [], 'headers': {}}
        for
            account in accounts}

        pig_award_urls = os.getenv('UCPIG_PIG_AWARD_URL', '')
        if not pig_award_urls:
            print('请检查环境变量UCPIG_PIG_AWARD_URL，收元宝获取', flush=True)
        else:
            for pig_award_url in pig_award_urls.split('&http'):
                if pig_award_url:
                    f = furl(pig_award_url)
                    f.scheme = 'https'
                    uid = f.args.get('sn')
                    accounts[uid]['pig_url'] = f.url

        pig_award_bodys = os.getenv('UCPIG_PIGAWARD_BODY', '')
        if not pig_award_bodys:
            print('请检查环境变量UCPIG_PIGAWARD_BODY，收元宝获取', flush=True)
        else:
            for pig_award_body in pig_award_bodys.split('&uid='):
                if pig_award_body:
                    pig_award_body = pig_award_body if pig_award_body[:4] == 'uid=' else f"uid={pig_award_body}"
                    uid = pig_award_body.split('&')[0].split('=')[-1]
                    accounts[uid]['pig_award_body'] = '&'.join(pig_award_body.split('&')[1:])

        task_infos = os.getenv('UCPIG_TASK', '')
        if not task_infos:
            print('请检查环境变量UCPIG_TASK，做进入任务中心获取', flush=True)
        else:

            for task_info in task_infos.split('&http'):
                task_info = task_info.strip(' ')
                f = furl(task_info)
                uid = f.args.get('sn')
                dn = f.args.get('dn')
                dn_sn_map[dn] = uid
                f.scheme = 'https'
                accounts[uid]['task_info'].append(f.url)

        task_reqs = os.getenv('UCPIG_TASK_REQ', '')
        if not task_reqs:
            print('请检查环境变量UCPIG_TASK_REQ，完成任务时获取', flush=True)
        else:

            for task_req in task_reqs.split(',http'):
                if task_req:
                    task_req = task_req.strip(' ')
                    f = furl(task_req)
                    uid = f.args.get('sn')
                    tid = f.args.get('tid')
                    f.scheme = 'https'
                    accounts[uid]['task_req'][tid] = f.url

        task_reqs = os.getenv('UCPIG_TASK_REQ2', '')
        if not task_reqs:
            print('请检查环境变量UCPIG_TASK_REQ2，完成任务时获取', flush=True)
        else:

            for task_req in task_reqs.split(',http'):
                task_req = task_req.strip(' ')
                f = furl(task_req)
                uid = f.args.get('sn')
                tid = f.args.get('tid')
                f.scheme = 'https'
                accounts[uid]['task_req2'][tid] = f.url

        task_awards = os.getenv('UCPIG_TASK_AWARD', '')
        if not task_awards:
            print('请检查环境变量UCPIG_TASK_AWARD，领取任务奖励时获取', flush=True)
        else:
            for task_award in task_awards.split(',http'):
                task_award = task_award.strip(' ')
                f = furl(task_award)
                uid = f.args.get('sn')
                tid = f.args.get('tid')
                f.scheme = 'https'
                if tid and uid:
                    accounts[uid]['award'][tid] = f.url

        exchange_body = os.getenv('UCPIG_EXCHANGE_BODY', '')
        if not pig_award_bodys:
            print('请检查环境变量UCPIG_EXCHANGE_BODY，点击兑换获取', flush=True)
        else:
            for exchange in exchange_body.split('&uid='):
                if exchange:
                    exchange_body = exchange if exchange[:4] == 'uid=' else f"uid={exchange}"
                    uid = exchange_body.split('&')[0].split('=')[-1]
                    accounts[uid]['exchange'] = '&'.join(exchange_body.split('&')[1:])

        tx_bodys = os.getenv('UCPIG_TX_BODY', '')
        if not tx_bodys:
            print('请检查环境变量UCPIG_TX_BODY，点击提现获取', flush=True)
        else:
            for tx_body in tx_bodys.split('&uid='):
                if tx_body:
                    tx_body = tx_body if tx_body[:4] == 'uid=' else f"uid={tx_body}"
                    uid = tx_body.split('&')[0].split('=')[-1]
                    accounts[uid]['tx_body'] = '&'.join(tx_body.split('&')[1:])

        coin_urls = os.getenv('UCPIG_COIN_URL', '')
        if not coin_urls:
            print('请检查环境变量UCPIG_COIN_URL', flush=True)
        else:

            for coin_url in coin_urls.split(',http'):
                coin_url = coin_url.strip(' ')
                f = furl(coin_url)
                uid = f.args.get('sn')
                # tid = f.args.get('tid')
                f.scheme = 'https'
                accounts[uid]['coin_url'] = f.url

        all_headers = os.getenv('UCPIG_HEADER', '')
        if not all_headers:
            print('请检查环境变量UCPIG_HEADER', flush=True)
        else:

            for headers in all_headers.split('&{'):
                try:
                    headers = headers.strip(' ')
                    headers = "{" + headers if headers[0]!= '{' else headers
                    headers = json.loads(headers)
                    referer = headers.get('Referer') if headers.get('Referer') else headers.get('referer')
                    f = furl(referer)
                    dn = f.args.get('dn')
                    uid = dn_sn_map[dn]
                    # tid = f.args.get('tid')
                    f.scheme = 'https'
                    accounts[uid]['headers'] = headers
                except Exception as e:
                    raise Exception(f"{e} UCPIG_HEADER 设置有误")

        return accounts

    def do_pig_award(self):
        self.request(self.pig_url, data=self.pig_award_body, method='post')

    def run(self):
        if self.task_info:
            for task_info in self.task_info:
                data = self.request(task_info)
                tasks = data['values']
                for task in tasks:
                    tid = task['id']
                    if tid in self.ignore_task:
                        continue
                    name = task['name']
                    progress = task['progress']
                    target = task['target']
                    state = task['state']
                    desc = task['desc']
                    if task.get('progress') == 0:
                        task_req = self.task_req.get(str(tid))
                        if not task_req:
                            print(f'UCPIG_TASK_REQ缺少第{self.day}天{name}请求信息id:{tid}')
                        else:
                            self.random_wait(20, 30, f'做任务:{name}')
                            res = self.request(task_req)
                            if res.get('state') == 1:
                                progress = res['curTask']['progress']
                                target = res['curTask']['target']
                                state = res['state']
                            elif res.get('code') == 'REPEAT_REQUEST_ID':
                                print(f"{res.get('msg')}")
                            else:
                                print(res)

                    if int(progress) == int(target) and state != 2:
                        award_req = self.award.get(str(tid))
                        if not award_req:
                            print(f'UCPIG_TASK_AWARD缺少{name}领取奖励请求信息id:{tid}')
                        else:
                            self.random_wait(1, 3, f'领取任务奖励:{name}')
                            res = self.request(award_req)
                            if res['state'] == 2:
                                print(f"完成{name} {desc}")

        else:
            print('任务获取失败，请检查环境变量UCPIG_TASK')

    def exchange_money(self):
        res = self.request(self.exchange_url, data=self.exchange, method='post')
        print(res)

    def parse_exchange_amount(self):
        amount = self.exchange.split('point=')[-1].split('&')[0]
        amount = int(amount)
        return amount

    def get_userinfo(self):
        data = self.request(self.coin_url)
        amount = data.get('longterm', {}).get('amount', 0)
        print(f'当前元宝:{amount}')
        if self.exchange:
            exchange_amount = self.parse_exchange_amount()
            if amount >= exchange_amount:
                self.exchange_money()
                self.tixian()

    def tixian(self):
        res = self.request(self.tx_url, data=self.tx_body, method='post')
        print(f'提现: {res.get("totalAmount", 0) / 100}💰', flush=True)


if __name__ == '__main__':
    accounts = UCPig.get_accounts()
    for account in accounts.values():
        ucpig = UCPig(**account)
        ucpig.run()
        ucpig.get_userinfo()


