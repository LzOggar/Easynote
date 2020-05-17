from Crypto.Cipher import AES
from Crypto import Random

class AdvancedEncryptionStandard(object):
    """
        AdvancedEncryptionStandard class.
    """

    def __init__(self, key):
        """
            __init__ function.
            :param key: symetric key. Must be <bytes>.
        """

        self.key = key

    def pad(self, s):
        """
            pad function. Complete with null bytes the string.
            :param s: string. Must be <bytes>.
            :return: <bytes> completed with null bytes.
            :rtype: <bytes>
        """

        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, plaintext):
        """
            encrypt function. Encrypt a plain text with AES CBC algorithm.
            :param plaintext: plain text to encrypt. Must be <bytes>
            :return: encrypted string.
            :rtype: <bytes>
        """

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(self.pad(plaintext))

    def decrypt(self, ciphertext):
        """
            decrypt function. Decrypt a cipher text with AES CBC algorithm.
            :param ciphertext: ciphertext to decrypt. Must be <bytes>.
            :return: decrypted string.
            :rtype: <bytes>
        """

        iv = ciphertext[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")
