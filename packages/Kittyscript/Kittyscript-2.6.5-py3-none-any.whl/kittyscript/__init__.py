import random

def say(Print):
    print(Print)

def addnum(x, y):
    print(x + y)

def addfloat(f1, f2):
    print(f1+ f2)

def Divide(a, b):
    print(a / b)

def genaratenumber():
    x = random.randint(1,9999999999)

    print(x)

Pi = 3.1415926535897932384626433832795028841971693993751058209749445923078164062

def version():
    print("v2.6.5 orange-boat")

def CreateFile(name, content):
    with open(name, 'w') as foo:
        foo.write(content)