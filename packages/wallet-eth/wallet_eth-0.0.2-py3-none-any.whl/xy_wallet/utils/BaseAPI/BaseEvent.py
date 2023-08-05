import os
from web3 import Web3
import time
import json
from pprint import pprint


def parse_path(path, num):
    for _ in range(1, num+1):
        path = path[:path.rfind("/")]
    return path


directory = os.path.dirname(__file__)
directory = parse_path(directory, 2)

with open(directory+"/conf/abi/abi.json", "r") as r:
    abi = json.loads(r.read())


class BaseEvent():
    def __init__(self) -> None:
        url = "https://ropsten.infura.io/v3/34ed41c4cf28406885f032930d670036"
        self.web3 = Web3(Web3.HTTPProvider(url))
        address = self.web3.toChecksumAddress(
            '0x43710f201183008EAf8170E729481289D52A695B')
        self.contract = self.web3.eth.contract(address=address, abi=abi)

    def main_function(self):
        latest = self.web3.eth.blockNumber
        transfer_events = self.contract.events.Transfer.createFilter(
            fromBlock=int(latest/5), toBlock=latest)
        data = transfer_events.get_all_entries()
        return data

    def loop_function(self):
        latest = self.web3.eth.blockNumber
        transfer_events = self.contract.events.Transfer.createFilter(
            fromBlock=latest-1, toBlock=latest)
        data = transfer_events.get_all_entries()
        return data

    def parsing_event(self, data):
        transfer_list = []
        for i in data:
            transfer_data = {}
            transfer_data['from'] = i['args']['from']
            transfer_data['to'] = i['args']['to']
            transfer_data['amount'] = i['args']['tokens']
            transfer_list.append(transfer_data)
        return transfer_list

    def get_transfer_events(self, realtime):
        data = self.main_function()
        pprint(self.parsing_event(data))
        print("↑↑↑↑↑↑↑↑↑↑↑↑↑↑历史数据↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
        while 1:
            data = self.loop_function()
            if not data:
                print("监听中···")
            else:
                pprint(self.parsing_event(data))
            time.sleep(realtime)


if __name__ == "__main__":
    main = BaseEvent()
    main.get_transfer_events(10)
