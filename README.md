# gibs_ml
Machine learning for anomaly detection in Global Imagery Browse Services ([GIBS](https://earthdata.nasa.gov/about/science-system-description/eosdis-components/global-imagery-browse-services-gibs)) Earth satellite imagery.

# Dependencies
Run ```conda install gdal``` to install the [GDAL translator library](http://www.gdal.org/). 

# Download Data
Run ```download_data.py``` to download a GIBS layer dataset. The script uses ```gdal_translate``` with the [GIBS API](https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+API+for+Developers#GIBSAPIforDevelopers-ServiceEndpointsandGetCapabilities).

The layer for each day can either be a single image (by default) or tiled (set ```--tiled_world``` flag).  

Images are saved in the ```data/``` directory by default. The folder structure is ```data/{EPSG code}/{YYYY-MM-DD}/```.

```
arguments:
  --layer_name          The layer name to download.  Default:  VIIRS_SNPP_CorrectedReflectance_TrueColor

  --start_date          The date from which to begin (inclusive) searching back in format YYYY-MM-DD.  Default:  None (uses layer start date)
  --end_date            The date to stop (non-inclusive) searching in format YYYY-MM-DD (or "Today").  Default:  Date of last check or Today

  --epsg                The numeric EPSG code of the map projection {4326:geographic, 3413:arctic, 3031:antarctic}.  Default:  4326 (geographic)
  
  --tiled_world         Flag to download the entire world as a series of tiled images.

  --tile_resolution     The zoom resolution of the tiles. Must be lower than the image resolution of layer.  Default:  8km
  
  --num_threads         Number of concurrent threads to launch to download images.  Default:  20

  --output_dir          Full path of output directory.  Default:  ./data
```

# Data Preprocessing
Run ```augment_data.py``` to augment the training dataset by rotations (90, 180, 270 degrees) and flips (horizontal and vertical).
