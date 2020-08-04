
from .dprint import dprint
from .node import Node

import asyncio
from asyncio import StreamReader, StreamWriter, AbstractServer
from typing import List


class Host:
	server: AbstractServer

	def __init__(self, addr='127.0.0.1', port=8888):
		super().__init__()
		self.addr = addr
		self.port = port
		self.connections: List[Node] = list()

	async def handler(self, reader: StreamReader, writer: StreamWriter):
		name = asyncio.current_task().get_name()
		node = Node(name, self, reader, writer)
		self.connections.append(node)
		try:
			await node.run()
		finally:
			self.connections.remove(node)

	async def run(self):
		self.server = await asyncio.start_server(self.handler, self.addr, self.port)
		await self.server.start_serving()
		dprint("Starting", f'Serving on {self.server.sockets[0].getsockname()}')

	async def close(self):
		for node in self.connections:
			await node.quit()
		self.server.close()
		await self.server.wait_closed()
		print("moo")
