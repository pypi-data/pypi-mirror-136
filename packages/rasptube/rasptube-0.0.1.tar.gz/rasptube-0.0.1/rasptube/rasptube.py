import os

def conTup_1(tup):
    com_1 = ''
    for item in tup:
        com_1 = com_1 + item
    return com_1

def conTup_2(tup):
    com_2 = ''
    for item in tup:
        com_2 = com_2 + item
    return com_2
def linkgen(url):
    com_1_tup = 'sudo youtube-dl -g -f 22 "', url, '"'
    com_1 = conTup_1(com_1_tup)

    out = os.popen(com_1)
    return out.read()
