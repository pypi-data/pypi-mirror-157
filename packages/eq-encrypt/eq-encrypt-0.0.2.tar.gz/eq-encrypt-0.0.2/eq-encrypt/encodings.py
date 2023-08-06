import base64


class B64Decrypt(object):

    def encrypt(self, pwd):
        pwd_bytes = pwd.encode('ascii')
        b64_bytes = base64.b64encode(pwd_bytes)
        return b64_bytes.decode('ascii')

    def decrypt(self, pwd):
        b64_bytes = pwd.encode('ascii')
        msg_bytes = base64.b64decode(b64_bytes)
        return msg_bytes.decode('ascii')
