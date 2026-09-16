# pip install "pwdlib[argon2]"
from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()
hashed = password_hash.hash("test")
print(hashed)
print(password_hash.verify("1234", hashed) )