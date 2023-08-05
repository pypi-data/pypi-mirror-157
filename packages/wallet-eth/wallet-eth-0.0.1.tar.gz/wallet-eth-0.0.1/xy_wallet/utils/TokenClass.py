
import os
from xy_wallet.utils.BaseAPI.BaseWallet import BaseWalletAPI
from xy_wallet.utils.BaseAPI.BaseConfig import ConfigUtil
from xy_wallet.utils.BaseAPI.BaseEvent import BaseEvent

ConfigUtil = ConfigUtil()
BaseEvent = BaseEvent()


def parse_path(path, num):
    for _ in range(1, num+1):
        path = path[:path.rfind("/")]
    return path


directory = os.path.dirname(__file__)
directory = parse_path(directory, 1)


class BaseTokenClass:
    def __init__(self):
        pass

    def help(self):
        """
        获取帮助
        """
        return """
        代币类
        sample: wallet token add weth 0xabc213
                wallet token balance weth
                wallet token send weth 0xabc123 100
        event只单独支持transfer监听
        """

    def add(self, token_name, addr):
        """
        增加代币

        :param token_name: _description_
        :param addr: _description_
        """
        return ConfigUtil.set(
            "TOKEN-LIST", NAME=token_name, ADDRESS=hex(addr))

    def balance(self, pwd, token_name="eth", addr=None):
        """
        获取余额

        :param addr: _description_, defaults to None
        :param token_name: _description_, defaults to "eth"
        """
        balance_api = BaseWalletAPI(pwd=pwd)
        addr = balance_api.address if addr is None else addr
        if token_name == "eth":
            print("您的ETH余额是: {}".format(balance_api.get_balance(addr)))
        else:
            token_list = ConfigUtil.get['TOKEN-LIST']
            for i in token_list:
                if i['NAME'] == token_name:
                    _addr = i['ADDRESS']
            decimals = 10**self._get_decimals(token_name, balance_api)
            print("您的{}余额是: {}".format(token_name, balance_api.contract_fun(
                _addr,
                directory+"/conf/abi/abi.json",
                balance_api.private_key,
                "balanceOf",
                balance_api.address,
                True)/decimals))

    def get_list(self):
        """
        代币列表

        :return: _description_
        """
        return ConfigUtil.get['TOKEN-LIST']

    def send(self, pwd, token_name, to, value):
        """
        发送交易

        :param token_name: _description_
        :param to: _description_
        :param value: _description_
        :return: _description_
        """
        send_api = BaseWalletAPI(pwd=pwd)
        to = send_api.to_checksum_address(to)

        if token_name == "eth":
            send_api.transfer_eth(to, value, send_api.private_key)
            return True

        if token_name == 'eth':
            return send_api.transfer_eth(to, value, send_api.private_key)
        else:
            token_list = ConfigUtil.get['TOKEN-LIST']
            for i in token_list:
                if i['NAME'] == token_name:
                    __address = i['ADDRESS']
            decimal = self._get_decimals(token_name, send_api)
            send_api.contract_fun(
                __address,
                directory+'/conf/abi/abi.json',
                send_api.private_key,
                'transfer',
                (to, int(float(value)*10**int(decimal))),
                False
            )
            # TODO 判断成功否
            return True

    def event(self):
        """
        获取event
        """
        BaseEvent.main_function()
        BaseEvent.get_transfer_events(10)

    def _get_decimals(self, token_name, get_decimals):
        """
        获取小数点

        :param token_name: _description_
        :return: _description_
        """
        if token_name == "eth":
            return 18
        else:
            token_list = ConfigUtil.get['TOKEN-LIST']
            for i in token_list:
                if i['NAME'] == token_name:
                    __address = i['ADDRESS']
            return get_decimals.contract_fun(
                __address,
                directory+'/conf/abi/abi.json',
                get_decimals.private_key,
                "decimals",
                None,
                True
            )
