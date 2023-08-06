import io
import json
import os
from io import StringIO
from os import path

import boto3
import botocore
import geopandas as gpd
import imageio
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError
from PIL import Image
from shapely import wkt


def upload_object(
    bucket: str = None,
    local_file_path: str = None,
    profile_name: str = None,
    verbose: bool = True,
    json_obj=None,
):
    """
    Upload a file from local to an S3 bucket

    Parameters
    ----------
    local_file_path: str. Local path of file to upload
    bucket: str. S3 bucket name to upload to.
    profile_name: str. Profile AWS name.
    verbose: Boolean. Print verbose
    json_obj: Json object in case a json file is uploaded.

    """
    # Store in same location in S3 and Locally.
    if '/data/' not in local_file_path:
        raise Exception('local_file_path=' + local_file_path + 'must contain "/data/"')

    _, file_format, _, _ = file_path_breaker(local_file_path)

    s3_file_path = local_file_path.split('/data/')[-1]

    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    # Upload the file
    out = True
    try:
        if profile_name is not None:
            boto3.setup_default_session(profile_name=profile_name)
        if verbose:
            print('Saving file in S3 as: ' + s3_file_path + ' ... ', end='')
        if file_format == '.json':
            s3object = s3_resource.Bucket(bucket).Object(s3_file_path)
            s3object.put(Body=(bytes(json.dumps(json_obj).encode('UTF-8'))))
        else:
            s3_client.upload_file(
                Filename=local_file_path, Bucket=bucket, Key=s3_file_path
            )
        if verbose:
            print('done')
    except ClientError:
        out = False
    return out


def save_object(
    obj=None,
    local_file_path: str = None,
    bucket: str = None,
    upload_only: bool = False,
    verbose: bool = True,
    **kwargs,
):
    """
    Saves locally and uploads a file from local to an S3 bucket

    Parameters
    ----------
    obj: Object. Dataframe to save in both: locally and into s3.
    local_file_path: str. Local path of file to upload
    bucket: str. S3 bucket name to upload to.
    upload_only: bolean. If False saves copy localy, else (True) it does not save local copy.
    verbose: Prints file path after saving if True.
    """

    if '/data/' not in local_file_path:
        raise Exception('local_file_path=' + local_file_path + 'must contain "/data/"')

    if obj is None:
        raise Exception('obj cannot be None')

    # Read file file_format
    file_name, file_format, local_file_dir, s3_file_dir = file_path_breaker(
        local_file_path
    )

    if not upload_only and verbose:
        # Do not show this message if in the end, this file will be removed.
        print('Saving local file: ' + local_file_path + '... ', end='')
    if file_format == '.json':
        file_formats = ['.json']
        with open(local_file_path, 'w') as fout:
            json.dump(obj, fout)
    elif file_format == '.csv':
        file_formats = ['.csv']
        obj.to_csv(local_file_path, index=False, **kwargs)
    elif file_format == '.geojson':
        file_formats = ['.geojson']
        obj.to_file(filename=local_file_path, driver='GeoJSON', **kwargs)
    elif file_format == '.shp':
        file_formats = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
        obj.to_file(filename=local_file_path, driver='ESRI Shapefile', **kwargs)
    elif file_format == '.png':
        imageio.imwrite(uri=local_file_path, im=obj)
        file_formats = ['.png']
    elif file_format == '.wld':
        with open(local_file_path, 'w+') as f:
            for i in obj:
                f.write(f'{i:.20f}\n')
        file_formats = ['.wld']
    else:
        raise Exception('Only csv, geojson, shp, png and wld formats are supported')

    if not upload_only and verbose:
        print('done')

    # Upload to S3
    for file_format in file_formats:
        local_file_path = local_file_dir + file_name + file_format
        if file_format == '.json':
            upload_object(
                bucket=bucket,
                local_file_path=local_file_path,
                json_obj=obj,
                verbose=verbose,
            )
        else:
            upload_object(
                bucket=bucket, local_file_path=local_file_path, verbose=verbose
            )

        if upload_only:
            os.remove(local_file_path)
    out = True

    return out


def get_object(
    bucket: str = None,
    s3_file_path: str = None,
    local_file_path: str = None,
    profile_name: str = None,
):
    """
    Get a file from an S3 bucket to local

    Parameters
    ----------
    bucket: str. S3 bucket name to upload to.
    s3_file_path: str. S3 object path.
    local_file_path: str. Local path for storing file.
    profile_name: str. Profile AWS name.
    """
    s3 = boto3.resource('s3')

    try:
        if profile_name is not None:
            boto3.setup_default_session(profile_name=profile_name)
        s3.Bucket(bucket).download_file(s3_file_path, local_file_path)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print('The object does not exist.')
        else:
            raise

    return None


