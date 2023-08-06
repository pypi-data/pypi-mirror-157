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

from track_analyzer.synthetic_data import *
from track_analyzer import prepare as tpr

outdir = '/Users/amichaut/Desktop/test_stretch'
tpr.safe_mkdir(outdir)

# parameters
part_num = 50  # number of particles
noise_amp = 0.5  # uniform noise amplitude for make_attraction_node
grid_size = [500,500,500]  # grid size
tmax = 80  # frame number
periodic = False
dt = 1.  # time scale
dim = 3  # dimension
bias_basis = [0,0,0]  # constant bias (without gradient)
diff_grad = {'min':0.5,'max':0.5}  # gradient of noise
bias_grad = {'min':0,'max':5,'dim':0} # gradient of bias (min, max amplitude, dim: orientation of bias 0:x,1:y,2:z)
grad = {'step_num':10,'dim':0} # gradient shape (number of steps, dimension 0:x, 1:y, 2:z)
x0_range = {'x':[0.1,0.3],'y':[0.1,0.9],'z':[0.1,0.9]} # boundaries of initial positions
attraction_ampl = 3 # only for make_attraction_node
movement_type = 'gradient'  # 'gradient' or 'node'


def main():
    """
    Generate a series of tracks using two kinds of movements: 
        - a random walk with, optionnally, a bias and/or some spatial gradient of amplitude
        - a movement towards an attraction/repulsion node, with optionnaly a random motion
    Tracks are saved as positions in csv files. The properties of each track are saved in a different csv file. Trajectories images are plotted to a tif file. 
    """
    # generate positions 
    if movement_type == 'gradient':
        df,df_param = make_spatial_gradient(part_num,grid_size,dim,tmax,periodic,bias_basis,diff_grad,bias_grad,grad,x0_range,dt=dt)
    elif movement_type == 'node':
        df,df_param = make_attraction_node(part_num,grid_size,dim,tmax,periodic,noise_amp,bias_basis,attraction_ampl=attraction_ampl,x0_range=x0_range,dt=dt)

    # save positions and tracks parameters
    df.to_csv(osp.join(outdir,'positions.csv')) # positions
    df_param.to_csv(osp.join(outdir,'params.csv')) # parameters of each track

    #make info
    info = {'length_unit':'um',
            'time_unit':'min',
            'lengthscale':1,  # by defaut 
            'timescale':dt,
            'image_width':grid_size[0],
            'image_height':grid_size[1],
            'table_unit':'px',
            'z_step':1
            }
    info_fn = osp.join(outdir,'info.txt')
    with open(info_fn,'w+') as f:
        for key in info.keys():
            f.write('{}:{}\n'.format(key,info[key]))

    # plot tracks
    plot_synthetic_stack(df,outdir,grid_size=grid_size,tmax=tmax)


if __name__ == '__main__':
    main()

