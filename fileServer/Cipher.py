def encrypt(string, key):
    newString = ""
    for c in string:
        newString += chr(ord(c) + key)
    return newString


def decrypt(string, key):
    newString = ""
    for c in string:
        newString += chr(ord(c) - key)
    return newString