def get_csv_as_gpd(
    bucket: str = None,
    local_file_path: str = None,
    crs='epsg:4326',
    geometry_col: str = 'geometry',
    confidential: bool = False,
    force_s3: bool = False,
    profile_name: str = None,
    colnames_to_lower: bool = False,
    verbose=True,
    **kwargs,
):
    """
    Reads a csv that has a geometry column and returns a geopandas dataframe.
    Parameters
    ----------
    bucket: str. S3 bucket name to upload to.
    local_file_path : str. Local path of a vector map in csv format.
    crs : int or str. The Coordinate Reference System (CRS) to read the file as. Default = 4326.
    geometry_col: geometry column name of dataframe
    confidential: If we assume the csv can be stored locally (False) or not (True).
    force_s3: force downloading file from s3 and overwrites local file if exits.
    profile_name : str. AWS profile name.
    colnames_to_lower : bool. Specifies if column names need to be converted to lower.
    verbose: bool. Prints verbose if True.
    **kwargs: options for functions pd.get_csv(). For example, encoding=latin1
    """

    df = get_csv(
        bucket=bucket,
        local_file_path=local_file_path,
        confidential=confidential,
        force_s3=force_s3,
        profile_name=profile_name,
        colnames_to_lower=colnames_to_lower,
        verbose=verbose,
        **kwargs,
    )
    df[geometry_col] = df[geometry_col].apply(wkt.loads)
    df = gpd.GeoDataFrame(df, crs=crs)
    return df


def get_csv(
    bucket: str = None,
    local_file_path: str = None,
    confidential: bool = False,
    force_s3: bool = False,
    profile_name: str = None,
    colnames_to_lower: bool = False,
    verbose=True,
    **kwargs,
):
    """
    Load a csv file from an S3 bucket to RAM.
    There are two methods to load a csv file:
    If confidential=True:
        We assume the csv can never be stored in disk and is stored into RAM directl from S3.
    If confidential=False:
        The csv will be stored first in disk and then read into RAM.
        First it tries to read directly from the localpath, in case the file was already stored.
        If the file does not exist or force_s3=True, then the csv file is dowloaded
        from S3 and then read from local.

    Parameters
    ----------
    bucket: str. S3 Bucket name to load from.
    local_file_path: Local path where csv is stored.
    confidential: If we assume the csv can be stored locally (False) or not (True).
    force_s3: force downloading file from s3 and overwrites local file if exits.
    profile_name : str. AWS profile name.
    colnames_to_lower : bool. Specifies if column names need to be converted to lower.
    verbose: bool. Prints verbose if True.
    **kwargs: options for functions pd.get_csv(). For example, encoding=latin1
    """

    if '/data/' not in local_file_path:
        raise Exception('local_file_path=' + local_file_path + 'must contain "/data/"')

    # Read file file_format
    file_name, file_format, _, s3_file_dir = file_path_breaker(local_file_path)

    if file_format != '.csv':
        raise Exception('File file_format invalid. Input must be a csv file.')

    if not confidential:
        # Tries to read from local file first because it is faster.
        local_file_path_exists = path.exists(local_file_path)

        if force_s3 or not local_file_path_exists:
            # Downloads file from S3.
            s3_file_path = s3_file_dir + file_name + file_format
            if verbose:
                print('Downloading ' + s3_file_path + ' from S3: ', end='')
            get_object(
                bucket=bucket,
                s3_file_path=s3_file_path,
                local_file_path=local_file_path,
            )
            if verbose:
                print('done')

        if verbose:
            print('Reading local file: ' + local_file_path + '... ', end='')
        out_df = pd.read_csv(local_file_path, **kwargs)
        if verbose:
            print('done')

    else:
        if profile_name is not None:
            boto3.setup_default_session(profile_name=profile_name)

        s3 = boto3.client('s3')
        try:
            s3_file_path = s3_file_dir + file_name + file_format
            obj = s3.get_object(Bucket=bucket, Key=s3_file_path)
            out_df = pd.read_csv(obj['Body'])

        except botocore.exceptions.ClientError:
            out_df = None

    if colnames_to_lower:
        out_df.columns = out_df.columns.str.lower()

    return out_df


