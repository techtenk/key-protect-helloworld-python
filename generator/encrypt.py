from Crypto.Cipher import AES
from Crypto import Random

BLOCK_SIZE = 16
PADDING = '{'
pad = lambda s: s + ((BLOCK_SIZE - len(s)) % BLOCK_SIZE * PADDING)


key = b'super secret key'
iv = Random.new().read(AES.block_size)
print len(iv)
with open('iv.txt', 'w') as ff:
    ff.write(iv)


with open('iv.txt', 'r') as fiv:
    new_iv = fiv.read()
    print len(new_iv)

cipher = AES.new(key, AES.MODE_CFB, iv)

secretMsg = []
# with open("Warren Buffett - 2015 Letter to Shareholders.txt", 'r') as f:
#     secretMsg.append(cipher.encrypt(f.read()))
with open("helpers_do_not_publish/Simple Message.txt", 'r') as f:
    secretMsg.append(cipher.encrypt(f.read()))


with open("secret message.txt", 'w') as f2:
    for block in secretMsg:
        f2.write(block)

decryptedMsg  = []

cipher2 = AES.new(key, AES.MODE_CFB, iv)

with open("secret message.txt", 'r') as f3:
    decryptedMsg.append(cipher2.decrypt(f3.read()))

with open("revealed message.txt", 'w') as f4:
    for block in decryptedMsg:
        f4.write(block)
