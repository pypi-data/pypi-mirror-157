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


def traj_analysis(data_dir, data=None, image=None, refresh=False, parallelize=False, filters=None, plot_config=None,
                  traj_config=None, data_config=None, quiet=0):
    """Container method to run analysis related to cell trajectories."""

    traj_dir = osp.join(data_dir, 'traj_analysis')
    tpr.safe_mkdir(traj_dir)

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
    dim = data['dim']
    dimensions = data['dimensions']
    custom_var = data['custom_var']
    timescale = data['timescale']

    # Get plot_config
    plot_config = tpl.make_plot_config(data_dir=data_dir, export_config=False) if plot_config is None else plot_config
    # check that all configs are in plot_config, if not load default
    plot_config_default = tpl.make_plot_config(data_dir=data_dir, export_config=False)
    for k in plot_config_default.keys():
        if k not in plot_config.keys():
            plot_config[k] = plot_config_default[k]
    if plot_config['save_as_stack']:
        mpl.use('agg')  # need to switch backend to use matplotlib tostring_rgb()
    
    # Get traj_config
    traj_config_default = tpr.make_traj_config(data_dir=data_dir, export_config=False)
    traj_config = traj_config_default if traj_config is None else traj_config

    # check that all configs are in traj_confign, if not load default
    for key in traj_config_default.keys():
        traj_config_default_ = traj_config_default[key]
        # if doesn't exist, add
        if key not in traj_config.keys():
            traj_config[key] = traj_config_default_
        # check all defaut param are present
        for k in traj_config_default_.keys():
            if k not in traj_config[key].keys():
                traj_config[key][k] = traj_config_default_[k]


    traj_config_ = traj_config["traj_config_"]
    MSD_config = traj_config["MSD_config"]
    scatter_config = traj_config["scatter_config"]
    hist_config = traj_config["hist_config"]
    total_traj_config = traj_config["total_traj_config"]
    voronoi_config = traj_config["voronoi_config"]
    boxplot_config = traj_config["boxplot_config"]

    # Filter data
    filters = tpr.init_filters(data_dir=data_dir, export_config=False) if filters is None else filters
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
        df_list = [df]  # a single df is kept
        # force color coding trajectory plotting
        traj_config_['color_code'] = 'group'
        total_traj_config['color_code'] = 'group'
        # convert z color code to z_scaled (currently assuming the user wants only scaled data)
        traj_config_['color_code'] = 'z_scaled' if traj_config_['color_code']=='z' else traj_config_['color_code']
        total_traj_config['color_code'] = 'z_scaled' if total_traj_config['color_code']=='z' else traj_config_['color_code']
    elif subset_analysis == 'separately':
        if "subset" in df.columns:
            df_list = [df[df['subset'] == sub] for sub in df['subset'].unique()]  # a list of df filtered by subset
        else: 
            df_list = [df]

    # Run analysis
    for i, df in enumerate(df_list):
        # name subset directory
        dir_name = ''
        if subset_analysis == 'separately' and "subset" in df.columns:
            subset_name = df['subset'].values[0]
            dir_name = '_' + subset_name if subset_name != '' else ''
        dir_name_ = '{}{}'.format(len(tpr.listdir_nohidden(traj_dir)) + 1, dir_name)

        if quiet < 2:
            print(r"Analyzing subset #{}, named: {}".format(i + 1, dir_name_))
        sub_dir = osp.join(traj_dir, dir_name_)
        sub_dir = sub_dir + '_1' if osp.exists(sub_dir) else sub_dir  # dont overwrite existing dir
        tpr.safe_mkdir(sub_dir)

        # export data
        csv_fn = osp.join(sub_dir, 'all_data.csv')
        df.to_csv(csv_fn)

        # save pipeline parameters
        config_dir = osp.join(sub_dir, 'config')
        tpr.safe_mkdir(config_dir)
        fn = osp.join(config_dir, 'filters.csv')
        tpr.write_dict(filters_[i], fn)

        # compute mean track properties
        mean_fn = osp.join(sub_dir, 'mean_track_data.csv')
        std_fn = osp.join(sub_dir, 'std_track_data.csv')
        print("Computing means along trajectories...")
        df_mean, df_std = tca.compute_track_prop(df, dimensions,custom_var)
        df_mean.to_csv(mean_fn)
        df_std.to_csv(std_fn)

        # analysis and plotting
        if subset_analysis == 'together':
            if 'subset' in df.columns:
                hue = 'subset'
                hue_order = df['subset'].unique() if filters['subset_order'] is None else filters['subset_order']
                traj_config_['subset_order'] = hue_order
            else:
                hue = None
                hue_order = None
        else:
            hue = None
            hue_order = None

        # plot trajectories
        if traj_config_['run']:
            if quiet < 2:
                print("Plotting trajectories...")
            tpl.plot_all_traj(data_dir, df, image=image, traj_parameters=traj_config_, parallelize=parallelize,
                              dim=dim, plot_dir=sub_dir, plot_config=plot_config, quiet=quiet, custom_var=custom_var)

        if total_traj_config['run']:
            if quiet < 2:
                print("Plotting total trajectories")
            tpl.plot_total_traj(data_dir, df, dim=dim, plot_dir=sub_dir, plot_config=plot_config,
                                specific_config=total_traj_config, custom_var=custom_var)

        # MSD analysis
        if MSD_config['run']:
            if quiet < 2:
                print("MSD analysis...")
            df_mean = tpl.plot_all_MSD(data_dir, df, df_out=df_mean, fit_model=MSD_config['MSD_model'],
                                       MSD_parameters=MSD_config, plot_config=plot_config, plot_dir=sub_dir, hue=hue,
                                       hue_order=hue_order,timescale=timescale)
            df_mean.to_csv(mean_fn)

        # Voronoi analysis
        if voronoi_config['run']:
            if quiet < 2:
                print("Voronoi analysis...")
            vor_data = tca.compute_all_Voronoi(data_dir, df, outdir=sub_dir,compute_local_area=voronoi_config['compute_local_area'],
                                            area_threshold=voronoi_config['area_threshold'], df_mean=df_mean)
            # update csv files with area data
            df_mean.to_csv(mean_fn)
            df.to_csv(csv_fn) 
            
            if voronoi_config['plot']:
                if len(df_list) > 1 and subset_analysis == 'together':
                    print("WARNING: there is no color code to identify subsets in Voronoi diagram plots")
                if plot_config['save_as_stack']:
                    plot_dir = sub_dir
                else: # save series of images in a separate directory 
                    plot_dir = osp.join(sub_dir, 'voronoi')
                    tpr.safe_mkdir(plot_dir)
                tpl.plot_all_Voronoi(data_dir, df, vor_data, show_local_area=voronoi_config['show_local_area'], image=image,
                                     map_param=voronoi_config, plot_dir=plot_dir, plot_config=plot_config, quiet=quiet)

        if hist_config['run']:
            fn = osp.join(config_dir, 'hist_config.csv')
            tpr.write_dict(hist_config, fn)

            if 'var_list' in hist_config.keys():
                if len(hist_config['var_list']) > 0:
                    if quiet < 2:
                        print("Plotting instantaneous parameters histograms...")
                for p in hist_config['var_list']:
                    tpl.plot_param_hist(data_dir, p, df, plot_config=plot_config, plot_dir=sub_dir, hue=hue,
                                        hue_order=hue_order,custom_var=custom_var)

            if 'mean_var_list' in hist_config.keys():
                if len(hist_config['mean_var_list']) > 0:
                    if quiet < 2:
                        print("Plotting whole-track parameters histograms...")
                for p in hist_config['mean_var_list']:
                    tpl.plot_param_hist(data_dir, p, df_mean, plot_config=plot_config, plot_dir=sub_dir, prefix='track_',
                                        hue=hue, hue_order=hue_order,custom_var=custom_var)

        if scatter_config['run']:
            fn = osp.join(config_dir, 'scatter_config.csv')
            tpr.write_dict(scatter_config, fn)

            if 'couple_list' in scatter_config.keys():
                if len(scatter_config['couple_list']) > 0:
                    if quiet < 2:
                        print("Plotting scatter plots of instantaneous parameters...")
                for param_vs_param in scatter_config['couple_list']:
                    x_param, y_param = param_vs_param
                    tpl.plot_param_vs_param(data_dir, x_param, y_param, df, plot_dir=sub_dir, plot_config=plot_config,
                                            hue=hue, hue_order=hue_order, x_bin_num=scatter_config["x_bin_num"], ci=scatter_config["ci"], 
                                            fit_reg=scatter_config["fit_reg"], scatter=scatter_config["scatter"],custom_var=custom_var)

            if 'mean_couple_list' in scatter_config.keys():
                if len(scatter_config['mean_couple_list']) > 0:
                    if quiet < 2:
                        print("Plotting scatter plots of whole-track parameters...")
                for param_vs_param in scatter_config['mean_couple_list']:
                    x_param, y_param = param_vs_param
                    tpl.plot_param_vs_param(data_dir, x_param, y_param, df_mean, plot_dir=sub_dir, plot_config=plot_config,
                                            prefix='track_', hue=hue, hue_order=hue_order, x_bin_num=scatter_config["x_bin_num"], ci=scatter_config["ci"], 
                                            fit_reg=scatter_config["fit_reg"], scatter=scatter_config["scatter"],custom_var=custom_var)

        if boxplot_config['run']:
            fn = osp.join(config_dir, 'boxplot_config.csv')
            tpr.write_dict(boxplot_config, fn)

            if 'var_list' in boxplot_config.keys():
                if len(boxplot_config['var_list']) > 0:
                    if quiet < 2:
                        print("Plotting instantaneous parameters boxplots...")
                for p in boxplot_config['var_list']:
                    tpl.plot_param_boxplot(data_dir, df=df, x_param=hue, param=p, order=hue_order,save_stat=boxplot_config['save_stat'], boxplot=boxplot_config['boxplot'],
                                   swarmplot=boxplot_config['swarmplot'], plot_config=plot_config, plot_dir=sub_dir,custom_var=custom_var)

            if 'mean_var_list' in boxplot_config.keys():
                if len(boxplot_config['mean_var_list']) > 0:
                    if quiet < 2:
                        print("Plotting whole-track boxplots...")
                for p in boxplot_config['mean_var_list']:
                    tpl.plot_param_boxplot(data_dir, df=df_mean, x_param=hue, param=p, order=hue_order, save_stat=boxplot_config['mean_save_stat'], boxplot=boxplot_config['mean_boxplot'],
                                   swarmplot=boxplot_config['mean_swarmplot'], plot_config=plot_config, plot_dir=sub_dir, prefix='track_',custom_var=custom_var)


    return df_list


def parse_args(args=None):
    """
    parse arguments for main()
    """

    parser = argparse.ArgumentParser(description="""
        Run the trajectory analysis module in the data_dir directory
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
            config[key] = None  # make them None, so they are initialize in traj_analysis

    # get traj_config
    traj_config_default = tpr.make_traj_config(data_dir=data_dir, export_config=False)
    traj_config = {}
    for key in traj_config_default.keys():  # load only the necessary config dict
        if key in config.keys():
            traj_config[key] = config[key]

    # run analysis
    traj_analysis(data_dir,
                  refresh=refresh,
                  parallelize=parallelize,
                  quiet=quiet,
                  filters=config["filters"],
                  plot_config=config["plot_config"],
                  traj_config=traj_config,
                  data_config=config["data_config"])


if __name__ == '__main__':
    main()
