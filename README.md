# RockMapper

# 🚧**UNDER CONSTRUCTION**🚧

[![PyPI - Version](https://img.shields.io/pypi/v/rockmapper?style=flat-square&label=Latest%20Version%20(PyPi))](https://pypi.org/project/rockmapper/)
[![GitHub last commit](https://img.shields.io/github/last-commit/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/commits)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/commits)
[![GitHub](https://img.shields.io/github/license/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/blob/main/LICENSE)


Interface for predicting and mapping benthic habitat (substrates) from any side-scan sonar mosaic. 

## Overview

`RockMapper` is an open-source Python interface for automatically predicting and mapping substrate types from and side-scan sonar mosaic(s). `RockMapper` leverages SegFormer pre-trained models fine-tuned with [Segmentation Gym](https://github.com/Doodleverse/segmentation_gym) to automatically predict Paddlefish spawning habitat (manuscript forthcoming).

## Published Documentation

### Journal Article

Wolfenkoehler, Bodine, Long (*forthcoming...*)

## Installation

1. Install [`Miniforge`](https://conda-forge.org/download/).
2. Open the [`Miniforge`](https://conda-forge.org/download/) prompt.
3. Install `PINGInstaller`:
    ```
    pip install --force-reinstall pinginstaller
    ```
4. Install `RockMapper`.
    ```
    python -m pinginstaller rockmapper
    ```

## Usage

1. Copy the following script to some location on your computer:

```python


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
    # Update Parameters
    seg_model = 'RockMapper_20250628_v1' # Don't update
    inDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\mosaics'
    mosaicFileType = '.tif'
    outDirTop = r'Z:\scratch'
    projName = 'RockMapperTest'
    mapRast = False
    mapShp = True

    epsg = 32615

    windowSize_m = (18, 18)
    window_stride = 9
    minArea_percent = 0.75
    threadCnt = 0.25

    predBatchSize = 30

    deleteIntData = True


    ################
    # Run HabiMapper

    modelDir = os.path.join(GV_UTILS_DIR, 'models')

    # RockMapper
    if seg_model == 'RockMapper_20250628_v1':
        from rockmapper.rock_mapper import do_work

        modelDir = os.path.join(modelDir, seg_model)


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
```

2. Open the file with [Visual Studio Code](https://code.visualstudio.com/).
3. Update the Parameters as necessary:

```python
# Update Parameters
seg_model = 'RockMapper_20250628_v1' # Don't update
inDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\mosaics'
mosaicFileType = '.tif'
outDirTop = r'Z:\scratch'
projName = 'RockMapperTest'
mapRast = False
mapShp = True

epsg = 32616

windowSize_m = (18, 18)
window_stride = 9
minArea_percent = 0.75
threadCnt = 0.25

predBatchSize = 30

deleteIntData = True
```

4. Ensure the `rockmapper` environment is selected as the Interpreter [see this](https://stackoverflow.com/a/76289404).
5. Run the script in debug mode by pressing `F5`.
