import yaml
import os

template = {
    "NETWORK": "",
    "KEYPATH": "",
    "KEYNAME": "",
    "GAS_URL": "",
    "TOKEN-LIST": [
        {"NAME": "", "ADDRESS": ""}
    ]
}


def parse_path(path, num):
    for _ in range(1, num+1):
        path = path[:path.rfind("/")]
    return path


directory = os.path.dirname(__file__)
directory = parse_path(directory, 2)


class ConfigUtil:
    def __init__(self):

        self.config_name = "config.yaml"
        self.config_path = directory + "/conf/"
        self.config_file = self.config_path+self.config_name

        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w', encoding="utf-8") as w:
                yaml.safe_dump(template, w)

    def set(self, key, *value, **kwargs):
        data = self.get
        with open(self.config_file, 'w', encoding="utf-8") as w:
            if kwargs != {}:
                data[key].append(kwargs)
            else:
                data[key] = value
            yaml.safe_dump(data, w)
            return True

    @ property
    def get(self):
        with open(self.config_file, "r", encoding="utf-8") as r:
            return yaml.safe_load(r.read())


if __name__ == "__main__":
    config = ConfigUtil()
