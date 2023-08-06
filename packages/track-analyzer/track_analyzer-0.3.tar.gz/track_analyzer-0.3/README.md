
[![Doc](https://img.shields.io/badge/doc-master-blue.svg)](http://track-analyzer.pages.pasteur.fr/track-analyzer)
[![Open Source License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://opensource.org/licenses/GPL-3.0)
[![PyPI](https://img.shields.io/pypi/v/track-analyzer)](https://pypi.org/project/track-analyzer/)
![Conda](https://img.shields.io/conda/pn/bioconda/track_analyzer)


# Track Analyzer :microscope: :bar_chart:
Quantification and visualization of tracking data

**Track Analyzer** is Python-based data visualization pipeline for tracking data.
It *does not* perform any tracking, but visualizes and quantifies any kind of tracked data.
It analyzes trajectories by computing standard quantities such as velocity,
acceleration, diffusion coefficient, local density, etc. 
Trajectories can also be plotted on the original image in 2D or 3D using custom color-coding.

**Track Analyzer** provides a filtering section that can extract subsets of data based on spatiotemporal criteria.
The filtered subsets can then be analyzed either independently or compared. This filtering section also provides a tool
for selecting specific trajectories based on spatiotemporal criteria which can be useful to perform fate mapping and back-tracking.

**Track Analyzer** is distributed as two versions: an [installation-free web-based interface](https://galaxy.pasteur.fr/root?tool_id=toolshed.pasteur.fr/repos/rplanel/track_analyzer/track-analyzer/0.1.0) run on [Galaxy](https://galaxyproject.org/), and a full version that has to be run on a local machine. On both versions, **Track Analyzer** can be run without any programming knowledge using its graphical interface. The full version interface is launched by running a [Jupyter notebook](https://jupyter.org/) containing widgets allowing the user to load data and set parameters without writing any code. 


![screenshot_1](https://gitlab.pasteur.fr/track-analyzer/track-analyzer/-/raw/master/resources/screenshot_1.png)

![screenshot_2](https://gitlab.pasteur.fr/track-analyzer/track-analyzer/-/raw/master/resources/screenshot_2.png)


## Data requirements
The mandatory input file of **Track Analyzer** is a data table (a csv or txt file) of tracks containing the position coordinates (in 2D or 3D) along time and the tracks identifiers. 
Optionally, data can be plotted on the original image provided as a 3D or 4D tiff stack (ie. 2D+time or 3D+time). If the format of your movie is 
different (list of images), please convert it to tiff stack using [Fiji](https://fiji.sc/) for instance. 

The position file must contain columns with the x, y, (z) positions, a frame column and track id column. The positions coordinates can be in 
pixels or in scaled data. The information about the scaling and other metadata such as time and length scales will be provided by the user through the graphical interface.


## Full version installation
If you want to benefit from all the functionalities (especially 3D rendering and hand-drawing selection), you need to install the full version locally on your machine. 
It is fully written in Python, so you just need to have Python running on your machine. If you haven't installed Python yet, install Python 3.7. For instance, just download [miniconda 3.7](https://docs.conda.io/en/latest/miniconda.html). Then you can install **Track Analyzer** in a virtual environment using conda or virtualenv. 

### Installation with conda

To install **Track Analyzer**, just run on a Terminal (Mac & Linux) or open an Anaconda powershell (Windows):

```sh
    conda create -n pyTA python=3.7
    conda activate pyTA
    pip install track-analyzer
```

### Installation with a virtualenv

You can also use a [virtual environment](<https://virtualenv.pypa.io/en/stable/>)

```sh
    python3 -m venv pyTA
    cd pyTA
    source bin/activate
    pip install track-analyzer
```

to exit from the virtualenv
```sh
    deactivate
```

To run track-analyzer
```sh
    cd pyTA
    source bin/activate
```


## Installation-free version
The installation-free online version is available [here](https://galaxy.pasteur.fr/root?tool_id=toolshed.pasteur.fr/repos/rplanel/track_analyzer/track-analyzer/0.1.0). It is run on the web-based platform [Galaxy](https://galaxyproject.org/), which is easy to use (some documentation regarding Galaxy is available [here](https://training.galaxyproject.org/training-material/)). A quickstart tutorial to Galaxy's interface is presented in Track Analyzer's [documentation](https://track-analyzer.pages.pasteur.fr/track-analyzer/). 

## Documentation
You can find a complete documentation [here](https://track-analyzer.pages.pasteur.fr/track-analyzer/).

## Troubleshooting
- The 3D visualization and the drawing selection tool depend on the [napari](https://napari.org/) package. 
The installation of this package can lead to issues depending on your system.
If you are not able to solve this installation, you will not be able to have access to 3D rendering. However, you will still be able to use **Track Analyzer** without the drawing tool, by using coordinates sliders in the graphical interface.
- The execution of blocks in the Jupyter notebook can be buggy because of the large number of widgets. If you can't normally execute a block by pressing Shift+Enter, use the Execute button at the top of the notebook. 
 