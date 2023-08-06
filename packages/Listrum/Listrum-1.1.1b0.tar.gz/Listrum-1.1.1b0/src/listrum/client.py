from base64 import urlsafe_b64decode, urlsafe_b64encode
import json
from random import randint
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import time
from components.constants import Const
from components.node_req import NodeReq
from utils.crypto import pad_key
from requests import Response


class Client:

    def __init__(self, key: str = "") -> None:
        if not key:
            self.priv = ECC.generate(curve='P-256')
        else:
            self.priv = ECC.import_key(urlsafe_b64decode(key))

        self.nodes = []

        self.owner = self.priv.public_key().export_key(format="DER")
        self.owner = urlsafe_b64encode(self.owner).decode()

        self.key = pad_key(self.owner)

    def export_priv(self) -> str:
        return urlsafe_b64encode(self.priv.export_key(format="DER")).decode()

    def get_owner(self, data: str) -> dict:

        time_stamp = int(time.time()*1000)

        data = data + str(time_stamp)
        data = SHA256.new(data.encode())

        sign = DSS.new(self.priv, 'fips-186-3').sign(data)

        owner = {
            "owner": self.owner,
            "time": time_stamp,
            "sign": urlsafe_b64encode(sign).decode()
        }

        return owner

    def remove_node(self, address: str) -> None:
        nodes = self.nodes

        for node in nodes:
            if node.address.find(address) >= 0:
                self.nodes.remove(node)

    def add_node(self, address: str) -> None:
        self.nodes.append(NodeReq(address))

    def send(self, to: str, value: float) -> Response:

        to = {
            "to": to,
            "value": float(value)
        }

        owner = self.get_owner(json.dumps(to).replace(" ", ""))

        data = {
            "to": to,
            "from": owner
        }

        rand_node = randint(0, len(self.nodes)-1)

        return self.nodes[rand_node].send(data)

    def issue(self, value: float) -> Response:
        owner = self.get_owner(str(value))

        data = {
            "value": float(value),
            "from": owner
        }

        rand_node = randint(0, len(self.nodes)-1)

        return self.nodes[rand_node].issue(data)

    def balance(self) -> float:
        balance = 0
        total = 0

        for node in self.nodes:
            try:
                balance += node.balance(self.key)
                total += 1

            except:
                pass

        if not total:
            return "No nodes"

        return balance/total


def check_command(cli: Client, command: list) -> None:

    if command[0] in ["delete", "remove"]:
        cli.remove_node(command[1])

    if command[0] in ["node", "add"]:
        cli.add_node(command[1])

    if command[0] in ["list", "nodes"]:
        for node in cli.nodes:
            print(node.address)

    if command[0] == "clear":
        for node in cli.nodes:
            cli.remove_node(node.address)

    if command[0] in ["issue", "mint"]:
        cli.issue(command[1])
        print(cli.balance())

    if command[0] == "send":
        if len(str(command[1])) == Const.pad_length:
            cli.send(command[1], command[2])
        else:
            cli.send(command[2], command[1])

        print(cli.balance())

    if command[0] in ["address", "key", "wallet", "balance"]:
        print(cli.key)
        print(cli.balance())

    if command[0] in ["privkey", "private", "priv", "export"]:
        print(cli.export_priv())

    if command[0] in ["history", "tx"]:
        if len(command) < 2:
            res = cli.nodes[0].history(cli.key)
        else:
            res = NodeReq(command[1]).history(cli.key)

        for tx in json.loads(res.text):
            print(tx)


def create_client() -> Client:
    cli = Client(input("Private key (optional): "))

    node = input("Node: ")
    if node:
        cli.add_node(node)

    return cli


if __name__ == "__main__":

    cli = create_client()

    while True:
        command = input("/").split(" ")
        check_command(cli, command)
