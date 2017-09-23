import os
import time
import multiprocessing
from ctypes import *

# def Sub():
#     print("sub pid : %s" % os.getpid())
#
#     try:
#         while True:
#             time.sleep(2)
#         pass
#     finally:
#         print("sub finally called")

if __name__ == "__main__":

    # print("main pid : %s" % os.getpid())
    #
    # time.sleep(2)
    #
    # process = multiprocessing.Process(target=Sub)
    # process.start()
    #
    # while True:
    #     time.sleep(3)
    #
    # # process = channel_map[channel_id]
    # process.terminate()
    # print('kill sub ')
    # process.join()

    libtest = cdll.LoadLibrary('./libUDP2HLS.so.1.0.0')


    libtest.dump.argtype = [c_int,c_char_p,c_int]
    dump = libtest.dump
    res = dump(10002,'./CCTV1'.encode(),60)
    print(res)

    while True:
        time.sleep(10)

    pass