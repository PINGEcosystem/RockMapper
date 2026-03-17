# <img width="100" height="100" alt="1FAA8_color" src="https://github.com/user-attachments/assets/b79cfeb7-396e-42ae-9867-8abff79679f2" /> RockMapper


# 🚧**UNDER CONSTRUCTION-GUI Forthcoming**🚧

[![PyPI - Version](https://img.shields.io/pypi/v/rockmapper?style=flat-square&label=Latest%20Version%20(PyPi))](https://pypi.org/project/rockmapper/)
[![GitHub last commit](https://img.shields.io/github/last-commit/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/commits)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/commits)
[![GitHub](https://img.shields.io/github/license/PINGEcosystem/GhostVision)](https://github.com/PINGEcosystem/GhostVision/blob/main/LICENSE)


Interface for predicting and mapping benthic habitat (substrates) from any side-scan sonar mosaic. 

## Overview

`RockMapper` is an open-source Python interface for automatically predicting and mapping rock from any side-scan sonar mosaic(s). `RockMapper` leverages SegFormer pre-trained models fine-tuned with [Segmentation Gym](https://github.com/Doodleverse/segmentation_gym) to automatically classify "rocky" substrate- defined as any hard particle greater than 2 mm in size. `RockMapper` uses the Udden-Wentworth grain size scale when classifying substrate into four classes: other (fines <2mm), gravel (2mm - 64mm), boulder/cobble (>64mm ), and bedrock (unfractured hard substrates) (Wentworth 1922).

## Published Documentation

### Journal Article

Wolfenkoehler, W. A., Bodine, C. S., & Long, J. M. (forthcoming). Evaluating `RockMapper`: A software to automatically map aquatic substrate from sonar images.

In this study `RockMapper` was evaluated by comparing output maps to those made by manual methods, allowing future substrate delineators to better understand the potential strengths or limitations of each approach. `RockMapper` mapping resulted in similar accuracy to manual methods, which ranged between 61-98%, while also saving ~ 11 minutes per hectare of manual delineation time. Additionally, `RockMapper` appeared to generalize well to new rivers, indicating reproducibility to unseen datasets. 

### Model Training Data

Wolfenkoehler, W., and Long, J., 2026, Substrate classifications of three rivers in eastern Oklahoma: U.S. Geological Survey data release, https://doi.org/10.5066/P1CZGXSF

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

1. Copy the following script to some location on your computer and name it "RockMapper.py":

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
    seg_model = 'RockMapper_20251117_v2'
    inDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\mosaics' #location of the sonar mosaic you wish to process
    mosaicFileType = '.tif'
    outDirTop = r'Z:\scratch' #output folder where you wish to place the RockMapper substrate shapefile
    projName = 'RockMapperTest'
    mapRast = False #do you want a raster output?
    mapShp = True #do you want a shapefile output? 

    epsg = 32615 # change to desired cooordinate system

    windowSize_m = (18, 18)
    window_stride = 6
    minArea_percent = 0.75
    threadCnt = 0.75

    predBatchSize = 30

    minPatchSize_m2 = 5 # Minimum patch size to keep in final shapefile, in square meters
    smoothShp = True # Smooth final shapefile polygons
    smoothTol_m = 0.3 # Smoothing tolerance in meters, higher = more smoothing

    deleteIntData = True



    ################
    # Run HabiMapper

    modelDir = os.path.join(GV_UTILS_DIR, 'models')

    # RockMapper
    if seg_model in ['RockMapper_20250628_v1', 'RockMapper_20251117_v2']:
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
        deleteIntData=deleteIntData,
        minPatchSize = minPatchSize_m2,
        smoothShp = smoothShp,
        smoothTol_m = smoothTol_m,
        )





    print("\n\nGrand Total Processing Time: ", datetime.timedelta(seconds = round(time.time() - start_time, ndigits=0)))
    return

if __name__ == "__main__":
    gui()
```

2. Open the file with [Visual Studio Code](https://code.visualstudio.com/).
3. Update the Parameters as necessary:

```python
#############################
# Update Parameters
seg_model = 'RockMapper_20251117_v2' 
inDir = r'Z:\scratch\202506_BrushyDeepKiamichi_Substrate\mosaics' #location of the sonar mosaic you wish to process
mosaicFileType = '.tif'
outDirTop = r'Z:\scratch' #output folder where you wish to place the RockMapper substrate shapefile
projName = 'RockMapperTest'
mapRast = False #do you want a raster output?
mapShp = True #do you want a shapefile output? 

epsg = 32615 # change to desired cooordinate system

windowSize_m = (18, 18)
window_stride = 6
minArea_percent = 0.75
threadCnt = 0.75

predBatchSize = 30

minPatchSize_m2 = 5 # Minimum patch size to keep in final shapefile, in square meters
smoothShp = True # Smooth final shapefile polygons
smoothTol_m = 0.3 # Smoothing tolerance in meters, higher = more smoothing

deleteIntData = True
```

4. Open Mini Forge Prompt
5. type "conda activate rockmapper"
6. change the directory to the folder where the python sciprt is located
7. Run the script by typing "python RockMapper.py" 
