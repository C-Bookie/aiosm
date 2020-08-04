from .host import Host

import asyncio
import argparse

parser = argparse.ArgumentParser(description='Asynchronous socket manager for using asyncio with RPC capabilities.')
parser.add_argument('--addr', type=str, nargs='?', default='127.0.0.1', help='The IP address to use')
parser.add_argument('--port', type=int, nargs='?', default=8888, help='The port to use')
args = parser.parse_args()


def run_host():
	host = Host(addr=args.addr, port=args.port)
	loop = asyncio.get_event_loop()
	task = loop.create_task(host.run())
	task.set_name("Host")
	loop.run_forever()
	loop.close()


if __name__ == "__main__":
	run_host()
