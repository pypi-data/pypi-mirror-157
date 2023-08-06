##########################################################################
# Track Analyzer - Quantification and visualization of tracking data     #
# Authors: Arthur Michaut                                                #
# Copyright 2016-2019 Harvard Medical School and Brigham and             #
#                          Women's Hospital                              #
# Copyright 2019-2022 Institut Pasteur and CNRS–UMR3738                  #
# See the COPYRIGHT file for details                                     #
#                                                                        #
# This file is part of Track Analyzer package.                           #
#                                                                        #
# Track Analyzer is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# Track Analyzer is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the           #
# GNU General Public License for more details .                          #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with Track Analyzer (COPYING).                                   #
# If not, see <https://www.gnu.org/licenses/>.                           #
##########################################################################

import os.path as osp
import sys
import argparse

from track_analyzer import prepare as tpr
from track_analyzer import plotting as tpl
from track_analyzer import calculate as tca


def make_default_config(data_dir):
    """Make default config and export it to data_dir"""

    config_dir = osp.join(data_dir, 'config')
    tpr.safe_mkdir(config_dir)

   
    data_config = tpr.make_data_config(data_dir=data_dir, export_config=True)
    plot_config = tpl.make_plot_config(data_dir=data_dir, export_config=True)
    traj_config = tpr.make_traj_config(data_dir=data_dir, export_config=True)
    map_config = tpr.make_map_config(data_dir=data_dir, export_config=True,empty_run=False)

    config = {'data_config':data_config, 
            'plot_config':plot_config, 
            'traj_config':traj_config, 
            'map_config':map_config, 
            }

    return config


def parse_args(args=None):
    """
    parse arguments for main()
    """

    parser = argparse.ArgumentParser(description="""
        Make a default set of config files and save it to data_dir
        """)

    parser.add_argument('data_dir',
                        help='path of the data directory')

    parsed_args = parser.parse_args(args)

    return parsed_args


def main(args=None):
    """ main function to run traj_analysis from command line"""

    args = sys.argv[1:] if args is None else args
    parsed_args = parse_args(args)

    data_dir = osp.realpath(parsed_args.data_dir)

    if not osp.exists(data_dir):
        raise Exception("ERROR: the passed data directory does not exist. Aborting...")

    if not osp.isdir(data_dir):
        raise Exception("ERROR: the passed data directory is not a directory. Aborting...")

    # make config
    make_default_config(data_dir)


if __name__ == '__main__':
    main()
