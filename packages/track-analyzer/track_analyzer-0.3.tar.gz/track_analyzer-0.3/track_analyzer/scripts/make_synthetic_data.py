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

import numpy as np

from track_analyzer import prepare as tpr
from track_analyzer import synthetic_data as tsy


def parse_args(args=None):
    """
    parse arguments for main()
    """

    parser = argparse.ArgumentParser(description="""Generate synthetic data""")

    parser.add_argument('data_dir',
                        help='path of the data directory')

    parser.add_argument('-p', '--plot',
                        action="store_true",
                        default=False,
                        help='plot positions and save to tif stack')

    parsed_args = parser.parse_args(args)

    return parsed_args


def main(args=None):
    """
    Generate synthetic trajectories using a diffusion and velocity fields (expressed as polynomials)
    """
    args = sys.argv[1:] if args is None else args

    parsed_args = parse_args(args)

    data_dir = osp.realpath(parsed_args.data_dir)
    plot = parsed_args.plot

    # get config 
    config_default = tsy.init_config()
    config_ = tsy.get_config(data_dir)
    config = config_default if config_ is None else config_

    traj_num = config["traj_num"]  # number of tracks
    frame_num = config["frame_num"]  # number of frame
    space = config["space"]
    pos0_lims = config["pos0_lims"]  # initial position limits
    diff_field = config["diff_field"]  # constant diffusion 
    vel_field = config["vel_field"]
    timescale = config["timescale"]
    lengthscale = config["lengthscale"]

    if lengthscale != 1:
        print('WARNING: div and curl calculations are not supported for lengthscales different than 1. Current lengthscale={}'.format(lengthscale))

    pos0_list = tsy.make_pos0(pos0_lims=pos0_lims, traj_num=traj_num, random=space['random'])
    df = tsy.make_dataset(pos0_list, frame_num=frame_num, diff_field=diff_field, vel_field=vel_field, space=space,
                          timescale=timescale)
    df.to_csv(osp.join(data_dir, 'positions.csv'), index=False)

    # save parameters
    parameters = {'space': space,
                  'pos0_lims': pos0_lims,
                  'traj_num': traj_num,
                  'diff_field': diff_field,
                  'vel_field': vel_field,
                  'frame_num': frame_num,
                  }

    tpr.write_dict(parameters, osp.join(data_dir, 'parameters.csv'))

    # save info
    width = int(np.abs(space['lims'][0][1] - space['lims'][0][0]) / lengthscale)
    height = int(np.abs(space['lims'][1][1] - space['lims'][1][0]) / lengthscale)
    info = {'length_unit': 'um',
            'time_unit': 's',
            'lengthscale': lengthscale,
            'timescale': timescale,
            'image_width': width,
            'image_height': height,
            'table_unit': 'unit',
            'z_step': 0,
            }

    info_fn = osp.join(data_dir, 'info.txt')
    with open(info_fn, 'w+') as f:
        for k in info.keys():
            f.write('{}:{}\n'.format(k, info[k]))

    # calculate theoretical v,div,curl and D and export
    tsy.export_vel_fields(vel_field,pos0_list,data_dir,space)
    tsy.export_diff_field(diff_field,pos0_list,data_dir,space,timescale)

    if plot:
        image_size = [width, height]
        tsy.plot_synthetic_stack(df, data_dir, dpi=300, image_size=image_size,
                                 frame_num=frame_num,lengthscale=lengthscale)


if __name__ == '__main__':
    main()
