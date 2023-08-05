from xy_wallet.utils.BaseAPI.BaseConfig import ConfigUtil

ConfigUtil = ConfigUtil()


class BaseToolClass:
    def __init__(self):
        pass

    def current(self):
        """
        获取网络
        """
        return ConfigUtil.get['NETWORK']

    def set(self, url):
        """
        更换网络

        :param url: _description_
        """
        return ConfigUtil.set("NETWORK", url)
