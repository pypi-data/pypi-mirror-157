import string
import random


def genPass(length=10):
    characters = list(string.ascii_letters + string.digits + '!@£$-*(')
    random.shuffle(characters)

    password = []
    for i in range(length):
        password.append(random.choice(characters))

    random.shuffle(password)

    for i in range(len(password)):
        password[i] = password[i].lower()

    return (''.join(password))


def genKey(length=10):
    keyChar = list(string.ascii_letters + string.digits + '-')
    random.shuffle(keyChar)

    key = []
    for i in range(length):
        key.append(random.choice(keyChar))

    random.shuffle(key)

    for i in range(len(key)):
        key[i] = key[i].lower()

    return (''.join(key))


def pickRan(list, length=1):
    random.shuffle(list)

    key = []
    for i in range(length):
        key.append(random.choice(list))

    random.shuffle(key)

    return (''.join(key))


def incrypt(password):
    words = ''
    unknown = ''
    a = 'shg¢'
    b = 'hnj£'
    c = 'ki*('
    d = 'dfk%'
    e = 'sy^&'
    f = 'kd*('
    g = 'kai%'
    h = 'qis$'
    i = 's^&%'
    j = '*^££'
    k = 'n)**'
    l = 'j(*£'
    m = 'b!@£'
    n = 'o*&#'
    o = 'fhdn'
    p = 'm¡€#'
    q = 'dnc¡'
    r = 'zz$%'
    s = 'cn§∞'
    t = 'bd#€'
    u = 'jn%$'
    v = 'c£$*'
    w = 'sp#€'
    x = 'j^&&'
    y = '^&&*'
    z = '¢~)~'
    alert = 'nh@£'
    dash = 'lk&*'
    col = 'bv^&'
    star = 'sgt$'
    dollar = '&^%$'
    eee = 'lk!@'
    at = 'ta><'
    one = 'nhj2'
    two = 'mk8&'
    three = 'qt$5'
    four = 'lmc('
    five = 'ncm_'
    six = '^&45'
    seven = 'lm1@'
    eight = 'nv*9'
    nine = 'as%4'
    zero = 'cxd£'

    for num in password:
        if num == 'a':
            words += a
        elif num == 'b':
            words += b
        elif num == 'c':
            words += c
        elif num == 'd':
            words += d
        elif num == 'e':
            words += e
        elif num == 'f':
            words += f
        elif num == 'g':
            words += g
        elif num == 'h':
            words += h
        elif num == 'i':
            words += i
        elif num == 'j':
            words += j
        elif num == 'k':
            words += k
        elif num == 'l':
            words += l
        elif num == 'm':
            words += m
        elif num == 'n':
            words += n
        elif num == 'o':
            words += o
        elif num == 'p':
            words += p
        elif num == 'q':
            words += q
        elif num == 'r':
            words += r
        elif num == 's':
            words += s
        elif num == 't':
            words += t
        elif num == 'u':
            words += u
        elif num == 'v':
            words += v
        elif num == 'w':
            words += w
        elif num == 'x':
            words += x
        elif num == 'y':
            words += y
        elif num == 'z':
            words += z
        elif num == '!':
            words += alert
        elif num == '@':
            words += at
        elif num == '$':
            words += dollar
        elif num == '-':
            words += dash
        elif num == '*':
            words += star
        elif num == '(':
            words += col
        elif num == '£':
            words += eee
        elif num == '1':
            words += one
        elif num == '2':
            words += two
        elif num == '3':
            words += three
        elif num == '4':
            words += four
        elif num == '5':
            words += five
        elif num == '6':
            words += six
        elif num == '7':
            words += seven
        elif num == '8':
            words += eight
        elif num == '9':
            words += nine
        elif num == '0':
            words += zero
        else:
            unknown += num

    if len(unknown) > 1:
        print('Unknown Values in Password : ', unknown, ' !!WARNING!! UNKNOWN VALUES CANT BE CHANGED BACK TO NORMAL')

    return words


def desIncrypt(password):
    words = ''
    unknown = ''
    a = 'shg¢'
    b = 'hnj£'
    c = 'ki*('
    d = 'dfk%'
    e = 'sy^&'
    f = 'kd*('
    g = 'kai%'
    h = 'qis$'
    i = 's^&%'
    j = '*^££'
    k = 'n)**'
    l = 'j(*£'
    m = 'b!@£'
    n = 'o*&#'
    o = 'fhdn'
    p = 'm¡€#'
    q = 'dnc¡'
    r = 'zz$%'
    s = 'cn§∞'
    t = 'bd#€'
    u = 'jn%$'
    v = 'c£$*'
    w = 'sp#€'
    x = 'j^&&'
    y = '^&&*'
    z = '¢~)~'
    alert = 'nh@£'
    dash = 'lk&*'
    col = 'bv^&'
    star = 'sgt$'
    dollar = '&^%$'
    eee = 'lk!@'
    at = 'ta><'
    one = 'nhj2'
    two = 'mk8&'
    three = 'qt$5'
    four = 'lmc('
    five = 'ncm_'
    six = '^&45'
    seven = 'lm1@'
    eight = 'nv*9'
    nine = 'as%4'
    zero = 'cxd£'

    passer = [password[i:i + 4] for i in range(0, len(password), 4)]
    for num in passer:
        if num == a:
            words += 'a'
        elif num == b:
            words += 'b'
        elif num == c:
            words += 'c'
        elif num == d:
            words += 'd'
        elif num == e:
            words += 'e'
        elif num == f:
            words += 'f'
        elif num == g:
            words += 'g'
        elif num == h:
            words += 'h'
        elif num == i:
            words += 'i'
        elif num == j:
            words += 'j'
        elif num == k:
            words += 'k'
        elif num == l:
            words += 'l'
        elif num == m:
            words += 'm'
        elif num == n:
            words += 'n'
        elif num == o:
            words += 'o'
        elif num == p:
            words += 'p'
        elif num == q:
            words += 'q'
        elif num == r:
            words += 'r'
        elif num == s:
            words += 's'
        elif num == t:
            words += 't'
        elif num == u:
            words += 'u'
        elif num == v:
            words += 'v'
        elif num == w:
            words += 'w'
        elif num == x:
            words += 'x'
        elif num == y:
            words += 'y'
        elif num == z:
            words += 'z'
        elif num == alert:
            words += '!'
        elif num == at:
            words += '@'
        elif num == dollar:
            words += '$'
        elif num == dash:
            words += '-'
        elif num == star:
            words += '*'
        elif num == col:
            words += '('
        elif num == eee:
            words += '£'
        elif num == one:
            words += '1'
        elif num == two:
            words += '2'
        elif num == three:
            words += '3'
        elif num == four:
            words += '4'
        elif num == five:
            words += '5'
        elif num == six:
            words += '6'
        elif num == seven:
            words += '7'
        elif num == eight:
            words += '8'
        elif num == nine:
            words += '9'
        elif num == zero:
            words += '0'

    return words


