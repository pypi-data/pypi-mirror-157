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

import matplotlib as mpl

from track_analyzer import prepare as tpr
from track_analyzer import plotting as tpl
from track_analyzer import calculate as tca


def map_analysis(data_dir, data=None, image=None, refresh=False, parallelize=False, filters=None,
                 plot_config=None, map_config=None, data_config=None, quiet=0):
    """Container method to plot a series of maps given by field_values. Manual vlim to colormap can be passed."""

    map_dir = osp.join(data_dir, 'map_analysis')
    tpr.safe_mkdir(map_dir)

    # Get image
    image = tpr.get_image(data_dir) if image is None else image

    # Get data
    data_config = tpr.make_data_config(data_dir=data_dir, export_config=False) if data_config is None else data_config
    # check that all configs are in data_config, if not load default
    data_config_default = tpr.make_data_config(data_dir=data_dir, export_config=False)
    for k in data_config_default.keys():
        if k not in data_config.keys():
            data_config[k] = data_config_default[k]
    if data is None: 
        data = tpr.get_data(data_dir, refresh=refresh, split_traj=data_config["split_traj"], set_origin_=data_config["set_origin_"], 
                            image=image, reset_dim=data_config["reset_dim"], invert_axes=data_config["invert_axes"], 
                            trackmate_input=data_config["trackmate_input"])

    df = data['df']
    dimensions = data['dimensions']
    lengthscale = data['lengthscale']
    custom_var = data['custom_var']

    # Get plot_config
    plot_config = tpl.make_plot_config(data_dir=data_dir, export_config=False) if plot_config is None else plot_config
    # check that all configs are in plot_config, if not load default
    plot_config_default = tpl.make_plot_config(data_dir=data_dir, export_config=False)
    for k in plot_config_default.keys():
        if k not in plot_config.keys():
            plot_config[k] = plot_config_default[k]
    if plot_config['save_as_stack']:
        mpl.use('agg')  # need to switch backend to use matplotlib tostring_rgb()

    # Get map_config
    map_config_default = tpr.make_map_config(data_dir=data_dir, export_config=False)
    map_config = map_config_default if map_config is None else map_config

    # check that all configs are in map_config, if not load default
    for key in map_config_default.keys():
        if key not in map_config.keys():
            map_config[key] = map_config_default[key]
        # add default param if missing
        for k in map_config_default[key].keys():
            if k not in map_config[key].keys():
                map_config[key][k] = map_config_default[key][k]

    grid_param = map_config["grid_param"]
    map_param = map_config["map_param"]
    scalar_fields = map_config["scalar_fields"]
    vector_fields = map_config["vector_fields"]
    vector_mean = map_config["vector_mean"]

    # Filter data
    filters = tpr.init_filters(data_dir=data_dir, export_config=True) if filters is None else filters
    # check that all keys are in filters, if not load default
    filters_default = tpr.init_filters(data_dir=data_dir, export_config=False)
    filters_default_dict = filters_default['filters_list'][0]
    for k in filters_default.keys():
        if k not in filters.keys():
            filters[k] = filters_default[k]
    # check all filter_subset
    for i,filter_ in enumerate(filters['filters_list']): 
        for k in filters_default_dict.keys():
            if k not in filter_.keys():
                filter_[k] = filters_default_dict[k]
        filters['filters_list'][i] = filter_

    subset_analysis = filters['subset']  # how to deal with subsets
    filters_ = filters['filters_list']
    df = tpr.select_sub_data(df, filters=filters_)
    if subset_analysis == 'together':
        print("WARNING: subsets won't be plotted in different colors in maps if plotted together")
        df_list = [df]  # a single df is kept
    elif subset_analysis == 'separately':
        if "subset" in df.columns:
            df_list = [df[df['subset'] == sub] for sub in df['subset'].unique()]  # a list of df filtered by subset
        else: 
            df_list = [df]

    # Make grid
    if image['image_size'] is None:  # get image size using data, making it slighlty larger
        xmax = df['x'].max() + 0.05 * (df['x'].max() - df['x'].min())
        ymax = df['y'].max() + 0.05 * (df['y'].max() - df['y'].min())
        image_size = (xmax, ymax)  # image width,image height in px
    else: 
        image_size = (image['image_size'][1], image['image_size'][0])  # image width,image height in px
    
    grids = tpr.make_grid(image_size,
                          x_num=grid_param['x_num'],
                          y_num=grid_param['y_num'],
                          cell_size=grid_param['cell_size'],
                          scaled=grid_param['scaled'],
                          lengthscale=lengthscale,
                          origin=grid_param['origin'],
                          plot_grid=grid_param['plot_grid'],
                          save_plot_fn=osp.join(map_dir, 'grids{}'.format(plot_config['format'])))

    special_fields = ['div', 'curl', 'v_mean', 'a_mean'] # special scalar fields that need to be calculated and not interpolated 
    # Compute fields
    for i, df in enumerate(df_list):
        # name subset directory
        dir_name = ''
        if subset_analysis == 'separately' and "subset" in df.columns:
            subset_name = df['subset'].values[0]
            dir_name = '_' + subset_name if subset_name != '' else ''
        dir_name_ = '{}{}'.format(len(tpr.listdir_nohidden(map_dir)) + 1, dir_name)

        if quiet < 2:
            print(r"Analyzing subset {}  ".format(i + 1, dir_name_))
        sub_dir = osp.join(map_dir, dir_name_)
        sub_dir = sub_dir + '_1' if osp.exists(sub_dir) else sub_dir  # dont overwrite existing dir
        tpr.safe_mkdir(sub_dir)
        
        # export data
        csv_fn = osp.join(sub_dir, 'all_data.csv')
        df.to_csv(csv_fn)
        config_dir = osp.join(sub_dir, 'config')
        tpr.safe_mkdir(config_dir)
        fn = osp.join(config_dir, 'filters.csv')
        tpr.write_dict(filters_[i], fn)
        for key in map_config.keys():
            fn = osp.join(config_dir, key + '.csv')
            tpr.write_dict(map_config[key], fn)

        # list required fields to interpolate
        all_fields = list(set(list(scalar_fields.keys()) + list(vector_fields.keys()) + list(vector_mean.keys())))
        interp_fields = [f for f in all_fields if f not in special_fields]  # fields to interpolate
        vel_fields = ['v' + d for d in dimensions]
        acc_fields = ['a' + d for d in dimensions]

        # remove not existing scalar fields from all_fields, scalar fields and interp_fields (mostly vz and az fields, if error in data dimension)
        for f in list(interp_fields):  # loop over a copy of interp_fields
            if f not in df.columns: 
                all_fields.remove(f)
                interp_fields.remove(f)
                scalar_fields.pop(f, None)
        
        # add all velocity fields if necessary to other calculation
        if 'div' in all_fields or 'curl' in all_fields or 'v_mean' in all_fields or 'v' in vector_fields.keys():  
            for vf in vel_fields:
                if vf not in interp_fields:
                    interp_fields.append(vf)

        # add all acceleration fields if necessary to other calculation
        if 'a_mean' in all_fields or 'a' in vector_fields.keys():  
            for af in acc_fields:
                if af not in interp_fields:
                    interp_fields.append(af)

        # add plot_on fields to fields to compute
        plot_on_fields = []
        for k in vector_fields.keys():
            plot_on_f = vector_fields[k]['plot_on']
            plot_on_fields.append(plot_on_f)
            if plot_on_f not in interp_fields and plot_on_f not in special_fields:
                interp_fields.append(plot_on_f)

        # compute data
        field_data = tca.interpolate_all_fields(data_dir, df, grids, field_values=interp_fields,
                                                temporal_average=map_param['temporal_average'],
                                                export_field=map_param['export_field'], outdir=sub_dir)
        if 'div' in all_fields or 'curl' in all_fields or 'div' in plot_on_fields or 'curl' in plot_on_fields:
            field_data = tca.compute_all_div_curl(data_dir, df, field_data, lengthscale,
                                                  export_field=map_param['export_field'], outdir=sub_dir)
        for mf in ['v_mean', 'a_mean']:
            if mf in all_fields:
                field_data = tca.compute_all_vector_mean(data_dir, df, field_data, mf,
                                                         dimensions=vector_mean[mf]['dimensions'],
                                                         export_field=map_param['export_field'], outdir=sub_dir)

        # plot data
        if quiet < 2:
            print("Plotting scalar fields...")
        scalar_fields_ = {**scalar_fields, **vector_mean}  # merge scalar data in one single dict
        for field in scalar_fields_.keys():
            if plot_config['save_as_stack']:
                plot_dir = sub_dir
            else: # save series of images in a separate directory 
                plot_dir = osp.join(sub_dir, field)
                tpr.safe_mkdir(plot_dir)
            map_param_ = dict(map_param)
            map_param_['vlim'] = scalar_fields_[field]['vlim'] if 'vlim' in scalar_fields_[field].keys() else None
            map_param_['cmap'] = scalar_fields_[field]['cmap'] if 'cmap' in scalar_fields_[field].keys() else 'plasma'
            tpl.plot_all_scalar_fields(data_dir, df, field_data, field, image=image, map_param=map_param_,
                                       plot_dir=plot_dir, plot_config=plot_config, quiet=quiet, custom_var=custom_var)
        
        if quiet < 2:
            print("Plotting vector fields...")
        for field in vector_fields.keys():
            if plot_config['save_as_stack']:
                plot_dir = sub_dir
            else: # save series of images in a separate directory 
                plot_dir = osp.join(sub_dir, field)
                tpr.safe_mkdir(plot_dir)
            map_param_ = dict(map_param)
            map_param_['vlim'] = vector_fields[field]['vlim']
            tpl.plot_all_vector_fields(data_dir, df, field_data, field, image=image, plot_on_field=vector_fields[field],
                                       dim=3, map_param=map_param_, plot_dir=plot_dir, plot_config=plot_config,
                                       quiet=quiet, custom_var=custom_var)

    return df_list


