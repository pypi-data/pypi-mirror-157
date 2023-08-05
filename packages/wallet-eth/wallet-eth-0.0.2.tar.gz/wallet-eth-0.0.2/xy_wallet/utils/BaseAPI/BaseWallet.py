import json
import requests
from web3 import Web3
from eth_account import Account
from web3.gas_strategies.time_based import construct_time_based_gas_price_strategy
from web3.middleware import geth_poa_middleware
from xy_wallet.utils.BaseAPI import BaseConfig
import os

directory = os.path.dirname(__file__)


class BaseWalletAPI:
    def __init__(self,
                 init_account=False,
                 network_url=None,
                 poa=False,
                 keystore_dir=None,
                 keystore_filename=None,
                 pwd=123
                 ):
        self.pwd = pwd
        self.ConfigUtil = BaseConfig.ConfigUtil()

        # 装载配置文件
        self.get_config(
            keystore_filename,
            network_url,
            keystore_dir
        )

        # 查看有没有key_file
        try:
            with open(self.keystore_dir+self.keystore_filename, 'r') as r:
                data = r.read()
                if data is None or data == "":
                    init = True
                else:
                    init = False
        except Exception:
            init = True

        # 查看是否强制初始化账户
        init = init_account

        # 是否要初始化账户
        if init:
            self.init_account()
        else:
            self.load_account()

        # 是否启动POA链
        self.poa = poa
        if self.poa:
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.web3 = Web3(Web3.HTTPProvider(self.network_url))

    @property
    def show(self):
        return {"address": self._address, "private": self._privatekey}

    @property
    def private_key(self):
        return self._privatekey

    @property
    def address(self):
        return self._address

    def get_config(self,
                   keystore_filename,
                   network_url,
                   keystore_dir
                   ):
        self.keystore_filename = self.ConfigUtil.get[
            'KEYNAME'] if keystore_filename is None else keystore_filename
        self.network_url = self.ConfigUtil.get['NETWORK'][0] if network_url is None else network_url

        def parse_path(path, num):
            for _ in range(1, num+1):
                path = path[:path.rfind("/")]
            return path

        self.keystore_dir = parse_path(directory, 2)+"/conf/keystores/"
        self.gas_url = self.ConfigUtil.get['GAS_URL']

    def update_network(self, url):
        self.network_url = url
        self.ConfigUtil.set('NETWORK', url)
        return True

    def to_checksum_address(self, addr):
        return self.web3.toChecksumAddress(addr)

    def create_wallet(self, pwd):
        with open(self.keystore_dir+self.keystore_filename, "w") as w:
            acc = Account.create()
            address = acc.address
            privatekey = acc.privateKey
            w.write(json.dumps(Account.encrypt(privatekey, pwd)))
            return {"address": address, "private": privatekey.hex()}

    def recover_wallet(self, private: str, pwd):
        if isinstance(private, int):  # 输入过来的私钥是int格式
            private = hex(private)
        with open(self.keystore_dir+self.keystore_filename, "w") as w:
            acc = Account.privateKeyToAccount(private)
            address = acc.address
            w.write(json.dumps(Account.encrypt(private, pwd)))
            return {"address": address, "private": private}

    def recover_m(self, mnemonic, pwd):
        with open(self.keystore_dir+self.keystore_filename, "w") as w:
            Account.enable_unaudited_hdwallet_features()
            acc = Account.create_with_mnemonic(mnemonic)[0]
            address = acc._address
            privatekey = acc._private_key.hex()
            w.write(json.dumps(Account.encrypt(privatekey, pwd)))
            return {"address": address, "private": privatekey}

    def get_wallet_from_file(self, keystore_file):
        with open(keystore_file, "r") as r:
            private = Account.decrypt(json.loads(r.read()), self.pwd).hex()
            address = Account.privateKeyToAccount(private).address
            return {address: private}

    def load_account(self):
        """
        通过file装载账户
        """
        with open(self.keystore_dir+self.keystore_filename, "r") as r:
            self._privatekey = Account.decrypt(
                json.loads(r.read()), self.pwd).hex()
        self._address = Account.privateKeyToAccount(
            self._privatekey).address

    def init_account(self):
        """
        初始化账户

        :param pwd: _description_
        """
        self.init_keystore_file()
        self.load_account()

    def init_keystore_file(self):
        """
        keystore初始化
        """
        with open(self.keystore_dir+self.keystore_filename, "w") as w:
            w.write(json.dumps(Account.encrypt(
                Account.create().privateKey, self.pwd)))

    def sign_and_send_raw(self, params, private_key):
        """
        签名发送函数

        :param params: _description_
        :param private_key: _description_
        :return: _description_
        """
        # 使用私钥签名
        signed_tx = self.web3.eth.account.signTransaction(
            params, private_key=private_key)
        # 发送交易，并获得交易hash
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        # 返回交易hash
        print("tx_hash: {}".format(tx_hash.hex))
        return tx_hash.hex()

    def get_balance(self, address):
        """
        获取余额

        :param address: _description_
        :return: _description_
        """
        return float(self.web3.fromWei(
            self.web3.eth.get_balance(address),
            "Ether"))

    def transfer_eth(self, target_address, amount, private_key):
        """
        以太坊转账

        :param target_address: _description_
        :param amount: _description_
        :param private_key: _description_
        :return: _description_
        """
        address = Account.privateKeyToAccount(private_key).address

        # 获取用户的nonce
        nonce = self.get_nonce(address)
        # 构建交易数据包
        params = {
            'nonce': nonce,
            'to': target_address,
            'value': self.web3.toWei(amount, 'ether'),
            'gas': 210000,
            'gasPrice': self.web3.toWei('150', 'gwei'),
            # 'gasPrice': self.web3.toHex(self.web3.toWei(90, "Gwei")),
            'from': address,
        }
        return self.sign_and_send_raw(params, private_key)

    def contract_fun(self,
                     contractaddress,
                     abi_file: str,
                     private_key,
                     function_name,
                     args=None,
                     call=False):
        """
        合约函数

        :param contractaddress: _description_
        :param abi_file: _description_
        :param private_key: _description_
        :param function_name: _description_
        :param args: _description_, defaults to None
        :param call: _description_, defaults to False
        :return: _description_
        """
        with open(abi_file, "r", encoding="utf-8") as r:
            contract_abi = json.loads(r.read())

        address = self.web3.eth.account.from_key(private_key).address
        contractaddress = self.web3.toChecksumAddress(contractaddress)

        # 通过地址找到nonce
        nonce = self.get_nonce(address)

        # 定义合约对象
        contract = self.web3.eth.contract(
            address=contractaddress, abi=contract_abi)
        params = {'from': address, 'nonce': nonce}

        if not call:
            txn = eval("contract.functions.{}{}".format(function_name, args))
            self.web3.eth.set_gas_price_strategy(
                construct_time_based_gas_price_strategy(max_wait_seconds=60,
                                                        sample_size=10))
            gasprice = self.web3.eth.generateGasPrice()
            estimate_gas = txn.estimateGas(params)
            params.update({
                'gas': int(estimate_gas*1.1),
                'gasPrice': int(gasprice*1.5)
            })
            txn = txn.buildTransaction(params)
        elif args is None:
            return eval("contract.functions.{}().call()".format(function_name))
        else:
            return eval("contract.functions.{}(\"{}\").call()".format(function_name,
                                                                      args))

        receipt = self.sign_and_send_raw(txn, private_key)
        return self.web3.eth.wait_for_transaction_receipt(timeout=360, transaction_hash=receipt)

    def get_gas_price(self):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
        }
        resp_data = json.loads(requests.get(
            self.gas_url, headers=headers).text)
        return int(resp_data['result'], 16)

    def get_nonce(self, address):
        nonce = self.web3.eth.getTransactionCount(address)
        return nonce
