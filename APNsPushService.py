from struct import pack, unpack
from binascii import a2b_hex, b2a_hex
import time

from tornado.netutil import TCPServer

def packed_uchar(num):
    return pack('>B', num)

def packed_ushort_big_endian(num):
    return pack('>H', num)

def unpacked_ushort_big_endian(bytes):
    return unpack('>H', bytes)[0]

def packed_uint_big_endian(num):
    return pack('>I', num)

def unpacked_uint_big_endian(bytes):
    return unpack('>I', bytes)[0]

def gen_token():
    token_list=[]
    for i in range(0, 10000):
        token_bin = packed_uint_big_endian(i)
        token = b2a_hex(token_bin)
        token_list.append(token)

    return token_list

TOKEN_LIST = gen_token()

class APNsPushService(TCPServer):

    def __init__(self, 
                cert_file, 
                key_file,
                **kwargs):

        TCPServer.__init__(self, 
                    ssl_options={"keyfile": key_file,
                                "certfile": cert_file}, 
                    **kwargs)

    def handle_stream(self, stream, address):
        print 'accept connect %s:%s' % (address[0],address[1])
        APNsTestConnection(stream, address)

class APNsTestConnection(object):

    def __init__(self, stream, address):
        self.stream = stream
        self.address = address
        self.buff = ''
        self.stream.read_until_close(callback=self._read_callback,
                                    streaming_callback=self._read_callback)

    def _read_callback(self, data):
        
        self.buff += data

        while len(self.buff) > 11:
            
            command = b2a_hex(self.buff[0])
            identifier = unpacked_uint_big_endian(self.buff[1:5])
            expiry = unpacked_uint_big_endian(self.buff[5:9])
            token_length = unpacked_ushort_big_endian(self.buff[9:11])

            bytes_to_token = 11+token_length

            if len(self.buff) >= bytes_to_token +2 :

                token = b2a_hex(self.buff[11:bytes_to_token])

                payload_length = \
                    unpacked_ushort_big_endian(
                            self.buff[bytes_to_token:bytes_to_token+2])

                bytes_to_payload=bytes_to_token + 2 + payload_length

                if len(self.buff) >= bytes_to_payload:

                    payload = self.buff[(bytes_to_token + 2):bytes_to_payload]

                    self._parse_data(identifier, expiry, token, payload)

                    self.buff = self.buff[bytes_to_payload:]

                else:
                    return

            else:
                return

    def _parse_data(self, identifier, expiry, token, payload):
        print 'Receive a message seq %s t %s token %s payload %s' %\
                (identifier, expiry, token, payload)

        if token not in TOKEN_LIST:
            status = '08'
            self._write_error_response(identifier, status)

    def _write_error_response(self, identifier, status):
        if not self.stream.closed():
            print 'write error'
            identifier_bin = packed_uint_big_endian(identifier)
            status_bin = a2b_hex(status)
            data = a2b_hex('08')+ status_bin + identifier_bin
            self.stream.write(data, self._on_write_complete)

    def _on_write_complete(self):
        self.stream.close()
        if self.stream.closed():
            print 'closed'

