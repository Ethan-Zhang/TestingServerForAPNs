from struct import pack
from binascii import a2b_hex
import time

from tornado.netutil import TCPServer

def packed_ushort_big_endian(num):
    return pack('>H', num)

def packed_uint_big_endian(num):
    return pack('>I', num)

def Generate_FeedBackData(num):

    FeedBackData = ''
    for i in range(0,num):
        expire = int(time.time()+i*300) 
        expire_bin = packed_uint_big_endian(expire)
        token_bin = packed_ushort_big_endian(i)
        token_length_bin = packed_ushort_big_endian(len(token_bin))
        FeedBackData = FeedBackData + expire_bin + token_length_bin + token_bin

    return FeedBackData

class APNsFeedBackService(TCPServer):

    def __init__(self, 
                cert_file, 
                key_file,
                data_num, 
                **kwargs):

        self.data_num = data_num
        TCPServer.__init__(self, 
                    ssl_options={"keyfile": key_file,
                                "certfile": cert_file}, 
                    **kwargs)

    def handle_stream(self, stream, address):
        FeedBackConnection(self.data_num, stream, address)

class FeedBackConnection(object):

    def __init__(self, data_num, stream, address):
        self.data_num = data_num
        self.stream = stream
        self.address = address
        self.write_feedback()

    def write_feedback(self):
        if not self.stream.closed():
            data = Generate_FeedBackData(self.data_num)
            self.stream.write(data, self._on_write_complete)

    def _on_write_complete(self):
        self.stream.close()
        if self.stream.closed():
            print 'closed'

