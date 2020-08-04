
from .radio import Radio
from .dprint import dprint

import asyncio
import inspect
import time
import json
from typing import List, Callable


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

	@staticmethod
	def echo(message: str) -> None:
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
