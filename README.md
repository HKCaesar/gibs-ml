# gibs_ml
Machine learning for anomaly detection in Global Imagery Browse Services ([GIBS](https://earthdata.nasa.gov/about/science-system-description/eosdis-components/global-imagery-browse-services-gibs)) Earth satellite imagery.

# Dependencies
Run ```conda install gdal``` to install the [GDAL translator library](http://www.gdal.org/). 

# Download Data
Run ```download_data.py``` to download a GIBS dataset. The script generates [```gdal_translate```](http://www.gdal.org/gdal_translate.html) commands to synchronously download images from the [GIBS API](https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+API+for+Developers#GIBSAPIforDevelopers-ServiceEndpointsandGetCapabilities).

Each layer for a day is a single image by default or can be tiled (set the ```--tiled_world``` flag).  

Images are saved in the ```data/``` directory by default. The folder structure is ```data/{EPSG code}/{YYYY-MM-DD}/```.

```
arguments:
  --time_begin          The date from which to begin searching back in format YYYY-MM-DD.  Default:  Today
  --time_stop           The date to stop searching in format YYYY-MM-DD.  Default:  Date of last check or Today-20
  
  --epsg                The numeric EPSG code of the map projection {4326:geographic, 3413:arctic, 3031:antarctic}.  Default:  4326 (geographic)
  
  --tiled_world         Flag to download the entire world as a series of tiled images.
  --tile_resolution     The zoom resolution of the tiles. Must be lower than the image resolution of layer.  Default:  8km
  
  --num_threads         Number of concurrent threads to launch to download images.  Default:  10
  --output_dir          Full path of output directory.  Default:  ./data
```

# Data Preprocessing
Run ```augment_data.py``` to augment the training dataset by rotations (90, 180, 270 degrees) and flips (horizontal and vertical).
