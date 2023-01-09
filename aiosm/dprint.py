
import asyncio
import datetime


def dprint(message_type: str, *args) -> None:
	# todo, consider if this filtering is needed
	if message_type in [
		"Sending",
		"Received",
	]:
		print(str(datetime.datetime.now()) + ": (" + asyncio.current_task().get_name() + ") " + message_type + "")
	else:
		print(str(datetime.datetime.now()) + ": (" + asyncio.current_task().get_name() + ") " + message_type + ": \n\t", *args)
