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
import requests, zipfile
from joblib import Parallel, delayed
from tqdm import tqdm

from rockmapper.utils import printUsage#, avg_npz_files, map_npzs

# Debug
pingTilePath = os.path.normpath('../PINGTile')
pingTilePath = os.path.abspath(pingTilePath)
sys.path.insert(0, pingTilePath)
sys.path.insert(0, 'src')
debug = True

pingSegPath = os.path.normpath('../PINGSeg')
pingSegPath = os.path.abspath(pingSegPath)
sys.path.insert(0, pingSegPath)
sys.path.insert(0, 'src')

from pingtile.mosaic2tile import doMosaic2tile
from pingtile.utils import avg_npz_files, map_npzs, mosaic_maps, maps2Shp, apply_son_mask
from pingseg.seg_gym import seg_gym_folder, seg_gym_folder_noDL
debug = False

# Set ROCKMAPPER utils dir
USER_DIR = os.path.expanduser('~')
GV_UTILS_DIR = os.path.join(USER_DIR, '.rockmapper')
if not os.path.exists(GV_UTILS_DIR):
    os.makedirs(GV_UTILS_DIR)

#=======================================================================
def do_work(
            inDir: str,
            outDirTop: str,
            modelDir: str,
            projName: str,
            mapRast: bool,
            mapShp: bool,
            epsg: int,
            windowSize_m: tuple,
            window_stride: int,
            minArea_percent: float,
            threadCnt: float, 
            mosaicFileType: str,
            predBatchSize: int,
            deleteIntData: bool=True
        ):
    '''
    '''

    start_time = time.time()

    outDir = os.path.join(outDirTop, projName)

    # if os.path.exists(outDir):
    #     shutil.rmtree(outDir)

    if not os.path.exists(outDir):
        os.makedirs(outDir)

    ###########
    # Get model

    seg_model = os.path.basename(modelDir)

    if not os.path.exists(modelDir) or len(os.listdir(modelDir)) == 0:
        os.makedirs(modelDir, exist_ok=True)

        url = f'https://github.com/PINGEcosystem/RockMapper/releases/download/models/{seg_model}.zip'
        print(f'\n\nDownloading segmentation models (v1.0): {url}')

        filename = modelDir + '.zip'
        try:
            # stream download to avoid memory spikes
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # quick validation
            if not zipfile.is_zipfile(filename):
                # read beginning of file to help debug (text/html error pages)
                with open(filename, 'rb') as fh:
                    head = fh.read(512).decode('utf-8', errors='replace')
                os.remove(filename)
                raise RuntimeError(f"Downloaded file is not a zip file. Server response starts with: {head!r}")

            # extract safely
            with zipfile.ZipFile(filename, 'r') as z_fp:
                z_fp.extractall(modelDir)

            os.remove(filename)
            print('Model download and extraction success!')

        except requests.RequestException as e:
            # network/HTTP problem
            if os.path.exists(filename):
                os.remove(filename)
            raise RuntimeError(f"Failed to download model from {url}: {e}") from e
        except zipfile.BadZipFile as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise RuntimeError("Downloaded model archive is corrupted or not a zip file.") from e


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

    # Delete intermediate data
    to_delete = []

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
    if debug:
        mosaics = mosaics[:1]


    # ###############################
    # # Generate moving window images

    # print('\n\nTiling Mosaics...\n\n')

    # imagesAll = []

    # for mosaic in mosaics:
    #     r = doMosaic2tile(
    #         inFile = mosaic,
    #         outDir = outSonDir,
    #         windowSize = windowSize_m,
    #         windowStride_m = window_stride,
    #         outName = projName,
    #         epsg_out = epsg,
    #         threadCnt = threadCnt,
    #         target_size = config['TARGET_SIZE'],
    #         minArea_percent = minArea_percent,
    #     )

    #     imagesAll.append(r)
    
    # imagesDF = pd.concat(imagesAll, axis=0, ignore_index=True)

    # # For debug
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_tiles.csv')
    # imagesDF.to_csv(outDF, index=False)

    # # Delete intermediate data
    # if deleteIntData:
    #     to_delete.append(outSonDir)

    # print('Image Tiles Generated: {}'.format(len(imagesDF)))

    # print("\nDone!")
    # print("Time (s):", round(time.time() - start_time, ndigits=1))
    # printUsage()


    # For Debug
    imagesDF = pd.read_csv(outDF)
    print(len(imagesDF))

    ###################
    # Do shadow removal
    print('\n\nPredicting and masking shadows from sonar tiles...\n\n')

    start_time = time.time()

    outSonMaskedDir = os.path.join(outDir, 'images_mask_npz')

    if not os.path.exists(outSonMaskedDir):
        os.makedirs(outSonMaskedDir)

    # Get shadow model

    shadowModelDir = os.path.join(GV_UTILS_DIR, 'models', 'PINGMapperv2.0_SegmentationModelv1.0')

    seg_model = os.path.basename(shadowModelDir)

    if not os.path.exists(shadowModelDir) or len(os.listdir(shadowModelDir)) == 0:
        os.makedirs(shadowModelDir, exist_ok=True)

        url = f'https://zenodo.org/records/10093642/files/PINGMapperv2.0_SegmentationModelsv1.0.zip?download=1'
        print(f'\n\nDownloading shadow model (v1.0): {url}')

        filename = shadowModelDir + '.zip'
        try:
            # stream download to avoid memory spikes
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # quick validation
            if not zipfile.is_zipfile(filename):
                # read beginning of file to help debug (text/html error pages)
                with open(filename, 'rb') as fh:
                    head = fh.read(512).decode('utf-8', errors='replace')
                os.remove(filename)
                raise RuntimeError(f"Downloaded file is not a zip file. Server response starts with: {head!r}")

            # extract safely
            with zipfile.ZipFile(filename, 'r') as z_fp:
                z_fp.extractall(shadowModelDir)

            os.remove(filename)
            print('Model download and extraction success!')

        except requests.RequestException as e:
            # network/HTTP problem
            if os.path.exists(filename):
                os.remove(filename)
            raise RuntimeError(f"Failed to download model from {url}: {e}") from e
        except zipfile.BadZipFile as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise RuntimeError("Downloaded model archive is corrupted or not a zip file.") from e
        
    shadowModelDir = os.path.join(shadowModelDir, 'Shadow_Segmentation_unet_v1.0')
        
    # imagesDF = seg_gym_folder(imgDF=imagesDF, modelDir=shadowModelDir, out_dir=outSonMaskedDir, batch_size=predBatchSize, threadCnt=threadCnt)

    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_shadow.csv')
    imagesDF.to_csv(outDF, index=False)
    gdf = imagesDF

    # Delete intermediate data
    if deleteIntData:
        to_delete.append(outSonMaskedDir)

    print("\nPrediction Complete!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()

    # ###############################
    # # Average overlapping npz files
    # print('\n\nAveraging overlapping shadow predictions...\n\n')
    # start_time = time.time()

    # out_shadow_avg_npz = os.path.join(outDir, 'images_mask_npz_avg')

    # if not os.path.exists(out_shadow_avg_npz):
    #     os.makedirs(out_shadow_avg_npz)

    # gdf = avg_npz_files(df=imagesDF, in_dir=outSonMaskedDir, out_dir=out_shadow_avg_npz, outName=projName, windowSize_m=windowSize_m, stride=windowSize_m[0], epsg=epsg, threadCnt=threadCnt)

    # outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_avgnpz_shadow.csv')
    # gdf.to_csv(outDF, index=False)

    # # Delete intermediate data
    # if deleteIntData:
    #     to_delete.append(out_shadow_avg_npz)

    # print("\nDone!")
    # print("Time (s):", round(time.time() - start_time, ndigits=1))
    # printUsage()


    # # For debug
    # out_avg_npz = os.path.join(outDir, 'preds_avg_npz')
    # outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_avgnpz_shadow.csv')
    # gdf = pd.read_csv(outDF)

    ##############################################
    # Mask the sonar tiles based on shadow avg npz

    print('\n\nMasking sonar tiles based on shadow predictions...\n\n')
    start_time = time.time()

    outSonMaskedTilesDir = os.path.join(outDir, 'images_masked_tiles')

    if not os.path.exists(outSonMaskedTilesDir):
        os.makedirs(outSonMaskedTilesDir)

    Parallel(n_jobs=threadCnt)(delayed(apply_son_mask)(row, outSonMaskedTilesDir) for idx, row in tqdm(gdf.iterrows(), total=gdf.shape[0]))



    ################################
    # Perform segmentation on images

    print('\n\nPredicting substrate from sonar tiles...\n\n')
    start_time = time.time()

    out_npz = os.path.join(outDir, 'preds_npz')

    imagesDF = seg_gym_folder(imgDF=imagesDF, modelDir=modelDir, out_dir=out_npz, batch_size=predBatchSize, threadCnt=threadCnt)

    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_tileseg.csv')
    imagesDF.to_csv(outDF, index=False)

    # Delete intermediate data
    if deleteIntData:
        to_delete.append(out_npz)

    print("\nPrediction Complete!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()

    


    # # For Debug #
    # #######################
    # # Map average npz files
    # print('\n\nMapping predicted substrate...\n\n')
    # start_time = time.time()

    # out_maps = os.path.join(outDir, 'preds_mapped_ind_npz')

    # if not os.path.exists(out_maps):
    #     os.makedirs(out_maps)

    # from shapely.geometry import box
    # # Create per-row geometry safely from bounds (xmin, ymin, xmax, ymax).
    # # Passing pandas.Series directly to shapely.box raises TypeError because
    # # shapely expects scalar floats for each bound. Build a geometry per row,
    # # coerce to float, and ignore degenerate or invalid rows.
    # def _make_geom_from_bounds(row):
    #     try:
    #         xmin = float(row['x_min'])
    #         ymin = float(row['y_min'])
    #         xmax = float(row['x_max'])
    #         ymax = float(row['y_max'])
    #         # ignore degenerate boxes or NaNs
    #         if any(pd.isna([xmin, ymin, xmax, ymax])):
    #             return None
    #         if xmin >= xmax or ymin >= ymax:
    #             return None
    #         return box(xmin, ymin, xmax, ymax)
    #     except Exception:
    #         return None

    # imagesDF['geometry'] = imagesDF.apply(_make_geom_from_bounds, axis=1)
    # # Drop rows without valid geometry
    # imagesDF = imagesDF[~imagesDF['geometry'].isnull()].reset_index(drop=True)
    # # Convert to GeoDataFrame with the provided CRS
    # imagesDF = gpd.GeoDataFrame(imagesDF, geometry='geometry', crs=f"EPSG:{epsg}")

    # # Make npz column with basename in imagesDF['mosaic'] and out_npz directory
    # # imagesDF['mosaic'] contains the source image path used for prediction.
    # # Build the corresponding npz filename (basename + .npz) located in out_npz.
    # def _npz_path_from_mosaic(p):
    #     try:
    #         if pd.isna(p):
    #             return None
    #         base = os.path.splitext(os.path.basename(p))[0]
    #         return os.path.join(out_npz, f"{base}.npz")
    #     except Exception:
    #         return None

    # imagesDF['npz'] = imagesDF['mosaic'].apply(_npz_path_from_mosaic)

    # gdf = map_npzs(df=imagesDF, in_dir=out_npz, out_dir=out_maps, outName=projName, windowSize_m=windowSize_m, epsg=epsg)

    # # Delete intermediate data
    # if deleteIntData:
    #     to_delete.append(out_maps)

    # print("\nDone!")
    # print("Time (s):", round(time.time() - start_time, ndigits=1))
    # printUsage()
    # # For Debug #






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

    gdf = avg_npz_files(df=imagesDF, in_dir=out_npz, out_dir=out_avg_npz, outName=projName, windowSize_m=windowSize_m, stride=windowSize_m[0], epsg=epsg, threadCnt=threadCnt)

    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_avgnpz.csv')
    gdf.to_csv(outDF, index=False)

    # Delete intermediate data
    if deleteIntData:
        to_delete.append(out_avg_npz)

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

    gdf = map_npzs(df=gdf, in_dir=out_avg_npz, out_dir=out_maps, outName=projName, windowSize_m=windowSize_m, epsg=epsg, threadCnt=threadCnt)

    # Delete intermediate data
    if deleteIntData:
        to_delete.append(out_maps)

    print("\nDone!")
    print("Time (s):", round(time.time() - start_time, ndigits=1))
    printUsage()


    # Save df
    outDF = os.path.join(outDir, f'{projName}_{windowSize_m[0]}_{windowSize_m[1]}_mapped_npzs.csv')
    gdf.to_csv(outDF, index=False) 

    #############
    # Mosaic maps

    if mapRast:

        print('\n\nExport map as raster mosaic...\n\n')
        start_time = time.time()

        map_files = glob(os.path.join(out_maps, '*.tif'))

        out_mosaic = os.path.join(outDir, 'mosaic')

        if not os.path.exists(out_mosaic):
            os.makedirs(out_mosaic)

        mosaic_maps(map_files, out_mosaic, projName)

        print("\nDone!")
        print("Time (s):", round(time.time() - start_time, ndigits=1))
        printUsage()

    ###################
    # Maps to Shapefile

    if mapShp:

        print('\n\nExport map as shapefile...\n\n')
        start_time = time.time()

        map_files = glob(os.path.join(out_maps, '*.tif'))

        out_shp = os.path.join(outDir, 'map_shp')

        if not os.path.exists(out_shp):
            os.makedirs(out_shp)

        maps2Shp(map_files, out_shp, projName, configFile)

        print("\nDone!")
        print("Time (s):", round(time.time() - start_time, ndigits=1))
        printUsage()

    # #################
    # # Mask the mosaic

    # print('\n\nMasking final map...\n\n')
    # start_time = time.time()

    # out_mosaic = os.path.join(out_mosaic, f'{projName}.tif')
    # out_mask = os.path.join(outDir, 'mask')

    # if not os.path.exists(out_mask):
    #     os.makedirs(out_mask)

    # mask_mosaic_map()


    ##########################
    # Delete intermediate data

    if deleteIntData:
        print('\n\nDeleting intermediate data...\n\n')
        start_time = time.time()

        for d in to_delete:
            shutil.rmtree(d, ignore_errors=True)

        print("\nDone!")
        print("Time (s):", round(time.time() - start_time, ndigits=1))
        printUsage()

    return