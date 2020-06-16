
# asyncio socket manager


Classes extending the Client class can overload the run function to connect, subscribe and run a loop in parallel

    async def run(self):
        await self.connect()
        await self.request("subscribe", "clinet1")
        await asyncio.gather(
            super().run(),
            self.loop()
        )

A loop function can deal with outgoing communication as long as it periodically calls self.wait

    async def loop(self):
        asyncio.current_task().set_name(self.__name__ + "-Transmitter")
        while True:
            #
            await self.wait()

To expose functions to RPC calling, add their name to the white_list_functions list.
To call a function running on a serer node, use self.request():

    await self.request("<name of function>", *args)

To call a function running on another client, use self.broadcast():

    await self.request("<subscription tag>", "<name of function>", *args)

To subscribe to a new tag, call the subscribe function:

    await self.request("subscribe", "clinet1")
