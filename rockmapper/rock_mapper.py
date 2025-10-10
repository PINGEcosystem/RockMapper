'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys, time
from os import cpu_count
from glob import glob
import pandas as pd
import geopandas as gpd
import json
import shutil

from rockmapper.utils import printUsage#, avg_npz_files, map_npzs

# Debug
pingTilePath = os.path.normpath('../PINGTile')
pingTilePath = os.path.abspath(pingTilePath)
sys.path.insert(0, pingTilePath)
sys.path.insert(0, 'src')

pingSegPath = os.path.normpath('../PINGSeg')
pingSegPath = os.path.abspath(pingSegPath)
sys.path.insert(0, pingSegPath)
sys.path.insert(0, 'src')

from pingtile.mosaic2tile import doMosaic2tile
from pingtile.utils import avg_npz_files, map_npzs, mosaic_maps
from pingseg.seg_gym import seg_gym_folder, seg_gym_folder_noDL

#=======================================================================
def do_work(
            inDir: str,
            outDirTop: str,
            modelDir: str,
            projName: str,
            epsg: int,
            windowSize_m: tuple,
            window_stride: int,
            minArea_percent: float,
            threadCnt: float, 
            mosaicFileType: str,
            predBatchSize: int,
        ):
    '''
    '''

    start_time = time.time()

    outDir = os.path.join(outDirTop, projName)

    if os.path.exists(outDir):
        shutil.rmtree(outDir)

    if not os.path.exists(outDir):
        os.makedirs(outDir)

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

    # Set Stride
    windowStride_m = windowSize_m
    minArea = minArea_percent * windowSize_m[0]*windowSize_m[1]

    # Make output image dir
    dirName = projName
    outDir = os.path.join(outDirTop, dirName)
    outSonDir = os.path.join(outDir, 'images')

    if not os.path.exists(outSonDir):
        os.makedirs(outSonDir)

    # Get the sonar images
    mosaics = glob(os.path.join(inDir, '**', '*{}'.format(mosaicFileType)), recursive=True)

    # Get the model config file and load it
    configFile = glob(os.path.join(modelDir, 'config', '*.json'))[0]

    with open(configFile) as f:
        config = json.load(f)






    # For debug
    mosaics = mosaics[:2]






    ###############################
    # Generate moving window images

    print('\n\nTiling Mosaics...\n\n')

    imagesAll = []

    for mosaic in mosaics:
        r = doMosaic2tile(
            inFile = mosaic,
            outDir = outDir,
            windowSize = windowSize_m,
            windowStride_m = window_stride,
            outName = projName,
            epsg_out = epsg,
            threadCnt = threadCnt,
            target_size = config['TARGET_SIZE'],
            minArea_percent = minArea_percent,
        )

        imagesAll.append(r)
    
    imagesDF = pd.concat(imagesAll, axis=0, ignore_index=True)

    # For debug
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_tiles.csv')
    imagesDF.to_csv(outDF, index=False)

    print('Image Tiles Generated: {}'.format(len(imagesDF)))

    print("\nDone!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()


    # For Debug
    imagesDF = pd.read_csv(outDF)
    print(len(imagesDF))


    ################################
    # Perform segmentation on images

    print('\n\nPredicting substrate from sonar tiles...\n\n')
    start_time = time.time()

    out_npz = os.path.join(outDir, 'preds_npz')

    imagesDF = seg_gym_folder(imgDF=imagesDF, modelDir=modelDir, out_dir=out_npz, batch_size=predBatchSize,)

    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_tileseg.csv')
    imagesDF.to_csv(outDF, index=False)

    print("\nPrediction Complete!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()
    

    # For Debug #
    #######################
    # Map average npz files
    print('\n\nMapping predicted substrate...\n\n')
    start_time = time.time()

    out_maps = os.path.join(outDir, 'preds_mapped_ind_npz')

    if not os.path.exists(out_maps):
        os.makedirs(out_maps)

    from shapely.geometry import box
    # Create per-row geometry safely from bounds (xmin, ymin, xmax, ymax).
    # Passing pandas.Series directly to shapely.box raises TypeError because
    # shapely expects scalar floats for each bound. Build a geometry per row,
    # coerce to float, and ignore degenerate or invalid rows.
    def _make_geom_from_bounds(row):
        try:
            xmin = float(row['x_min'])
            ymin = float(row['y_min'])
            xmax = float(row['x_max'])
            ymax = float(row['y_max'])
            # ignore degenerate boxes or NaNs
            if any(pd.isna([xmin, ymin, xmax, ymax])):
                return None
            if xmin >= xmax or ymin >= ymax:
                return None
            return box(xmin, ymin, xmax, ymax)
        except Exception:
            return None

    imagesDF['geometry'] = imagesDF.apply(_make_geom_from_bounds, axis=1)
    # Drop rows without valid geometry
    imagesDF = imagesDF[~imagesDF['geometry'].isnull()].reset_index(drop=True)
    # Convert to GeoDataFrame with the provided CRS
    imagesDF = gpd.GeoDataFrame(imagesDF, geometry='geometry', crs=f"EPSG:{epsg}")

    # Make npz column with basename in imagesDF['mosaic'] and out_npz directory
    # imagesDF['mosaic'] contains the source image path used for prediction.
    # Build the corresponding npz filename (basename + .npz) located in out_npz.
    def _npz_path_from_mosaic(p):
        try:
            if pd.isna(p):
                return None
            base = os.path.splitext(os.path.basename(p))[0]
            return os.path.join(out_npz, f"{base}.npz")
        except Exception:
            return None

    imagesDF['npz'] = imagesDF['mosaic'].apply(_npz_path_from_mosaic)

    gdf = map_npzs(df=imagesDF, in_dir=out_npz, out_dir=out_maps, outName=projName, windowSize_m=windowSize_m, epsg=epsg)

    print(gdf)

    print("\nDone!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()
    # For Debug #






    # For debug
    out_npz = os.path.join(outDir, 'preds_npz')
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_tileseg.csv')
    imagesDF = pd.read_csv(outDF)

    ###############################
    # Average overlapping npz files
    print('\n\nAveraging overlapping substrate predictions...\n\n')
    start_time = time.time()

    out_avg_npz = os.path.join(outDir, 'preds_avg_npz')

    if not os.path.exists(out_avg_npz):
        os.makedirs(out_avg_npz)

    gdf = avg_npz_files(df=imagesDF, in_dir=out_npz, out_dir=out_avg_npz, outName=projName, windowSize_m=windowSize_m, stride=windowSize_m[0], epsg=epsg)

    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_avgnpz.csv')
    gdf.to_csv(outDF, index=False)

    print("\nDone!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()


    # For debug
    out_avg_npz = os.path.join(outDir, 'preds_avg_npz')
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_avgnpz.csv')
    gdf = pd.read_csv(outDF)



    #######################
    # Map average npz files
    print('\n\nMapping predicted substrate...\n\n')
    start_time = time.time()

    out_maps = os.path.join(outDir, 'preds_mapped')

    if not os.path.exists(out_maps):
        os.makedirs(out_maps)

    gdf = map_npzs(df=gdf, in_dir=out_avg_npz, out_dir=out_maps, outName=projName, windowSize_m=windowSize_m, epsg=epsg)

    print(gdf)

    print("\nDone!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()


    # Save df
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_mapped_npzs.csv')
    gdf.to_csv(outDF, index=False) 

    #############
    # Mosaic maps

    print('\n\nMosaicking mapped substrate predictions...\n\n')
    start_time = time.time()

    map_files = glob(os.path.join(out_maps, '*.tif'))

    out_mosaic = os.path.join(outDir, 'mosaic')

    if not os.path.exists(out_mosaic):
        os.makedirs(out_mosaic)

    mosaic_maps(map_files, out_mosaic, projName)

    return