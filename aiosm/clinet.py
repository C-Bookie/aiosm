
from .responder import Responder

import asyncio


class Client(Responder):
	def __init__(self, name, addr='127.0.0.1', port=8888):
		super().__init__(name)
		self.addr = addr
		self.port = port

		# self.white_list_functions += []

	async def connect(self) -> None:
		self.reader, self.writer = await asyncio.open_connection(self.addr, self.port)  # todo add exception handling
		self.ready = True

	async def request(self, func_name: str, *args):
		await self.send({
			"type": func_name,
			"args": args
		})

	async def broadcast(self, tag: str, func_name: str, *args):  # only Clients subscribed to the tag shall receive
		await self.request("broadcast", {
					"type": func_name,
					"args": args
				},
				tag
		)
