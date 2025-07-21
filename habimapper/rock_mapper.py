'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys
from os import cpu_count

#=======================================================================
def do_work(
            inDir: str,
            outDirTop: str,
            projName: str,
            epsg: int,
            windowSize_m: tuple,
            window_stride: int,
            minArea_percent: float,
            threadCnt: float
        ):
    '''
    '''

    if not os.path.exists(outDirTop):
        os.makedirs(outDirTop)

    ###############################################
    # Specify multithreaded processing thread count
    if threadCnt==0: # Use all threads
        threadCnt=cpu_count()
    elif threadCnt<0: # Use all threads except threadCnt; i.e., (cpu_count + (-threadCnt))
        threadCnt=cpu_count()+threadCnt
        if threadCnt<0: # Make sure not negative
            threadCnt=1
    elif threadCnt<1: # Use proportion of available threads
        threadCnt = int(cpu_count()*threadCnt)
        # Make even number
        if threadCnt % 2 == 1:
            threadCnt -= 1
    else: # Use specified threadCnt if positive
        pass

    if threadCnt>cpu_count(): # If more than total avail. threads, make cpu_count()
        threadCnt=cpu_count();
        print("\nWARNING: Specified more process threads then available, \nusing {} threads instead.".format(threadCnt))

    return