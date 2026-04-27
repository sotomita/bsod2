# bsod2

<p>
<a href="https://github.com/sotomita/bsod2/actions/workflows/publish.yml"><img src="https://github.com/sotomita/bsod2/actions/workflows/publish.yml/badge.svg"></a>
<img src="https://img.shields.io/github/license/sotomita/bsod2">
<img src="https://img.shields.io/badge/-Python-gray.svg?logo=Python">
</p>

BSoD2(BalloonScope on Deck 2) is a package in Python for reading radiosonde data.

## Requirements
- numpy == 2.4.3
- pandas == 3.0.2
- metpy == 1.7.1

## Installation
This package can be installed from [PyPI](https://pypi.org/project/bsod2/).
```
pip install bsod2
```

## Usage
The only functionality provided by this package is the `bsod2.Sonde` class, which retrieves radiosonde data and performs quality control.

### Basic `Sonde` construction and methods
Initialize the class with the file path to the raw data.
```
from pathlib import Path
from bsod2 import Sonde

data = Sonde(Path("Seisuimaru2407/raw_data/F2024061806S1101771.CSV"))
data
>>> Sonde(sonde_no=1101771, launch_time=2024-06-18 06:01:42, product_name=iMS-100 , num_records=1101)
```

### Accessors for observed variables
The following accessors can be used to retrieve meteorological variables.  
Most accessors return values with `metpy.units.units` attached.

| Accessor | units | Description | Example |
|----------|-------------|---------| ---------|
|`df`|`NOne`| quality-controlled `pandas.DataFrame`|`sonde.df`|
|`time`|`None`|Time|`sonde.time`|
|`lat`|`units("deg")`| Latitude|`sonde.lat`|
|`lon`|`units("deg")`| Longitude|`sonde.lon`|
|`x`|`units("m")`| X-displacement from the launch point|`sonde.x`|
|`y`|`units("m")`| Y-displacement from the launch point|`sonde.y`|
|`z`| ```units("m")```  | Altitude | `sonde.z` |
|`p`| ```units("hPa")```  | Pressure | `sonde.p` |
|`t`| ```units("degC")```| Temperature | `sonde.temp` |
|`rh`|```units("percents")```| Relative humidity | `sonde.rh` |
|`wd`|```units("deg")```| Wind direction | `sonde.wd` |
|`ws`| ```units("m/s")```| Wind speed | `sonde.ws` |


### Save as CSV
Save the quality-controlled DataFrame as a CSV file to the specified file path using the `save_df` method.
```
data.save_df(Path("output.csv"))

```

### Altitude or pressure interpolation
Interpolate linearly onto an evenly spaced grid in pressure or altitude using the `interp` argument.
```
data = Sonde(FILE_PATH,interp="p")
```
By default, the interpolated pressure axis ranges from 100 to 1100 hPa at 1 hPa intervals, and the height axis ranges from 0 m to 2000 m at 10 m intervals.   
Values outside the original data range are filled with NaN. The range and resolution of the interpolation axes can be specified using the following arguments.

| Argument      | Description                                                                 | Default |
|---------------|-----------------------------------------------------------------------------|---------|
| `interp`      | Name of the interpolation axis. If None, interpolation is not performed.    | None    |
| `interp_pmin` | Minimum value of the interpolated pressure axis (hPa)                       | 50     |
| `interp_pmax` | Maximum value of the interpolated pressure axis (hPa)                       | 1100    |
| `interp_dp`   | Step size of the interpolated pressure axis (hPa)                           | 1       |
| `interp_zmin` | Minimum value of the interpolated height axis (m)                           | 0       |
| `interp_zmax` | Maximum value of the interpolated height axis (m)                           | 20000   |
| `interp_dz`   | Step size of the interpolated height axis (m)                               | 10      |

## Sample plots
### data
Sample data was observed in Seisui-maru 2407 cruise
(2024年度　三重大学　陸海空・環境科学実習).
- [raw data](sample/Seisuimaru2407/raw_data/)
- [field book(pdf)](sample/Seisuimaru2407/2407オペレーター野帳.pdf)

### emagram
<p align="center">
 <img src="docs/images/emagram.png" width="400" alt="emagram">
</p>

#### additional dependencies
- matplotlib

See [emagram.ipynb](sample/emagram.ipynb) for more details.

### z vs. sonde variables plot
<p align="center">
 <img src="docs/images/vertical_profile.png" width="600" alt="vertical profile of observed sonde variables">
</p>

#### additional dependencies
- matplotlib


See [z_vs_var.ipynb](sample/z_vs_var.ipynb) for more details.

### time-z cross section plot
<p align="center">
  <img src="docs/images/vert_csec.png" width="600" alt="time-z cross section of relative humidity">
</p>

#### additional dependencies
- matplotlib
- xarray

See [vertcal_csec.ipynb](sample/vertical_csec.ipynb) for more details.

### 2D/3D trajectories plot
<p align="center">
  <img src="docs/images/trj2d.png" width="300" alt="2D trajectories">
  <img src="docs/images/trj3d.png" width="300" alt="3D trajectories">
</p>
<p align="center">
  <img src="docs/images/trj3d_animation.gif", width="600" alt="animation of 3D trajectories">
</p>

#### additional dependencies
- matplotlib
- cartopy
- pygmt
- imageio
- tqdm

See [trajectory.ipynb](sample/trajectory.ipynb) for more details.

## License
This project is distributed under the terms of the GNU General Public License, Version 3 (GPLv3).  
See the [LICENSE](LICENSE) file for details.