def parse_args(args=None):
    """
    parse arguments for main()
    """

    parser = argparse.ArgumentParser(description="""
        Run the map analysis module in the data_dir directory
        """)

    parser.add_argument('data_dir',
                        help='path of the data directory')

    parser.add_argument('-r', '--refresh',
                        action="store_true",
                        default=False,
                        help='refresh database')

    parser.add_argument('-p', '--parallelize',
                        action="store_true",
                        default=False,
                        help=argparse.SUPPRESS)

    parser.add_argument('-q', '--quiet',
                        action="count", 
                        default=False,
                        help="""decrease verbosity level. There are 3 levels: 
                        display detailed log (default), display simple log (-q), display only warning and errors (-qq)""")

    parsed_args = parser.parse_args(args)

    return parsed_args


def main(args=None):
    """ main function to run traj_analysis from command line"""

    args = sys.argv[1:] if args is None else args
    parsed_args = parse_args(args)

    data_dir = osp.realpath(parsed_args.data_dir)
    refresh = parsed_args.refresh
    parallelize = parsed_args.parallelize
    quiet = parsed_args.quiet

    if not osp.exists(data_dir):
        raise Exception("ERROR: the passed data directory does not exist. Aborting...")

    if not osp.isdir(data_dir):
        raise Exception("ERROR: the passed data directory is not a directory. Aborting...")

    # Load config
    config = tpr.load_config(data_dir)

    # Check config
    mandatory_config = ["filters", "plot_config", "data_config"]
    for key in mandatory_config:
        if key not in config.keys():
            config[key] = None

    # get map_config
    map_config_default = tpr.make_map_config(data_dir=data_dir, export_config=False)
    map_config = {}
    for key in map_config_default.keys():
        if key in config.keys():
            map_config[key] = config[key]

    # run analysis
    map_analysis(data_dir,
                 refresh=refresh,
                 parallelize=parallelize,
                 quiet=quiet,
                 filters=config["filters"],
                 plot_config=config["plot_config"],
                 map_config=map_config,
                 data_config=config["data_config"])


if __name__ == '__main__':
    main()
