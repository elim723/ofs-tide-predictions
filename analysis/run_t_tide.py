#!/home/elims/envs/py37/bin/python

## By Elim Thompson 2020/07/03
##
## This python loops through all netcdf file and extract the data needed
## as dataframe and dump out a csv of time series.
#########################################################################

#####################################
## Import packages
#####################################
import pandas, numpy, glob, os

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
#rerunHA = False
#matlab_script = "C:\\Users\\elim.thompson\\Documents\\ofsRD\\ofs-tide-prediction\\analysis\\run_t_tide.m"
#matlab.exe -nodisplay -nosplash -nodesktop -r "run('C:\\Users\\elim.thompson\\Documents\\ofsRD\\ofs-tide-prediction\\analysis\\run_t_tide.m');exit;"

tTidePath = 'C:\\Users\\elim.thompson\\Documents\\ofsRD\\outputs\\t_tide\\'
outPath = 'C:\\Users\\elim.thompson\\Documents\\ofsRD\\outputs\\plots\\'

constiNames = ['M2', 'S2', 'N2', 'K1', 'M4', 'O1']

#####################################
## Define functions
#####################################
extract_station = lambda afile: os.path.basename (afile).split ('.')[0].split ('_')[1][1:]
extract_results = lambda data, col: {'ofs':extract (data['ofs'], col), 'coops':extract (data['coops'], col)}

def gather_stations ():

    coops_stations = numpy.array ([extract_station (afile) for afile in glob.glob (tTidePath + 'coops_*.dat')])
    ofs_stations   = numpy.array ([extract_station (afile) for afile in glob.glob (tTidePath + 'ofs_*.dat')])
    return ofs_stations[numpy.in1d (ofs_stations, coops_stations)]    

def read_dat (station, predType):

    with open (tTidePath + predType + '_x' + station + '.dat') as f:
        content = f.readlines()
    f.close ()

    percent = None
    for index, line in enumerate (content):
        if line.strip().split (' ')[0] == 'percent':
            percent = float ( line.strip().split (' ')[4])

    table_start_index = -1
    for index, line in enumerate (content):
        if line.strip().split (' ')[0] == 'tide':
            table_start_index = index
    if table_start_index == -1:
        print ('Cannot find table of results.')
        return None
    
    content = content[table_start_index:]
    content = numpy.array ([[value for value in line.strip().split (' ') if len (value.strip())>0 ] for line in content]).T
    header = content[:, 0]
    content = content[:, 1:]
    content[0] = [aTide.replace ('*', '') for aTide in content[0]]
    
    adict = {}
    for index, column in enumerate (header):
        values = content[index, :] if index==0 else content[index, :].astype (float)
        adict[column] = values

    return percent, pandas.DataFrame (adict)

def read_dats ():

    stations = gather_stations ()

    percents = {'ofs':{}, 'coops':{}}
    data = {'ofs':{}, 'coops':{}}
    for predType in data.keys ():
        for station in stations:
            percent, df = read_dat (station, predType)
            percents[predType][station] = percent
            if df is None: continue
            data[predType][station] = df

    stations = sorted (percents['ofs'])
    percents_df = {'stations':stations,
                   'ofs':[percents['ofs'][station] for station in stations],
                   'coops':[percents['coops'][station] for station in stations]}
    percents_df = pandas.DataFrame (percents_df)
    percents_df.index = percents_df.stations
    percents_df = percents_df.drop (axis=1, columns=['stations'])

    return percents_df, data

def extract (subdata, col):

    this_df = {station:df[col] for station, df in subdata.items()}
    this_df = pandas.DataFrame (this_df)
    this_df.index = subdata[list (subdata.keys())[0]]['tide']
    return this_df

def plot_percents (percents):

    h = plt.figure (figsize=(7.5, 5))
    gs = gridspec.GridSpec (1, 1)
    gs.update (bottom=0.15)

    axis = h.add_subplot (gs[0])
    xvalues = numpy.arange (len (percents))
    for predType in ['ofs', 'coops']:
        color = 'red' if predType == 'ofs' else 'blue'
        yvalues = percents[predType].values/100
        axis.scatter (xvalues[numpy.isfinite (yvalues)], yvalues[numpy.isfinite (yvalues)],
                      color=color, alpha=0.7, marker='x', label=predType)

    ##  Format x-axis
    axis.set_xlim ([min(xvalues)-1, max(xvalues)+1])
    axis.set_xticks (xvalues)    
    axis.set_xticklabels (percents.index)
    axis.tick_params (axis='x', labelsize=8, labelrotation=30)
    ##  Format y-axis
    axis.set_ylim ([0.0, 1.0])
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel ('predicted / original [%]', fontsize=10)       
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    ##  Plot legend
    axis.legend (loc=3, fontsize=8)

    ### Store plot as PDF
    plt.suptitle ('T-Tide percentage', fontsize=15)
    h.savefig (outPath + 't_tide_percentage.pdf')
    plt.close ('all')
    return

