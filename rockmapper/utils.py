'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os, sys
import psutil
import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm
import rasterio as rio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import box, shape

# Debug
pingTilePath = os.path.normpath('../PINGTile')
pingTilePath = os.path.abspath(pingTilePath)
sys.path.insert(0, pingTilePath)
sys.path.insert(0, 'src')
from pingtile.utils import getMovingWindow

#=======================================================================
def printUsage():
    '''
    Show computing resources used
    '''
    cpuPercent = round(psutil.cpu_percent(0.5), 1)
    ramPercent = round(psutil.virtual_memory()[2], 1)
    ramUsed = round(psutil.virtual_memory()[3]/1000000000, 1)

    print('\n\nCurrent CPU/RAM Usage:')
    print('________________________')
    print('{:<5s} | {:<5s} | {:<5s}'.format('CPU %', 'RAM %', 'RAM [GB]'))
    print('________________________')

    print('{:<5s} | {:<5s} | {:<5s}'.format(str(cpuPercent), str(ramPercent), str(ramUsed)))
    print('________________________\n\n')


    return

# #=======================================================================
# def avg_npz_files_batch(df: pd.DataFrame,
#                         win: pd.Series,
#                         arr_shape: tuple,
#                         in_dir: str,
#                         out_dir: str,
#                         outName: str,
#                         windowSize_m: tuple,
#                         epsg: int,
#                         ):
    
#     '''
#     '''

#     win_minx, win_miny, win_maxx, win_maxy = win.geometry.bounds

#     # Calculate pixel size for the window array
#     win_height, win_width = arr_shape[1], arr_shape[2]  # (bands, height, width)
#     win_pixel_size_x = (win_maxx - win_minx) / win_width
#     win_pixel_size_y = (win_maxy - win_miny) / win_height


#     win_coords = ''
#     for b in win.geometry.bounds:
#         b = int(round(b, 0))

#         win_coords += str(b)+'_'

#     win_coords = win_coords[:-1]

#     # Find overlapping npz files
#     overlaps = df[
#         (df['x_min'] < win_maxx) & (df['x_max'] > win_minx) &
#         (df['y_min'] < win_maxy) & (df['y_max'] > win_miny)
#     ]

#     if overlaps.empty:
#         return

#     # Determine output array shape for this window
#     sum_arr = np.zeros(arr_shape, dtype=np.float64)
#     count_arr = np.zeros((arr_shape[1], arr_shape[2]), dtype=np.int32)

#     for _, row in overlaps.iterrows():
#         base = os.path.splitext(os.path.basename(row['mosaic']))[0]
#         npz_path = os.path.join(in_dir, f"{base}.npz")
#         npz = np.load(npz_path)
#         arr = npz['softmax']
#         arr_minx, arr_miny, arr_maxx, arr_maxy = row[['x_min', 'y_min', 'x_max', 'y_max']]
#         arr_shape = arr.shape  # (bands, height, width)
#         arr_pixel_size_x = (arr_maxx - arr_minx) / arr_shape[2]
#         arr_pixel_size_y = (arr_maxy - arr_miny) / arr_shape[1]


#         # Calculate overlap in world coordinates
#         overlap_minx = max(win_minx, arr_minx)
#         overlap_maxx = min(win_maxx, arr_maxx)
#         overlap_miny = max(win_miny, arr_miny)
#         overlap_maxy = min(win_maxy, arr_maxy)

#         # Convert world coordinates to array indices
#         win_x0 = int(np.floor((overlap_minx - win_minx) / win_pixel_size_x))
#         win_x1 = int(np.ceil((overlap_maxx - win_minx) / win_pixel_size_x))
#         win_y0 = int(np.floor((overlap_miny - win_miny) / win_pixel_size_y))
#         win_y1 = int(np.ceil((overlap_maxy - win_miny) / win_pixel_size_y))

#         arr_x0 = int(np.floor((overlap_minx - arr_minx) / arr_pixel_size_x))
#         arr_x1 = int(np.ceil((overlap_maxx - arr_minx) / arr_pixel_size_x))
#         arr_y0 = int(np.floor((overlap_miny - arr_miny) / arr_pixel_size_y))
#         arr_y1 = int(np.ceil((overlap_maxy - arr_miny) / arr_pixel_size_y))

#         # Check for valid overlap and matching shapes
#         win_slice_shape = (win_y1 - win_y0, win_x1 - win_x0)
#         arr_slice_shape = (arr_y1 - arr_y0, arr_x1 - arr_x0)
#         if (win_slice_shape[0] > 0 and win_slice_shape[1] > 0 and
#             arr_slice_shape[0] > 0 and arr_slice_shape[1] > 0 and
#             win_slice_shape == arr_slice_shape):
#             sum_arr[:, win_y0:win_y1, win_x0:win_x1] += arr[:, arr_y0:arr_y1, arr_x0:arr_x1]
#             count_arr[win_y0:win_y1, win_x0:win_x1] += 1


#         # print('\n\n', win_x0, win_x1, win_y0, win_y1, sum_arr.shape)
#         # print(arr_x0, arr_x1, arr_y0, arr_y1, arr.shape)
#         # print('Overlap:', overlap_minx, overlap_miny, overlap_maxx, overlap_maxy)
#         # print(arr_pixel_size_x, arr_pixel_size_y)

#     # Avoid division by zero
#     avg_arr = np.divide(sum_arr, count_arr, out=np.zeros_like(sum_arr), where=count_arr != 0)

#     # print('\n\n', avg_arr)

