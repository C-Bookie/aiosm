
from aiosm.responder import Responder
# from .host import Host  # fixme circular import preventing type hinting

from typing import Set


class Node(Responder):
	def __init__(self, name, host, reader, writer):
		super().__init__(name, reader, writer)
		self.host = host

		self.subscriptions: Set[str] = {"all"}
		self.white_list_functions += [
			"subscribe",
			"broadcast"
		]

	async def subscribe(self, tag: str):
		self.subscriptions.add(tag)

	async def broadcast(self, json_dict: dict, tag: str):
		for node in self.host.connections:
			if node.ready and tag in node.subscriptions:  # todo change to channels containing Nodes to avoid for loops
				await node.send(json_dict)
