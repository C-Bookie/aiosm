
from .dprint import dprint

from asyncio import StreamReader, StreamWriter


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
