
from aiosm.responder import Responder

import asyncio


class Client(Responder):
	def __init__(self, name, addr='127.0.0.1', port=8888):
		super().__init__(name)
		self.addr = addr
		self.port = port

		# todo consider adding white_list_functions
		# self.white_list_functions += []

	async def connect(self) -> None:
		# todo add exception handling
		self.reader, self.writer = await asyncio.open_connection(self.addr, self.port)
		self.ready = True

	async def request(self, func_name: str, *args):
		await self.send({
			"type": func_name,
			"args": args
		})

	async def broadcast(self, tag: str, func_name: str, *args):  # only Clients subscribed to the tag shall receive
		# fixme, add key word args
		#  tdoo, remember what this meant
		await self.request("broadcast", {
					"type": func_name,
					"args": args
				},
				tag
		)
