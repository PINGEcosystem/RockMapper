'''
Copyright (c) 2025 Cameron S. Bodine
'''

#########
# Imports
import os

from rockmapper.utils import printUsage#, avg_npz_files, map_npzs

from pingtile.mapper_workflow import run_mapper_workflow

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
            deleteIntData: bool=True,
            minPatchSize: float=3,
            smoothShp: bool=False,
            smoothTol_m: float=0.5,
        ):
    '''
    '''

    def _predict_tiles_rock(imagesDF, modelDir, out_npz, predBatchSize, threadCnt):
        # RockMapper intentionally uses the Segmentation Gym backend.
        # Keep existing user-facing error handling around dependency issues.
        try:
            from pingseg.seg_gym import seg_gym_folder
        except OSError as e:
            msg = str(e)
            if 'shm.dll' in msg or 'WinError 127' in msg:
                raise RuntimeError(
                    'PyTorch failed to load on Windows (shm.dll dependency issue). '
                    'This is usually caused by an incompatible torch/transformers combination. '
                    'Use a TensorFlow-compatible transformers version (e.g., 4.46.3) or reinstall a '
                    'CPU-only PyTorch build for your Python version, then restart Python and rerun RockMapper.'
                ) from e
            raise
        except ImportError as e:
            raise RuntimeError(
                'Failed to import pingseg segmentation dependencies. '
                'Install/repair pingseg, doodleverse_utils, tensorflow, tf-keras, and transformers.'
            ) from e

        try:
            return seg_gym_folder(
                imgDF=imagesDF,
                modelDir=modelDir,
                out_dir=out_npz,
                batch_size=predBatchSize,
                threadCnt=threadCnt,
            )
        except ImportError as e:
            msg = str(e)
            if 'SegformerForSemanticSegmentation requires the PyTorch library' in msg or 'TFSegformerForSemanticSegmentation' in msg:
                raise RuntimeError(
                    'SegFormer dependencies are not available in this environment. '
                    'Use a TensorFlow-compatible transformers version (e.g., 4.46.3). '
                    'If you must use newer transformers, install a working CPU-only PyTorch build, '
                    'then restart Python and rerun RockMapper.'
                ) from e
            raise

    run_mapper_workflow(
        mapper_name='RockMapper',
        releases_repo='RockMapper',
        inDir=inDir,
        outDirTop=outDirTop,
        modelDir=modelDir,
        projName=projName,
        mapRast=mapRast,
        mapShp=mapShp,
        epsg=epsg,
        windowSize_m=windowSize_m,
        window_stride=window_stride,
        minArea_percent=minArea_percent,
        threadCnt=threadCnt,
        mosaicFileType=mosaicFileType,
        predBatchSize=predBatchSize,
        deleteIntData=deleteIntData,
        minPatchSize=minPatchSize,
        smoothShp=smoothShp,
        smoothTol_m=smoothTol_m,
        print_usage=printUsage,
        predict_tiles=_predict_tiles_rock,
    )

    return