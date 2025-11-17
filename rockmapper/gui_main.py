
'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys
import time, datetime

start_time = time.time()

# Set ROCKMAPPER utils dir
USER_DIR = os.path.expanduser('~')
GV_UTILS_DIR = os.path.join(USER_DIR, '.rockmapper')
if not os.path.exists(GV_UTILS_DIR):
    os.makedirs(GV_UTILS_DIR)

def gui():
    '''
    '''

    #################
    # NEED TO ADD GUI


    # FOR DEVELOPMENT
    #############################
    # Hard coding for development
    seg_model = 'RockMapper_20251117_v2'
    inDir = r'D:\scratch\202511_BrushDeepKiamichi_SubstrateShadow'
    # modelDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\seg_gym\20250628_test\fold_0\RockMapper'
    # inDir = r'Z:\scratch\USGS-CERC_2025\00_carp_group_targets\Mosaics'
    # modelDir = r'D:\redbo_science\projects\USGS-CERC_2025\seg_gym\20250710_v01\fold_0'
    mosaicFileType = '.tif'
    outDirTop = r'Z:\scratch'
    projName = 'RockMapperTest_24_24'
    mapRast = False
    mapShp = True

    epsg = 32615

    windowSize_m = (24, 24)
    window_stride = 9
    minArea_percent = 0.5
    threadCnt = 0.25

    predBatchSize = 30

    deleteIntData = True


    ################
    # Run HabiMapper

    modelDir = os.path.join(GV_UTILS_DIR, 'models')

    # RockMapper
    if seg_model == 'RockMapper_20250628_v1':
        modelDir = os.path.join(modelDir, seg_model)
    elif seg_model == 'RockMapper_20251117_v2':
        modelDir = os.path.join(modelDir, seg_model)
    else:
        raise ValueError('seg_model not recognized: {}'.format(seg_model))

    from rockmapper.rock_mapper import do_work
    print('\n\nMapping habitat with ROCKMAPPER model...\n\n')
    do_work(
        inDir = inDir,
        outDirTop = outDirTop,
        projName = projName,
        mapRast = mapRast,
        mapShp = mapShp,
        epsg = epsg,
        windowSize_m = windowSize_m,
        window_stride = window_stride,
        minArea_percent = minArea_percent,
        threadCnt = threadCnt,
        mosaicFileType=mosaicFileType, 
        modelDir=modelDir,
        predBatchSize=predBatchSize,
        deleteIntData=deleteIntData
    )





    print("\n\nGrand Total Processing Time: ", datetime.timedelta(seconds = round(time.time() - start_time, ndigits=0)))
    return
