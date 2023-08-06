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

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
from skimage.color import rgb2gray
from skimage.util import img_as_ubyte
import seaborn as sns
import tifffile as tifff

from track_analyzer import prepare as tpr

# Plotting parameters
color_list = [c['color'] for c in list(plt.rcParams['axes.prop_cycle'])] + sns.color_palette("Set1", n_colors=9,
                                                                                             desat=.5)

mpl.use('agg')

# parameters
traj_num = 500  # number of tracks
frame_num = 5  # number of frame
dim = 2  # dimension
lims = [[0, 500], [0, 500]]  # space limits
periodic = False  # space periodicity
random = False  # initial position spacing
space = {'dim': dim, 'lims': lims, 'periodic': periodic, 'random': random}
pos0_lims = [[100, 400], [100, 400]]  # initial position limits
diff_field = {'cst': 1}  # random motion amplitude  (in px**2/time_unit)
vel_field = [{'a': 0.01, 'p': 2, 'b': 250, 'c': -0.01, 'q': 2, 'd': 250},  # vx = x^2 - y^2 (centered) (in px/time_unit)
             {'a': 0.01, 'p': 2, 'b': 250, 'c': -0.01, 'q': 2, 'd': 250},  # vy = x^2 - y^2 (centered) (in px/time_unit)
             ]
timescale = 1
lengthscale = 1


def init_config(traj_num=traj_num, frame_num=frame_num, space=space, pos0_lims=pos0_lims, diff_field=diff_field,
                vel_field=vel_field, timescale=timescale, lengthscale=lengthscale):
    """
    Make config_default
    """
    config_default = {'traj_num': traj_num,
                      'frame_num': frame_num,
                      'space': space,
                      'pos0_lims': pos0_lims,
                      'diff_field': diff_field,
                      'vel_field': vel_field,
                      'lengthscale': lengthscale,
                      'timescale': timescale,
                      }
    return config_default


def get_config(data_dir):
    """
    Load from config file 'config.csv' if it exists, else return None
    """

    config_fn = osp.join(data_dir, 'config.csv')
    if osp.exists(config_fn):
        config = tpr.load_dict(config_fn)
    else:
        config = None

    return config


def make_pos0(pos0_lims=pos0_lims, traj_num=traj_num, random=True):
    """
    Generate list of initial positions at random position within boudaries given by pos0_lims 
    """
    pos0_list = []

    if random:
        for i in range(traj_num):
            pos0 = np.array([np.random.uniform(pos0_lims_[0], pos0_lims_[1]) for pos0_lims_ in pos0_lims])
            pos0_list.append(pos0)
    else:
        # create a rectangle array of N_ positions evenly spaced 
        # height/width = N_h/N_w and N_h*N_w = N_ 
        width = np.abs(pos0_lims[0][1] - pos0_lims[0][0])
        height = np.abs(pos0_lims[1][1] - pos0_lims[1][0])
        N_ = int(np.sqrt(traj_num)) ** 2  # number of positions needs to be a square number
        N_h = int(np.sqrt(N_) * height / width)
        N_w = int(N_ / N_h)

        # meshgrid
        X, Y = np.meshgrid(np.linspace(pos0_lims[0][0], pos0_lims[0][1], N_w),
                           np.linspace(pos0_lims[1][0], pos0_lims[1][1], N_h))
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                pos0_list.append(np.array([X[i, j], Y[i, j]]))

    return pos0_list


