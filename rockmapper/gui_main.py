
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
    # seg_model = 'RockMapper_20250628_v1'
    inDir = r'D:\scratch\202511_BrushDeepKiamichi_SubstrateShadow'
    mosaicFileType = '.tif'
    outDirTop = r'Z:\scratch'
    projName = 'RockMapper'
    mapRast = False
    mapShp = True

    epsg = 32615

    windowSize_m = (18, 18)
    window_stride = 6
    minArea_percent = 0.1
    threadCnt = 0.75

    predBatchSize = 30

    minPatchSize_m2 = 18 # Minimum patch size to keep in final shapefile, in square meters
    smoothShp = True # Smooth final shapefile polygons
    smoothTol_m = 0.25 # Smoothing tolerance in meters, higher = more smoothing

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
        deleteIntData=deleteIntData,
        minPatchSize = minPatchSize_m2,
        smoothShp = smoothShp,
        smoothTol_m = smoothTol_m,
    )





    print("\n\nGrand Total Processing Time: ", datetime.timedelta(seconds = round(time.time() - start_time, ndigits=0)))
    return

if __name__ == "__main__":
    gui()
