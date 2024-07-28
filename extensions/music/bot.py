from disnake.ext.commands import InteractionBot
# from mafic import NodePool

# from config import NODES


class LapisBot(InteractionBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #     self.pool = NodePool(self)
    #     self.loop.create_task(self.add_nodes())

    # async def add_nodes(self):
    #     for node in NODES:
    #         await self.pool.create_node(**node)
