from xy_wallet.utils.BaseAPI.BaseWallet import BaseWalletAPI


class BaseWalletClass:
    def __init__(self):
        pass

    def help(self):
        """
        获取帮助
        """
        return """
        钱包类
        sample: wallet show
                wallet token balance weth
                wallet token send weth 0xabc123 100
        """

    def show(self, pwd):
        """
        查看钱包

        :param pwd: _description_
        :return: _description_
        """
        show_api = BaseWalletAPI(pwd=pwd)
        return show_api.show

    def crate(self, pwd):
        """
        创建钱包

        :param pwd: _description_
        :return: _description_
        """
        crate_api = BaseWalletAPI(init_account=True)
        return crate_api.create_wallet(pwd)

    def recover_p(self, priv, pwd):
        """
        通过私钥恢复
        """
        recover_api = BaseWalletAPI(init_account=True)
        return recover_api.recover_wallet(priv, pwd)

    def recover_m(self, mnemonic, pwd):
        """
        通过助记词恢复

        :param mnemonic: _description_
        :param pwd: _description_
        :return: _description_
        """
        wallet_api = BaseWalletAPI(init_account=True)
        return wallet_api.recover_m(mnemonic, pwd)
