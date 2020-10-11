# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet

# Fernet гарантирует, что сообщение, зашифрованное с его помощью, не может быть обработано или прочитано без ключа.
# Fernet -это реализация симметричной (также известной как "секретный ключ") аутентифицированной криптографии.
#
# https://cryptography.io/en/latest/fernet/

KEY = b'SsBaCvNd8hIYKAj9Z_EfqkXoBXkwLbBrBT_Q9PM0x8E='


def encrypt_string(string, key):
    cipher_suite = Fernet(key)
    encoded_text = cipher_suite.encrypt(string.encode(encoding="utf-8"))
    return encoded_text.decode(encoding="utf-8")


def decrypt_string(string, key):
    cipher_suite = Fernet(key)
    decoded_text = cipher_suite.decrypt(string.encode(encoding="utf-8"))
    return decoded_text.decode(encoding="utf-8")


def main():
    s = "hello world!"
    for i in range(4):
        enc_s = encrypt_string(s, KEY)
        dec_s = decrypt_string(enc_s, KEY)
        print(enc_s)


if __name__ == '__main__':
    main()
