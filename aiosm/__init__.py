"""An asynchronous network hub

todo:
    revise Radio to use custom sockets
        create Radio using asyncio.create_datagram_endpoint() (aka UDP)
    revert to using headers
        use EOF marked for header?
    make encoder/decoder modules
        make protobuf encoder/decoders
    revise node communication
        replace JSON reliance with encoder/decoder module support
            perhaps an intermediate higher level interface for utility functions
    retest with JazZy
    implement heartbeat
        checking if a connection is still alive
    remember what old notes meant:
        implement inheritable class structure for client side to represent a node with header functions for RPC

"""

__version__ = '0.0.6'

from .__main__ import run_host
