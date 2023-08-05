from xy_wallet.utils.BaseAPI.BaseConfig import ConfigUtil
from xy_wallet.utils import (
    WalletClass,
    ToolClass,
    TokenClass,
)
import fire


WalletClass = WalletClass.BaseWalletClass()
ToolClass = ToolClass.BaseToolClass()
TokenClass = TokenClass.BaseTokenClass()
config = ConfigUtil()


class Wallet:
    def __init__(self):

        self.help = """

        Usage

            wallet token/tool/wallet show/crate/recover ...

        Parameters

            token
                token类 add(添加代币)、balance(获取余额)、get_list(获取列表)、send(发送交易)、event(监听转账)
            tool
                tool类 current(获取当前网络)、set(更换网络)
            wallet
                wallet类 show(查看钱包)、crate(创建钱包)、recover(恢复钱包)

        """

    def token(self):
        return TokenClass

    def tool(self):
        return ToolClass

    def wallet(self):
        return WalletClass

    def help(self):
        return self.help


def main():
    fire.Fire(Wallet)


if __name__ == "__main__":
    main()