def polynom_mapping(pos, params={'cst': 0}, space=space):
    """
    Evaluate polynomial at position pos.
    Polynomial function: a*(x-b)^p + c*(y-d)^q + e*(z-f)^r + cst
    Useful to generate a velocity field with polynomial expression
    """

    # put parameter to either if missing
    for p in list('abcdefpqr') + ['cst']:
        if p not in params.keys():
            params[p] = 0

    # check dimension of position compatible with space dimension
    pos_dim = len(pos)
    if pos_dim > space['dim']:
        raise Exception('position dimension larger than space dimension')

    value = params['cst']

    if pos_dim == 1:
        value += params['a'] * ((pos[0] - params['b']) ** params['p'])

    elif pos_dim == 2:
        value += params['a'] * ((pos[0] - params['b']) ** params['p'])
        value += params['c'] * ((pos[1] - params['d']) ** params['q'])

    elif pos_dim == 3:
        value += params['a'] * ((pos[0] - params['b']) ** params['p'])
        value += params['c'] * ((pos[1] - params['d']) ** params['q'])
        value += params['e'] * ((pos[2] - params['f']) ** params['r'])

    return value


def n_polynom_mapping(pos, params_list=[{'cst': 0}], space=space):
    """
    n-dimension polynomial evaluation at position pos using polynom_mapping()
    """

    # check there is a set of parameters along each space dimension
    if len(params_list) != space['dim']:
        raise Exception('params_list must have the same size as space dimension')

    vector = []
    for i in range(space['dim']):
        vector.append(polynom_mapping(pos, params=params_list[i], space=space))

    return np.array(vector)


def export_vel_fields(vel_field, pos_list, data_dir, space=space):
    """
    Export velocity curl and div fields evaluated at an list of positions.
    vel_field (generated by n_polynom_mapping) is a list of n elements (n=2 or 3), each element being a spatial component
    """

    # check 2D velocity field is 2D
    if len(vel_field) < 2:
        raise Exception("Need a 2D velocity field")

    # check missing parameters in vel_field
    for i in range(len(vel_field)):
        for p in list('abcdefpqr'):
            if p not in vel_field[i].keys():
                vel_field[i][p] = 0

    # get velocity list
    vel_list = []
    for pos in pos_list:
        vel_list.append(n_polynom_mapping(pos, params_list=vel_field, space=space))

    # calculate v
    v_arr = np.array(vel_list)
    v_modulus = np.sqrt(np.sum(v_arr**2,axis=1))
    v_arr = np.concatenate((v_arr,np.array([v_modulus]).T),axis=1)

    # calculate 2D curl and div
    curl_list = []
    div_list = []
    for pos in pos_list:
        # curl
        curl = dx_polynom(vel_field[1], pos) - dy_polynom(vel_field[0], pos)  # Dx_vy - Dy_vx
        curl_list.append(curl)
        # div
        div = dx_polynom(vel_field[0], pos) + dy_polynom(vel_field[1], pos)  # Dx_vx + Dy_vy
        div_list.append(div)

    # save to df 
    data = np.concatenate((np.array(pos_list), v_arr, np.array([curl_list]).T, np.array([div_list]).T),axis=1)

    columns = ['x', 'y', 'vx', 'vy', 'vz', 'v', 'curl', 'div'] if len(vel_field) == 3 else ['x', 'y', 'vx', 'vy', 'v', 
                                                                                        'curl','div']
    df_out = pd.DataFrame(data, columns=columns)
    df_out.to_csv(osp.join(data_dir, 'v_fields.csv'))


def export_diff_field(diff_field, pos_list, data_dir, space=space, timescale=timescale):
    """
    Export diffusion coefficient field evaluated at an list of positions.
    diff_field (generated by polynom_mapping) is the noise_amplitude field. diffusion = noise_amp ** 2 / (2. * dim * dt)
    """

    # get velocity list
    D_list = []
    for pos in pos_list:
        D_list.append(polynom_mapping(pos, diff_field, space))

    # save to df 
    data = np.concatenate((np.array(pos_list), np.array([D_list]).T), axis=1)

    df_out = pd.DataFrame(data, columns=['x', 'y', 'D'])
    df_out.to_csv(osp.join(data_dir, 'D_fields.csv'))


def dx_polynom(polynom, pos):
    """
    x-component of spatial derivative of polynom_mapping at position pos
    """
    if polynom['p'] > 0:
        value = polynom['a'] * polynom['p'] * (pos[0] - polynom['b']) ** (polynom['p'] - 1)
    else:
        value = 0

    return value


