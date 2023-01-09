import asyncio
import unittest

from aiosm import Host, Client, __version__


class Adder(Client):  # example implementing the Client class
	def __init__(self, name):
		super().__init__(name)
		self.white_list_functions += [  # names of class functions appended to the list are accessible by the Host
			"echo",
			"print",
			"pass_along",
			"add"
		]

		self.i = 1

	async def echo(self, message):
		await self.broadcast("test", "print", message)

	@staticmethod
	async def print(message):
		print(message)

	async def pass_along(self, tag):
		await self.broadcast(tag, "add", self.i)

	async def add(self, n):
		self.i += n


class MyTestCase(unittest.TestCase):
	def test_version(self):
		self.assertEqual(__version__, '0.0.3')

	host = Host()
	client1 = Adder("client1")
	client2 = Adder("client2")

	async def run_clients(self, callback):
		async def setup():
			await asyncio.gather(
				self.client1.connect(),
				self.client2.connect()
			)
			await asyncio.gather(  # subscription should occur after connecting yet before any broadcasting in callback
				self.client1.request("subscribe", "client1"),
				self.client2.request("subscribe", "client2")
			)
			await asyncio.gather(
				self.client1.run(),
				self.client2.run(),
				callback()
			)
		await self.host.run()
		await setup()

	def test_bidirectional_rpc(self):
		async def broadcast_test():
			asyncio.current_task().set_name("Broadcast Test")
			await self.client1.broadcast("client2", "pass_along", "client1")
			await self.client1.pass_along("client2")
			await self.client2.pass_along("client1")

			await asyncio.sleep(1)

			await self.host.close()

		asyncio.run(self.run_clients(broadcast_test))

		self.assertEqual(3, self.client1.i)
		self.assertEqual(2, self.client2.i)


if __name__ == '__main__':
	unittest.main()