def get_vector_map(
    local_file_path=None,
    bucket=None,
    crs=4326,
    force_s3=False,
    verbose=True,
):
    """
    Reads almost any vector-based spatial data format including ESRI shapefile
    (.shp) or  GeoJSON file. Then, transforms the geopandas to the Coordinate
    Reference System (CRS) given by crs.
    Returns a GeoDataFrame object.

    First tries to read from local_file_path, since its faster. Unless force_s3=True
    is specified. If local_file_path exits the GeoDataFrame object is returned.
    Otherwise, it downloads it from bucket under the same name and then reads it from local.

    Parameters
    ----------
    bucket: str.  S3 bucket name to upload to.
    local_file_path : str. Local path of a vector map file (shp or geojson).
    crs : int. The Coordinate Reference System (CRS) to read the file as. Default = 4326.
    force_s3: boolean. Forces download from s3 even if local file exists and overwrites.
    verbose: bool. Prints verbose if True.
    """

    if '/data/' not in local_file_path:
        raise Exception('local_file_path=' + local_file_path + 'must contain "/data/"')

    # Read file file_format
    file_name, file_format, local_file_dir, s3_file_dir = file_path_breaker(
        local_file_path
    )

    if file_format == '.geojson':
        file_formats = ['.geojson']
    elif file_format == '.shp':
        file_formats = ['.cpg', '.dbf', '.prj', '.shp', '.shx']
    else:
        raise Exception('File file_format invalid. Must be geojson or shp')

    # Tries to ready from local file first because it is faster.
    local_file_path_exists = path.exists(local_file_path)

    if force_s3 or not local_file_path_exists:
        for file_format in file_formats:
            s3_file_path_iter = s3_file_dir + file_name + file_format
            local_file_path_iter = local_file_dir + file_name + file_format
            if verbose:
                print('Downloading ' + s3_file_path_iter + ' from S3: ', end='')
            get_object(
                bucket=bucket,
                s3_file_path=s3_file_path_iter,
                local_file_path=local_file_path_iter,
            )
            if verbose:
                print('done')

    if verbose:
        print('Reading local file: ' + local_file_path + '... ', end='')
    vector_map = gpd.read_file(local_file_path)
    if verbose:
        print('done')

    # CRS maps Python to places on the Earth.
    # For example, one of the most commonly used
    # CRS is the WGS84 latitude-longitude projection.
    # This can be referred to using the authority code "EPSG:4326" or epsg=4326.
    vector_map = vector_map.to_crs(epsg=crs)

    return vector_map


def get_feather(bucket=None, key=None, profile_name=None, colnames_to_lower=False):
    """
    Load a feather file of an S3 bucket to RAM.

    Parameters
    ----------
    bucket: str. Bucket name to load from.
    key: str. S3 object name path.
    profile_name : str. AWS profile name.
    colnames_to_lower : bool. Specifies if column names need to be converted to lower.
    """

    if profile_name is not None:
        boto3.setup_default_session(profile_name=profile_name)

    s3 = boto3.resource('s3')

    try:
        s3.Object(bucket, key).load()
        bytes_obj = s3.Object(bucket, key).get()['Body'].read()
        feather = pd.read_feather(io.BytesIO(bytes_obj))

    except botocore.exceptions.ClientError:
        feather = None

    if colnames_to_lower:
        feather.columns = feather.columns.str.lower()

    return feather


def get_img(bucket=None, local_file_path=None, rm=True, wld=True):
    """
    Load a gpd dataframe of an S3 bucket to RAM.

    Parameters
    ----------
    bucket: str. Bucket name to load from.
    local_file_path: str. Local path to save S3 Object.
    rm: boolean. If True removes local file after reading in RAM.
    wld: boolean. If True, downloads wld file associated to local.
    """

    if '/data/' not in local_file_path:
        raise Exception('local_file_path=' + local_file_path + 'must contain "/data/"')

    _, _, local_file_dir, _ = file_path_breaker(local_file_path=local_file_path)
    dir_exists = path.exists(local_file_dir)
    if not dir_exists:
        os.mkdir(local_file_dir)

    s3_file_path = local_file_path.split('/data/')[-1]

    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket, s3_file_path, local_file_path)
        img = (mpimg.imread(local_file_path) * 255).astype(np.uint8)
        img = img[:, :, :-1]
        img = Image.fromarray(img)  # Assumes range [1,255]
        if rm and path.exists(local_file_path):
            os.remove(local_file_path)

        if wld:
            local_file_path = local_file_path.replace('png', 'wld')
            s3_file_path = s3_file_path.replace('png', 'wld')
            s3_client.download_file(bucket, s3_file_path, local_file_path)
    except ClientError:
        raise Exception('Error when trying to download either img or wld')
    return img


def check_key(bucket=None, key=None, profile_name=None):
    """
    Checks if a file exists in an S3 bucket. Return True if exists and False if it does not.
    ----------
    Parameters
        bucket: str. Bucket name to load from.
        key: str. S3 object name path.
        profile_name : str. AWS profile name.
    """
    if profile_name is not None:
        boto3.setup_default_session(profile_name=profile_name)

    s3 = boto3.resource('s3')
    exists = True
    try:
        s3.Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            exists = False  # The object does not exist.
        else:
            raise  # Something else has gone wrong.

    return exists


def file_path_breaker(local_file_path):
    """
    Breaks string of a local_file_path into different useful strings
    to save file in s3 or change file_format.
    local_file_path: string. Relative path of where a local file is stored.
    """
    s3_file_path = local_file_path.split('/data/')[-1]
    file_name_file_format = local_file_path.split('/', local_file_path.count('/'))[-1]
    file_name = file_name_file_format.split('.', file_name_file_format.count('.'))[0]
    file_format = (
        '.' + file_name_file_format.split('.', file_name_file_format.count('.'))[-1]
    )
    local_file_dir = local_file_path.replace(file_name_file_format, '')
    s3_file_dir = s3_file_path.replace(file_name_file_format, '')
    return file_name, file_format, local_file_dir, s3_file_dir
