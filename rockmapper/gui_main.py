
'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys
import time, datetime

start_time = time.time()

def gui():
    '''
    '''

    #################
    # NEED TO ADD GUI


    # FOR DEVELOPMENT
    #############################
    # Hard coding for development
    seg_model = 'rock_mapper'
    # inDir = r'D:\scratch\USGS-CERC_2025\00_carp_group_targets\Mosaics'
    # modelDir = r'D:\scratch\202506_BrushyDeepKiamichi_Substrate\seg_gym\20250628_test\fold_0'
    # inDir = r'C:\Users\cbodine\Desktop\NewMapWorkflow\scratch\USGS-CERC_2025\00_carp_group_targets\Mosaics'
    # modelDir = r'C:\Users\cbodine\Desktop\NewMapWorkflow\scratch\202506_BrushyDeepKiamichi_Substrate\seg_gym\20250628_test\fold_0'
    inDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\mosaics'
    modelDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\seg_gym\20250628_test\fold_0\RockMapper'
    mosaicFileType = '.tif'
    outDirTop = r'Z:\scratch'
    projName = 'HabiMapper_Test_idx_DL_weights'

    epsg = 32616

    windowSize_m = (18, 18)
    window_stride = 6
    minArea_percent = 0.5
    threadCnt = 0.10

    predBatchSize = 30


    ################
    # Run HabiMapper

    # RockMapper
    if seg_model == 'rock_mapper':
        from rockmapper.rock_mapper import do_work

        print('\n\nMapping habitat with ROCKMAPPER model...\n\n')
        do_work(
            inDir = inDir,
            outDirTop = outDirTop,
            projName = projName,
            epsg = epsg,
            windowSize_m = windowSize_m,
            window_stride = window_stride,
            minArea_percent = minArea_percent,
            threadCnt = threadCnt,
            mosaicFileType=mosaicFileType, 
            modelDir=modelDir,
            predBatchSize=predBatchSize,
        )





    print("\n\nGrand Total Processing Time: ", datetime.timedelta(seconds = round(time.time() - start_time, ndigits=0)))
    return
