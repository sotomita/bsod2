# Sample


### data
Sample data was observed in Seisui-maru 2407 cruise
(2024年度　三重大学　陸海空・環境科学実習).
- [raw data](Seisuimaru2407/raw_data/)
- [field book(pdf)](Seisuimaru2407/2407オペレーター野帳.pdf)

### emagram
<p align="center">
 <img src="../docs/images/emagram.png" width="400" alt="emagram">
</p>

#### additional dependencies
- matplotlib
- metpy
- numpy

See [emagram.ipynb](emagram.ipynb) for more details.

### z vs. sonde variables plot
<p align="center">
 <img src="../docs/images/vertical_profile.png" width="600" alt="vertical profile of observed sonde variables">
</p>

#### additional dependencies
- matplotlib
- numpy

See [z_vs_var.ipynb](z_vs_var.ipynb) for more details.


### time-z cross section plot
<p align="center">
  <img src="../docs/images/vert_csec.png" width="600" alt="time-z cross section of relative humidity">
</p>

#### additional dependencies
- matplotlib

See [vertcal_csec.ipynb](vertical_csec.ipynb) for more details.

### 2D/3D trajectories plot
<p align="center">
  <img src="../docs/images/trj2d.png" width="300" alt="2D trajectories">
  <img src="../docs/images/trj3d.png" width="300" alt="3D trajectories">
</p>
<p align="center">
  <img src="../docs/images/trj3d_animation.gif", width="600" alt="animation of 3D trajectories">
</p>

#### additional dependencies
- matplotlib
- cartopy
- pygmt
- imageio
- tqdm

See [trajectory.ipynb](trajectory.ipynb) for more details.