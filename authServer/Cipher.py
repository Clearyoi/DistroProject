def encrypt(string, key):
    newString = ""
    for symbol in string:
        if symbol.isalpha():
            num = ord(symbol)
            num += key

            if symbol.isupper():
                if num > ord('Z'):
                    num -= 26
                elif num < ord('A'):
                    num += 26
            elif symbol.islower():
                if num > ord('z'):
                    num -= 26
                elif num < ord('a'):
                    num += 26

            newString += chr(num)
        else:
            newString += symbol
    return newString


def decrypt(string, key):
    newString = ""
    newString = ""
    for symbol in string:
        if symbol.isalpha():
            num = ord(symbol)
            num -= key

            if symbol.isupper():
                if num > ord('Z'):
                    num -= 26
                elif num < ord('A'):
                    num += 26
            elif symbol.islower():
                if num > ord('z'):
                    num -= 26
                elif num < ord('a'):
                    num += 26

            newString += chr(num)
        else:
            newString += symbol
    return newString
