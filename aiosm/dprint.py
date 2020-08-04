
import asyncio
import datetime


def dprint(message_type: str, *args) -> None:
	print(str(datetime.datetime.now()) + ": (" + asyncio.current_task().get_name() + ") " + message_type + ": \n\t", *args)
