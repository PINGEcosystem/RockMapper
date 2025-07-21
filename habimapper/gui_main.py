
'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys
import time

start_time = time.time()

def gui():
    '''
    '''

    #################
    # NEED TO ADD GUI


    #############################
    # Hard coding for development
    seg_model = 'rock_mapper'
    inDir = r'D:\scratch\USGS-CERC_2025\00_carp_group_targets\Mosaics'
    outDirTop = r'C:\Users\cbodine\Downloads'
    projName = 'HabiMapper_Test'

    epsg = 32616

    windowSize_m = (30, 30)
    window_stride = 6
    minArea_percent = 0.5
    threadCnt = 0.5


    ################
    # Run HabiMapper

    # RockMapper
    if seg_model == 'rock_mapper':
        from habimapper.rock_mapper import do_work

        print('\n\nMapping habitat with ROCKMAPPER model...\n\n')
        do_work(
            inDir = inDir,
            outDirTop = outDirTop,
            projName = projName,
            epsg = epsg,
            windowSize_m = windowSize_m,
            window_stride = window_stride,
            minArea_percent = minArea_percent,
            threadCnt = threadCnt
        )





    print("\n\nGrand Total Processing Time: ",datetime.timedelta(seconds = round(time.time() - start_time, ndigits=0)))
    return