def plot_consti (constiName, df):

    h = plt.figure (figsize=(7.5, 5))
    gs = gridspec.GridSpec (2, 1, wspace=0.1)
    gs.update (bottom=0.15)

    ## Top plot: amplitude
    axis = h.add_subplot (gs[0])
    xvalues = numpy.arange (len (df))
    ylimits = [numpy.Inf, -numpy.Inf]
    for predType in ['ofs', 'coops']:
        color = 'red' if predType == 'ofs' else 'blue'
        yvalues = df[predType + '_amps'].values
        xoffset = 0.1
        if predType=='coops': xoffset *=-1
        axis.errorbar (xvalues + xoffset, yvalues, yerr=df[predType + '_amp_errs'].values, marker='x',
                       markersize=6, color=color, alpha=0.5, linestyle=None, linewidth=0.0,
                       ecolor=color, elinewidth=3, capsize=0, capthick=0, label=predType)
        
        if min (yvalues - df[predType + '_amp_errs'].values) < ylimits[0]: ylimits[0] = min (yvalues - df[predType + '_amp_errs'].values)
        if max (yvalues + df[predType + '_amp_errs'].values) > ylimits[1]: ylimits[1] = max (yvalues + df[predType + '_amp_errs'].values)

    ##  Format x-axis
    axis.set_xlim ([min(xvalues)-1, max(xvalues)+1])
    axis.set_xticks (xvalues)
    axis.get_xaxis ().set_ticklabels ([])
    ##  Format y-axis
    axis.set_ylim ([ylimits[0] - 0.01, ylimits[1] + 0.01])
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel (constiName + ' Amp', fontsize=10)       
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    ##  Plot legend
    axis.legend (loc=0, fontsize=8)        

    ## Top plot: phase
    axis = h.add_subplot (gs[1])
    for predType in ['ofs', 'coops']:
        color = 'red' if predType == 'ofs' else 'blue'
        yvalues = df[predType + '_phases'].values
        xoffset = 0.1
        if predType=='coops': xoffset *=-1
        axis.errorbar (xvalues + xoffset, yvalues, yerr=df[predType + '_phase_errs'].values, marker='x',
                       markersize=6, color=color, alpha=0.5, linestyle=None, linewidth=0.0,
                       ecolor=color, elinewidth=3, capsize=0, capthick=0, label=predType)

    ##  Format x-axis
    axis.set_xlim ([min(xvalues)-1, max(xvalues)+1])
    axis.set_xticks (xvalues)    
    axis.set_xticklabels (percents.index)
    axis.tick_params (axis='x', labelsize=8, labelrotation=30)
    ##  Format y-axis
    axis.set_ylim ([0, 360])
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel (constiName + ' Phase', fontsize=10)       
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)

    ### Store plot as PDF
    plt.suptitle ('T-Tide ' + constiName, fontsize=15)
    h.savefig (outPath + 't_tide_' + constiName + '.pdf')
    plt.close ('all')
    return

#####################################
## Script starts here!
#####################################
if __name__ == '__main__':

    ## Step 1. Load T-Tide outputs
    percents, data = read_dats ()

    ## Step 2. Extract the amp / phases
    amps = extract_results (data, 'amp')
    amp_errs = extract_results (data, 'amp_err')
    phases = extract_results (data, 'pha')
    phase_errs = extract_results (data, 'pha_err')

    ## Step 3. Plots
    plot_percents (percents)
    for constiName in constiNames:
        adict = {'ofs_amps'  : amps['ofs'].loc[constiName,:], 
                 'ofs_amp_errs': amp_errs['ofs'].loc[constiName,:],
                 'coops_amps': amps['coops'].loc[constiName,:], 
                 'coops_amp_errs': amp_errs['coops'].loc[constiName,:],
                 'ofs_phases'  : phases['ofs'].loc[constiName,:],
                 'ofs_phase_errs': phase_errs['ofs'].loc[constiName,:],
                 'coops_phases': phases['coops'].loc[constiName,:],
                 'coops_phase_errs': phase_errs['coops'].loc[constiName,:]}
        plot_consti (constiName, pandas.DataFrame (adict))
