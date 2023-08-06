Rsacrack is a library to carck rsa.

**Install**

Stable Version:
```shell
pip install -U rsacrack
```
Beta Version:
```shell
pip install --pre -U rsacrack
```

**[Usage]**
```python
from rsacrack import crack_key
from rsa import newkeys, encrypt, decrypt, PublicKey, PrivateKey
from secrets import choice
from string import printable
from binascii import b2a_hex

key = newkeys(90)
pub_key = eval(str(key[0]).split('PublicKey')[1])
msg = choice(printable).encode('ascii')
encrypted = encrypt(msg, key[0])

priv_key = crack_key(pub_key)
hacked = decrypt(encrypted, PrivateKey(*priv_key)).decode('utf-8')
print(f'Plain Text: {msg.decode()}')
print(f'Cipher Text (HEX): {b2a_hex(encrypted).decode()}')
print(f'Hacked Plain Text: {hacked}')
```