#     # Save to npz
#     # Save the clipped raster and shapefile
#     if outName:
#         fileName = f"{outName}_{windowSize_m[0]}m_{win_coords}"
#     else:
#         fileName = f"{windowSize_m[0]}m_{win_coords}"
#     out_npz = os.path.join(out_dir, f"{fileName}.npz")

#     df['npz'] = out_npz

#     np.savez_compressed(out_npz, softmax=avg_arr)

#     # Convert to GeoDataFrame
#     geometry = box(win_minx, win_miny, win_maxx, win_maxy)
#     # df['geometry'] = gpd.GeoSeries.from_bounds(win_minx, win_miny, win_maxx, win_maxy, crs=f"EPSG:{epsg}").geometry
#     df['geometry'] = gpd.GeoSeries([geometry], crs=f"EPSG:{epsg}")

#     return df



# #=======================================================================
# def avg_npz_files(df: pd.DataFrame,
#                   in_dir: str,
#                   out_dir: str,
#                   outName: str,
#                   windowSize_m: tuple,
#                   stride: int,
#                   epsg: int):
#     '''
#     Average overlapping npz files
#     '''

#     # Get non-overlapping moving window geodataframe
#     movWin = getMovingWindow(df=df, windowSize=windowSize_m, windowStride_m=stride, epsg=epsg)
    
#     # Save moving window to shapefile
#     out_file = os.path.join(out_dir, 'Map_Tiles.shp')
#     movWin.to_file(out_file, driver='ESRI Shapefile')

#     # Assume all arrays have the same shape and resolution
#     # Load one sample to get array shape and pixel size
#     base = os.path.splitext(os.path.basename(df.iloc[0]['mosaic']))[0]
#     base = base.split('.png')[0]
#     npz_path = os.path.join(in_dir, f"{base}.npz")
#     sample_npz = np.load(npz_path)
#     arr_shape = sample_npz['softmax'].shape

#     # Use joblib to parallelize the averaging process
#     results = Parallel(n_jobs=-1, verbose=10)(
#         delayed(avg_npz_files_batch)(df, win, arr_shape, in_dir, out_dir, outName, windowSize_m, epsg)
#         for idx, win in tqdm(movWin.iterrows(), total=len(movWin), desc="Processing windows")
#     )

#     results = [res for res in results if res is not None]
#     results = pd.concat(results, ignore_index=True)

#     results = gpd.GeoDataFrame(results, geometry='geometry', crs=movWin.crs)                    

#     return results


# # def label_array_to_shapefile(df, in_dir, out_dir, outName, windowSize_m, epsg):
# #     """
# #     Convert a label array to polygons and save as a shapefile.

# #     label: 2D numpy array of class labels
# #     transform: affine transform for the array (e.g., from rasterio)
# #     out_shp: output shapefile path
# #     """

# #     # Load npz
# #     # base = os.path.splitext(os.path.basename(df.iloc[0]['mosaic']))[0]
# #     # npz_path = os.path.join(in_dir, f"{base}.npz")
# #     npz = np.load(df['npz'].values[0])

# #     softmax = npz['softmax']
# #     label = np.argmax(softmax, axis=0).astype(np.uint8)  # Assuming softmax shape is (classes, height, width)

# #     # x_min, y_min, x_max, y_max = df[['x_min', 'y_min', 'x_max', 'y_max']].values[0]

# #     # transform = rio.transform.from_bounds(x_min, y_min, x_max, y_max, label.shape[1], label.shape[0])

# #     geometry = df['geometry'].values[0]
# #     transform = rio.transform.from_bounds(*geometry.bounds, label.shape[1], label.shape[0])

# #     # Generate polygons from the label array
# #     mask = label != 0  # Optional: mask out background if label 0 is background
# #     results = (
# #         {'properties': {'class': int(v)}, 'geometry': s}
# #         for s, v in shapes(label, mask=mask, transform=transform)
# #     )

# #     # Convert to GeoDataFrame
# #     geoms = []
# #     classes = []
# #     for result in results:
# #         geoms.append(shape(result['geometry']))
# #         classes.append(result['properties']['class'])
# #     gdf = gpd.GeoDataFrame({'class': classes, 'geometry': geoms}, crs=f"EPSG:{epsg}")

# #     # # Save to shapefile
# #     # gdf.to_file(out_shp)

# #     if len(gdf) == 0:
# #         return None
    
# #     return gdf

# #=======================================================================
# def map_npzs(df: pd.DataFrame, in_dir: str, out_dir: str, outName: str, windowSize_m: tuple, epsg: int):

#     '''
#     '''

#     # Iterate each row
#     # for idx, row in tqdm(df.iterrows(), total=len(df), desc="Mapping npz files"):

#     # r = Parallel(n_jobs=-1, verbose=10)(
#     #     delayed(label_array_to_shapefile)(df, in_dir, out_dir, outName, windowSize_m, epsg)
#     #     for idx, win in tqdm(df.iterrows(), total=len(df), desc="Processing windows")
#     #     )
    
#     # Concatenate results
#     if not os.path.exists(out_dir):
#         os.makedirs(out_dir)

#     if len(r) == 0:
#         print("No valid polygons found in any npz files.")
#         return None
#     r = pd.concat(r, ignore_index=True)

#     if outName:
#         out_shp = os.path.join(out_dir, f"{outName}.shp")
#     else:
#         out_shp = os.path.join(out_dir, 'mapped_polygons.shp')

#     # r.to_file(out_shp, driver='ESRI Shapefile')
    

        