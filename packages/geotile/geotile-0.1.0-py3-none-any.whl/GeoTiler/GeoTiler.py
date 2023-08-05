# inbuilt libraries
import os
import itertools
import glob
from typing import List, Optional, Set

# rasterio library
import rasterio as rio
from rasterio import windows
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.features import rasterize

# geopandas library
import geopandas as gpd


class GeoTiler:
    """GeoTiler class

            Attributes
            ----------
                path : str, python path
                    Path to the raster file (str)
                ds : rasterio.DatasetReader, object
                    Raster dataset
                meta : dict
                    Raster metadata
                height : int 
                    Raster height
                width : int
                    Raster width
                crs : str
                    Raster crs (e.g. 'EPSG:4326'). The will be generated automatically. 
                    In case of non-geographic raster, the crs will be None. 
                stride_x : int 
                    The stride of the x axis (int), default is 128
                stride_y : int
                    The stride of the y axis (int), default is 128
                tile_x : int 
                    The size of the tile in x axis (int), default is 256
                tile_y : int
                    The size of the tile in y axis (int), default is 256
    """

    def __init__(self, path):
        """
        Read the raster file

            Parameters
            ----------
                path: the path of the raster file

            Returns
            -------
                None: Read raster and assign metadata of raster to the class
        """
        self._read_raster(self, path)

    def __del__(self):
        self.ds.close()

    def _read_raster(self, path):
        """Read the raster file

            Parameters
            ----------
                path: the path of the raster file

            Returns
            -------
                None: Read raster and assign metadata of raster to the class
        """
        self.path = path
        self.ds = rio.open(path)
        self.meta = self.ds.meta
        self.height = self.meta['height']
        self.width = self.meta['width']
        self.meta['crs'] = self.ds.crs

    def _calculate_offset(self, stride_x: Optional[int] = None, stride_y: Optional[int] = None) -> tuple:
        """Calculate the offset for the whole dataset 

            Parameters
            ----------
                tile_x: the size of the tile in x axis
                tile_y: the size of the tile in y axis
                stride_x: the stride of the x axis
                stride_y: the stride of the y axis

            Returns
            -------
                tuple: (offset_x, offset_y)
        """
        self.stride_x = stride_x
        self.stride_y = stride_y

        # offset x and y values calculation
        X = [x for x in range(0, self.ds.width, stride_x)]
        Y = [y for y in range(0, self.ds.height, stride_y)]
        offsets = list(itertools.product(X, Y))
        return offsets

    def generate_raster_tiles(
            self,
            output_folder: str,
            out_bands: Optional[list] = None,
            image_format: Optional[str] = 'tif',
            dtype: Optional[str] = None,
            tile_x: Optional[int] = 256,
            tile_y: Optional[int] = 256,
            stride_x: Optional[int] = 128,
            stride_y: Optional[int] = 128
    ):
        """
        Save the tiles to the output folder

            Parameters
            ----------
                output_folder : str 
                    Path to the output folder
                out_bands : list
                    The bands to save (eg. [3, 2, 1]), if None, the output bands will be same as the input raster bands
                image_format : str 
                    The image format (eg. tif), if None, the image format will be the same as the input raster format (eg. tif)
                dtype : str, np.dtype
                    The output dtype (eg. uint8, float32), if None, the dtype will be the same as the input raster
                tile_x: int
                    The size of the tile in x axis, Default value is 256
                tile_y: int
                    The size of the tile in y axis, Default value is 256
                stride_x: int
                    The stride of the x axis, Default value is 128
                stride_y: int
                    The stride of the y axis, Default value is 128 

            Returns
            -------
                None: save the tiles to the output folder

            Examples
            --------
                >>> import GeoTiler
                >>> tiler = GeoTiler.GeoTiler('/path/to/raster/file.tif')
                >>> tiler.generate_raster_tiles('/path/to/output/folder')
                    # save the specific bands with other than default size
                >>> tiler.generate_raster_tiles('/path/to/output/folder', [3, 2, 1], tile_x=512, tile_y=512, stride_x=0, stride_y=0)
        """

        self.tile_x = tile_x
        self.tile_y = tile_y
        self.stride_x = stride_x
        self.stride_y = stride_y

        # create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # offset calculation
        offsets = self._calculate_offset(self.stride_x, self.stride_y)

        # iterate through the offsets
        for col_off, row_off in offsets:
            window = windows.Window(
                col_off=col_off, row_off=row_off, width=256, height=256)
            transform = windows.transform(window, self.ds.transform)
            meta = self.ds.meta.copy()

            # update the meta data
            meta.update(
                {"width": window.width, "height": window.height, "transform": transform})

            # if the output bands is not None, add all bands to the output dataset
            if out_bands is None:
                out_bands = [i for i in range(0, self.ds.count())]

            else:
                meta.update({"count": len(out_bands)})

            # if data_type, update the meta
            if dtype:
                meta.update({"dtype": dtype})

            else:
                dtype = self.ds.meta['dtype']

            tile_name = 'tile_' + str(col_off) + '_' + \
                str(row_off) + '.' + image_format
            tile_path = os.path.join(output_folder, tile_name)
            # save the tiles with new metadata
            with rio.open(tile_path, 'w', **meta) as outds:
                outds.write(self.ds.read(
                    out_bands, window=window).astype(dtype))

    def mosaic_rasters(self, input_folder: str, output_file: str, image_format: Optional[str] = 'tif', **kwargs):
        """Mosaic the rasters inside the input folder

            This method is used to merge the tiles into single file

            Parameters
            ----------
                input_folder: str, python path 
                    Path to the input folder
                output_file: str, python path
                    Path to the output file
                image_format: str
                    The image format (eg. tif), if None, the image format will be the same as the input raster format.
                kwargs: dict 
                    The kwargs from rasterio.merge.merge can be used here: https://rasterio.readthedocs.io/en/latest/api/rasterio.merge.html#rasterio.merge.merge (e.g. bounds, res, nodata etc.)

            Returns
            -------
                output_file
                    Save the mosaic as a output_file. Returns the output_file path

            Examples
            --------
                >>> import GeoTiler
                >>> tiler = GeoTiler.GeoTiler('/path/to/raster/file.tif')
                >>> tiler.mosaic_rasters('/path/to/input/folder', '/path/to/output/file.tif')
        """

        # get the list of input rasters to merge
        search_criteria = "*.{}".format(image_format)
        q = os.path.join(input_folder, search_criteria)
        input_files = sorted(glob.glob(q))

        # Open and add all the input rasters to a list
        src_files_to_mosaic = []
        for files in input_files:
            src = rio.open(files)
            src_files_to_mosaic.append(src)

        # Merge the rasters
        mosaic, out_trans = merge(src_files_to_mosaic, **kwargs)

        # update the metadata
        meta = src.meta.copy()
        meta.update({
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
        })

        # write the output raster
        with rio.open(output_file, 'w', **meta) as outds:
            outds.write(mosaic)

        return output_file

    def generate_raster_mask_from_shapefile(self, input_shapefile: str, output_file: str, crop=True, invert=False, **kwargs):
        """Generate a mask raster from a shapefile

            Parameters
            ----------
                input_shapefile: str, python path
                    Path to the input shapefile
                output_file: Str, python Path
                    Path to the output location of the mask raster   
                crop: bool
                    If True, the mask will be cropped to the extent of the shapefile
                    If false, the mask will be the same size as the raster
                invert: bool
                    If True, the mask will be inverted, pixels outside the mask will be filled with 1 and pixels inside the mask will be filled with 0
                kwargs: dict
                    The kwargs from rasterio.mask.mask can be used here: https://rasterio.readthedocs.io/en/latest/api/rasterio.mask.html#rasterio.mask.mask (e.g. bounds, res, nodataetc.)

            Returns
            -------
                output_file   
                    Save the mask as a output_file 

            Examples:
                >>> import GeoTiler
                >>> tiler = GeoTiler.GeoTiler('/path/to/raster/file.tif')
                >>> tiler.generate_raster_mask('/path/to/shapefile.shp', '/path/to/output/file.tif')
        """

        # open the input shapefile
        df = gpd.read_file(input_shapefile)

        # check the coordinate system for both raster and shapefile and reproject shapefile if necessary
        raster_crs = self.meta['crs']
        if raster_crs != df.crs:
            df = df.to_crs(raster_crs)

        # get the bounds of the shapefile
        with rio.open(self.path) as src:
            out_image, out_transform = mask(
                src, df["geometry"], crop=crop, invert=invert, **kwargs)
            out_meta = src.meta.copy()

        # update the metadata
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform})

        # write the output raster
        with rio.open(output_file, 'w', **out_meta) as outds:
            outds.write(out_image)

    def rasterize_shapefile(self, input_shapefile: str, output_file: str, value_col=None, **kwargs):
        """Rasterize a shapefile to a raster

            Parameters
            ----------
                input_shapefile: str, python path 
                    Path to the input shapefile
                output_file: str, python path 
                    Path to the output location of the rasterized shapefile  
                value_col: str
                    The column name of the shapefile to be rasterized 
                    If None, the rasterization will be binary otherwise the rasterization will be the based on value of the column 
                kwargs: dict
                    The kwargs from rasterio.rasterize can be used here: https://rasterio.readthedocs.io/en/latest/api/rasterio.rasterize.html#rasterio.rasterize.rasterize (e.g. fill, transform etc.)


            Returns
            -------
                None: save the rasterized shapefile as a output_file 

            Examples:
                >>> import GeoTiler 
                >>> tiler = GeoTiler.GeoTiler('/path/to/raster/file.tif')
                >>> tiler.rasterize_shapefile('/path/to/shapefile.shp', '/path/to/output/file.tif')
        """

        # open the input shapefile
        df = gpd.read_file(input_shapefile)

        # check the coordinate system for both raster and shapefile and reproject shapefile if necessary
        raster_crs = self.meta['crs']
        if raster_crs != df.crs:
            df = df.to_crs(raster_crs)

        # if value column is specified, rasterize the shapefile based on value column else bianary classification
        dataset = zip(df['geometry'], df[value_col]
                      ) if value_col else df['geometry']

        # rasterize the shapefile based on raster metadata
        mask = rasterize(dataset, self.ds.shape,
                         transform=self.meta['transform'], **kwargs)

        # update the metadata
        meta = self.meta.copy()
        meta.update({'count': 1, "dtype": "uint8"})

        # write the output raster
        with rio.open(output_file, 'w', **meta) as outds:
            outds.write(mask)

    def close(self):
        """Close the dataset
        """
        self.ds.close()
