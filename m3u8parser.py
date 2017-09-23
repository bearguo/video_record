import urllib.request as ul

class TSFile():
    def __init__(self,inf,name):
        self.inf = inf
        self.name = name
        self.index = int(name[name.find("-")+1:name.find(".")])

    def __str__(self):
        return self.name + ' ' + str(self.inf)

def getM3U8(url):
    # f = ul.urlopen(url)

    # fout = open('stream1.m3u8', 'wb')
    # fout.writelines(f)
    # fout.close()

    ret = []
    try:
        f = ul.urlopen(url)
        line = f.readline()

        while line != b"":
            # print(str(line))
            line = f.readline()
            if str(line).__contains__("#EXTINF:"):
                inf = str(line)
                name = str(f.readline())
                tsFile = TSFile(inf[inf.find(":") + 1:inf.__len__() - 3], name[2:name.__len__() - 3])
                ret.append(tsFile)
                # print(tsFile.inf + '  ' +  tsFile.name + '  ' +  str(tsFile.index))
    finally:
        pass


    return ret

def getTS(url):
    f = None
    try:
        f = ul.urlopen(url)
    finally:
        pass

    return f


if __name__ == '__main__':
    # list = getM3U8("http://1.8.203.198/live/stream1.m3u8")
    # # fout = open("1min.ts",'wb')
    # for file in list:
    #     fout = open(file.name, 'wb')
    #     fout.writelines(getTS("http://1.8.203.198/live/" + file.name))
    #     fout.close()

    f = ul.urlopen("http://1.8.203.198/live/stream1.m3u8")
    fout = open('stream1.m3u8', 'wb')
    fout.writelines(f)
    fout.close()

    list = getM3U8("http://1.8.203.198/live/stream1.m3u8")

    for i in list:
        print(i)



    for file in list:
        for file in list:
            fout = open(file.name,'wb')
            fout.writelines(getTS("http://1.8.203.198/live/" + file.name))
            fout.close()