def dy_polynom(polynom, pos):
    """
    y-component of spatial derivative of polynom_mapping at position pos
    """
    if polynom['q'] > 0:
        value = polynom['c'] * polynom['q'] * (pos[1] - polynom['d']) ** (polynom['q'] - 1)
    else:
        value = 0

    return value


def make_traj(pos0, frame_num=frame_num, diff_field=diff_field, vel_field=vel_field, space=space, track_id=0,
              timescale=timescale):
    """
    Generate a trajectory of frame_num positions from a an initial position pos0. 
    At each frame, the displacement is given by the superposition of a diffusive component and ballistic component.
    Each component are computed at the position using the diffusion filed diff_field and the velocity field vel_field.
    """

    traj = pd.DataFrame(columns=['track', 'frame'] + list('xyz')[:space['dim']])

    pos = np.array(pos0)  # intialize position
    pos = pos.astype('float64')

    traj.loc[0, :] = np.concatenate(([track_id, 0],pos))

    for frame in range(1, frame_num):  # first position already given

        # diffusive component
        diff = np.random.randn(space['dim'])
        diff_2 = diff ** 2
        diff_normalized = diff / np.sqrt(diff_2.sum())  # unit diffusion vector
        D = polynom_mapping(pos, diff_field, space)  # diffusion coefficient at pos
        diff_ampl = np.sqrt(2 * space['dim'] * D * timescale)   # diffusion amplitude

        # ballistic component
        vel = n_polynom_mapping(pos, params_list=vel_field, space=space)  # velocity at pos
        vel = vel.astype('float64')

        # new position
        pos += vel * timescale + diff_ampl * diff_normalized  # pos += v*dt + noise_amplitude

        if periodic:
            for i in range(len(pos)):
                pos[i] = np.remainder(pos[i], space['lims'][i])

        traj.loc[frame, :] = [track_id, frame] + list(pos)

    return traj


def make_dataset(pos0_list, frame_num=frame_num, diff_field=diff_field, vel_field=vel_field, space=space,
                 timescale=timescale):
    """
    Make set of trajectories using make_traj
    """

    dimensions = list('xyz')[:space['dim']]
    df = pd.DataFrame(columns=['track', 'frame'] + dimensions)

    for i, pos0 in enumerate(pos0_list):
        traj = make_traj(pos0, frame_num=frame_num, diff_field=diff_field, vel_field=vel_field, space=space, track_id=i,
                         timescale=timescale)

        df = pd.concat([df, traj], ignore_index=True)

    return df


def plot_synthetic_stack(df, outdir, dpi=300, image_size=[500, 500], frame_num=10, lengthscale=lengthscale):
    """Plot synthetic data and save it as a grayscaled tiff stack"""

    stack = []  # stack to store images

    # scale to px
    df_ = df.copy()
    df_['x'] = df_['x']/lengthscale
    df_['y'] = df_['y']/lengthscale

    groups = df_.groupby('frame')

    # plot frames
    for i in range(frame_num):
        group = groups.get_group(i).reset_index(drop=True)

        figsize = (image_size[0] / dpi, image_size[1] / dpi)
        fig = plt.figure(frameon=False, figsize=figsize, dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        for k in range(group.shape[0]):
            ax.scatter(group.loc[k, 'x'], group.loc[k, 'y'], s=3)
        ax.set_xlim(0, image_size[0])
        ax.set_ylim(0, image_size[1])
        ax.invert_yaxis()
        ax.axis('off')

        fig.canvas.draw()
        fig_image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        fig_image = fig_image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        fig_image = rgb2gray(fig_image)  # convert to grayscale
        fig_image = img_as_ubyte(fig_image)  # convert to 8 bit
        stack.append(fig_image)
        plt.close(fig)

    # save
    stack = np.array(stack)
    tifff.imwrite(osp.join(outdir, 'stack.tiff'), stack)
