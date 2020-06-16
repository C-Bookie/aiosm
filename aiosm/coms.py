import asyncio
import inspect
from asyncio import StreamReader, StreamWriter, AbstractServer
import json

from typing import List, Callable, Set

import datetime
import time


def dprint(message_type: str, *args) -> None:
	print(str(datetime.datetime.now()) + ": (" + asyncio.current_task().get_name() + ") " + message_type + ": \n\t", *args)


class Radio:
	ETX = b'\x03'  # end of transmission tag
	ETX_LEN = len(ETX)

	def __init__(self, reader: StreamReader, writer: StreamWriter):
		self.reader = reader
		self.writer = writer

	def prepare(self, message: str) -> bytes:
		data = message.encode()
		if self.ETX in data:
			raise Exception('message contains exit sequence: ' + self.ETX.decode())  # todo create custom Exception
		return data + self.ETX

	def unpack(self, data: bytes) -> str:
		return data[0:-self.ETX_LEN].decode()

	def sequence(self, message: str) -> None:
		data = self.prepare(message)
		self.writer.write(data)

	async def send(self, message: str) -> None:
		dprint("Sending", message)
		self.sequence(message)
		await self.writer.drain()

	async def feedback(self, message: str) -> None:
		data = self.prepare(message)
		dprint("Feeding-back", message)
		self.reader.feed_data(data)

	async def receive(self) -> str:
		data = await self.reader.readuntil(self.ETX)
		message = self.unpack(data)
		dprint("Received", message)
		return message


def json_encoder(obj):
	if isinstance(obj, set):
		return list(obj)
	return obj.list()


class Responder(Radio):
	def __init__(self, name, reader=None, writer=None):
		super().__init__(reader, writer)

		self.__name__ = type(self).__name__ + "-" + name

		self.white_list_functions: List[str] = [  # todo change to function reference in a json friendly way
			"echo",
			"close"
		]

		self.clock = time.time()
		self.update_rate = 1/60

		self.ready = reader is not None

	async def callback(self, response: dict) -> None:
		if "type" in response and response["type"] in self.white_list_functions:
			function: Callable = getattr(self, response["type"])
			if "args" in response and response["args"] is not None:
				args = response["args"]
			else:
				args = ()

			if inspect.iscoroutinefunction(function):
				await function(*args)
			else:
				function(*args)
		else:
			print("(", asyncio.current_task().get_name(), ") Request unrecognised by server: " + str(response))

	async def run(self) -> None:
		asyncio.current_task().set_name(self.__name__ + "-Receiver")
		dprint("listening", "Begun")
		if self.ready:
			try:
				while self.ready:
					message = await self.receive()
					await self.callback(message)
			except ConnectionResetError:
				dprint("Error", "Connection lost")
			finally:
				self.close()
				if self.writer.close():
					await self.writer.wait_closed()
					# self.reader, self.writer = None, None
				dprint("listening", "Ended")

	async def wait(self):
		new_clock = time.time()
		await asyncio.sleep(self.update_rate + self.clock - new_clock)
		self.clock = new_clock

	def echo(self, message: str) -> None:
		print(message)

	def close(self) -> None:
		self.ready = False

	def prepare(self, json_dict: dict) -> bytes:
		message = json.dumps(json_dict, default=json_encoder)
		return super().prepare(message)

	def unpack(self, data: bytes) -> dict:
		message = super().unpack(data)
		return json.loads(message)

	def sequence(self, json_dict: dict) -> None:
		if not self.ready:
			raise Exception("Illegal communication")
		# noinspection PyTypeChecker
		super().sequence(json_dict)

	async def send(self, json_dict: dict) -> None:
		if not self.ready:
			raise Exception("Illegal communication")
		# noinspection PyTypeChecker
		await super().send(json_dict)

	async def feedback(self, json_dict: dict) -> None:
		if not self.ready:
			raise Exception("Illegal communication")
		# noinspection PyTypeChecker
		await super().feedback(json_dict)

	async def receive(self) -> dict:
		if not self.ready:
			raise Exception("Illegal communication")
		# noinspection PyTypeChecker
		return await super().receive()

	async def quit(self) -> None:
		json_dict = {"type": "close"}
		await self.send(json_dict)
		await self.feedback(json_dict)


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


class Node(Responder):
	def __init__(self, name, host: Host, reader, writer):
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


def main():
	host = Host()
	loop = asyncio.get_event_loop()
	loop.create_task(host.run())
	loop.run_forever()
	loop.close()


if __name__ == "__main__":
	main()
