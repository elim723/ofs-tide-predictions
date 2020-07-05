#!/home/elims/envs/py37/bin/python

## By Elim Thompson 2020/07/03
##
## This python loops through all netcdf file and extract the data needed
## as dataframe and dump out a csv of time series.
#########################################################################

#####################################
## Import packages
#####################################
import numpy, pandas, xarray, glob
from datetime import datetime
from natsort import natsorted

import matplotlib
matplotlib.use ('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
plt.rc ('text', usetex=False)
plt.rc ('font', family='sans-serif')
plt.rc ('font', serif='Computer Modern Roman')

#####################################
## Define constants
#####################################
datapath = '/home/elims/projects/cbofs/data/'
outpath = '/home/elims/projects/cbofs/outputs/'

ofs_start_date = pandas.to_datetime ("2016-01-01 00:00:00")
n_minutes_per_day = 24 * 60

#####################################
## Define functions
#####################################
def read_one_file (afile):

    one_data = xarray.open_dataset (afile, decode_times=False)
    
    # Get lat / lon of the stations
    lats = one_data.variables['lat_rho'].data
    lons = one_data.variables['lon_rho'].data
    
    # collect water level - only 6 hours i.e. 10 * 6
    heights = one_data.variables['zeta'].data[:60, :].T # meters; MLLW

    # collect time
    start_min = one_data.variables['dstart'].data * n_minutes_per_day
    start_day = ofs_start_date + pandas.offsets.Minute (start_min) 
    times = [start_day + index * pandas.offsets.Minute (6) for index in range (heights.shape[1])]

    # Close file before leaving
    one_data.close ()

    # Convert data into a dataframe
    adict = {'datetime': times}
    for index, (lat, lon) in enumerate (zip (lats, lons)):
        column = str (lat) + '_' + str (lon)
        adict[column] = heights[index]

    dataframe = pandas.DataFrame (adict)
    dataframe.index = pandas.to_datetime (dataframe.datetime)
    dataframe = dataframe.drop (axis=1, columns=['datetime'])

    return dataframe

def collect_ofs_data ():

    allSubPaths = natsorted (glob.glob (datapath + '*/'))

    # Collect all data
    dataframe = None
    for subpath in allSubPaths:
        allfiles = natsorted (glob.glob (subpath + '*.nc'))
        for afile in allfiles:
            subdf = read_one_file (afile)
            if dataframe is None:
                dataframe = subdf
                continue
            dataframe = dataframe.append (subdf)
    
    # Drop out any station that have NaN values. 
    dataframe = dataframe.dropna (axis=1, how='any')
    print ('{0} stations with full time-series'.format (len (dataframe.columns)))
    return dataframe

def plot_one_file (data):

    h = plt.figure (figsize=(15, 5))
    gs = gridspec.GridSpec (1, 1)
    gs.update (bottom=0.15)

    axis = h.add_subplot (gs[0])
    xvalues = numpy.arange (len (data))
    yvalues = data.values
    axis.plot (xvalues[numpy.isfinite (yvalues)], yvalues[numpy.isfinite (yvalues)],
                color='blue', alpha=0.7, linewidth=0.5, linestyle='-')

    ##  Format x-axis
    axis.set_xlim ([min(xvalues), max(xvalues)])
    is_xticks = xvalues % 8760 == 0
    axis.set_xticks (xvalues[is_xticks])    
    axis.get_xaxis ().set_ticklabels ([])
    times = numpy.array (list (data.index))
    xticklabels = [datetime.strftime (atime, '%Y-%m-%d\n%H:%M')
                   for atime in times[is_xticks]]
    axis.set_xticklabels (xticklabels)
    axis.tick_params (axis='x', labelsize=8, labelrotation=30)
    ##  Format y-axis
    axis.set_ylim ([min(yvalues)-0.5, max(yvalues) + 0.5])
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel ('MLLW Height [meters]', fontsize=10)       
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)

    ### Store plot as PDF
    lat, lon = data.name.split ('_')
    lat, lon = '{0:.4f}'.format (float (lat)), '{0:.4f}'.format (float (lon))
    plt.suptitle ('OFS Height at (lat, lon) = ({0}, {1})'.format (lat, lon), fontsize=15)
    h.savefig (outpath + 'ofs_stations/ofs_height_' + lat + '_' + lon + '.pdf')
    plt.close ('all')
    return

def plot_heights (dataframe):

    for column in dataframe.columns:
        plot_one_file (dataframe[column])

#####################################
## Script starts here!
#####################################

if __name__ == '__main__':

    dataframe = collect_ofs_data ()
    plot_heights (dataframe)

    dataframe.to_csv (outpath + 'ofs_all_heights.csv')