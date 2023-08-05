import string
import random

characters = list(string.ascii_letters + string.digits + '!@£$%^&*()_+}{:"|?><€#,./;§±')
passChar = list(string.ascii_letters + string.digits)


def genPass(length=10):
    random.shuffle(characters)

    password = []
    for i in range(length):
        password.append(random.choice(characters))

    random.shuffle(password)

    return (''.join(password))


def genKey(length=10):
    random.shuffle(passChar)

    key = []
    for i in range(length):
        key.append(random.choice(passChar))

    random.shuffle(key)

    return (''.join(key))


def pickRan(list, length=1):
    random.shuffle(list)

    key = []
    for i in range(length):
        key.append(random.choice(list))

    random.shuffle(key)

    return (''.join(key))
