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

def videoplayer(url):
    com_1_tup = 'omxplayer -b "', url, '"'
    com_1 = conTup_1(com_1_tup)
    
    out = os.popen(com_1)
    return out.read()

videoplayer('https://rr5---sn-5uaeznr6.googlevideo.com/videoplayback?expire=1643521676&ei=LNL1Yf-dFsvQ4QT0vrGgDw&ip=2600%3A1700%3A1e10%3A6030%3A0%3A0%3A0%3A5e5&id=o-AAH4uqHFJUVZ0-zax7ENpexYl2k79gV_OnWwjFOzeEqC&itag=22&source=youtube&requiressl=yes&mh=J6&mm=31%2C29&mn=sn-5uaeznr6%2Csn-5ualdnee&ms=au%2Crdu&mv=m&mvi=5&pl=40&initcwndbps=1255000&vprv=1&mime=video%2Fmp4&ns=lGj_4IHZi9qtoxqkBCpvBNUG&cnr=14&ratebypass=yes&dur=196.603&lmt=1576475905515312&mt=1643499647&fvip=5&fexp=24001373%2C24007246&c=WEB&txp=5535432&n=rxB19o-VrgwN6y74TJV&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Ccnr%2Cratebypass%2Cdur%2Clmt&sig=AOq0QJ8wRQIgMQbQyjSI5zPOFb7p7XPz9K23ADYkz2o4D-fugEDKPScCIQDjcv_l7YGhNbvVQCTMdxshOU3mKDBqnlQka2mZzSiU5g%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgJXZDmHPgKl3NLWWswovq-d_2DVUvtzhKBdsqyS_YWY8CIQCShj2HjDmo21zLtoz1DGYeKFXgH8XqM6VsVr87micE3A%3D%3D')