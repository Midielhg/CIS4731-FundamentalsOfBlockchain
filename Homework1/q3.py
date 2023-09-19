# 3. (35 points) The following Python function encrypt implements the following symmetric encryption algorithm which accepts a shared 8-bit key (integer from 0-255):

# breaks the plaintext into a list of characters
# places the ASCII code of every four consecutive characters of the plaintext into a single word (4-bytes) packet
# If the length of plaintext is not divisible by 4, it adds white-space characters at the end to make the total length divisible by 4
# encrypt each packet by finding the bit-wise exclusive-or of the packet and the given key after extending the key. For example, if the key is 0x4b, the extended key is 0x4b4b4b4b
# each packet gets encrypted separately, but the results of encrypting packets are concatenated together to generate the ciphertext.
def make_block(lst):
    return (ord(lst[0])<<24) + (ord(lst[1])<<16) + (ord(lst[2])<<8) + ord(lst[3])

def encrypt(message, key):
    rv = ""
    l = list(message)
    n = len(message)
    blocks = []
    for i in range(0,n,4):# break message into 4-character blocks
        if i+4 <= n:
            blocks.append(make_block(l[i: i+4]))
        else:# pad end of message with white-space if the lenght is not divisible by 4
            end = l[i:n]
            end.extend((i+4-n)*[' '])
            blocks.append(make_block(end))
    extended_key = (key << 24) + (key << 16) + (key << 8) + (key)
    for block in blocks:#encrypt each  block separately
        encrypted = str(hex(block ^ extended_key))[2:]
        for i in range(8 - len(encrypted)):
            rv += '0'
        rv += encrypted
    return rv

# a) implement the decrypt function that gets the ciphertext and the key as input and returns the plaintext as output.
def decrypt(ciphertext, key):
    rv = ""
    extended_key = (key << 24) + (key << 16) + (key << 8) + (key)
    for i in range(0, len(ciphertext), 8): # break ciphertext into 8-character blocks
        block = int(ciphertext[i:i+8], 16)
        decrypted = block ^ extended_key
        for j in range(3,-1,-1): # extract each byte from the decrypted block
            char = chr((decrypted >> (j * 8)) & 0xff)
            rv += char
    return rv
  

# b) If we know that the following ciphertext is the result of encrypting a single meaningful English word with some key, find the key and the word: 10170d1c0b17180d10161718151003180d101617

f = open("dict.txt", 'r')

words = f.readlines()
stripped_words = []
for word in words:
    stripped_words.append(word[:-1])

ciphertext = "10170d1c0b17180d10161718151003180d101617"
for key in range(256):
  if decrypt(ciphertext, key) in stripped_words:
      print(hex(key), decrypt(ciphertext, key))
