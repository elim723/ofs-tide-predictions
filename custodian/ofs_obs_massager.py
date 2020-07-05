#!/home/elims/envs/py37/bin/python

## By Elim Thompson 2020/07/03
##
## This python takes in a massaged OFS dataframe and combine them with
## the stations in CB and their predictions from obs-HA data.
#########################################################################

#####################################
## Import packages
#####################################
import numpy, pandas, requests
from datetime import datetime

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
outpath = '/home/elims/projects/cbofs/outputs/'
ofsAllFile = outpath + 'ofs_all_heights.csv'
ofsFile = outpath + 'ofs_preds.csv'
coopsFile = outpath + 'coops_preds.csv'

stations = {'8575512':'Annapolis', '8571892':'Cambridge', '8577330':'Solomons Island',
            '8574680':'Baltimore', '8573927':'Chesapeake City', '8635750':'Lewisetta',
            '8573364':'Tolchester Beach', '8571421':'Bishops Head', 
            '8636580':'Windmill Point', '8637689':'Yorktown', '8632200':'Kiptopeke Beach',
            '8638610':'Sewells Point'}

dataAPI_params = {'product':'predictions', 'datum':'MLLW', 'time_zone':'gmt', 'units':'metric'}
metadataAPI_params = {'units':dataAPI_params['units']}

dataAPI_template = 'https://tidesandcurrents.noaa.gov/api/datagetter?' + \
                   'begin_date={begin_date}&end_date={end_date}&station={station}&' + \
                   'product={product}&datum={datum}&time_zone={time_zone}&units={units}&format=json'

metadataAPI_template = 'https://tidesandcurrents.noaa.gov/mdapi/v1.0/webapi/stations/' + \
                       '{station}.json?units={units}'

earth_radius = 6373. # km

#####################################
## Define functions
#####################################
def pull_data (api):

    response = requests.get (api)
    if not response.status_code == 200:
        print ('Connection failed with {0}.'.format (response.status_code))
        return None
    
    content = response.json()
    if 'error' in content:
        print ('Error encountered: {0}.'.format (content['error']['message']))
        return None
    if len (content) == 0:
        print ('Empty content encounted. Please check API:\n{0}.'.format (api))
        return None

    try:
        return content
    except:
        print ('Failed to collect data. Please check API:\n{0}.'.format (api))
    return None    

def pull_heights (**params):

    params = {**params, **dataAPI_params}
    api = dataAPI_template.format (**params)

    content = pull_data (api)
    if content is None: return None

    data = numpy.array ([[aTime['t'], aTime['v']] for aTime in content['predictions']]).T
    dataframe = pandas.DataFrame ({'datetime':data[0], 'predicted':data[1].astype (float)})
    dataframe.index = pandas.to_datetime (dataframe.datetime)
    dataframe = dataframe.drop (axis=1, columns=['datetime'])
    dataframe.columns = [params['station']]
    return dataframe

def pull_coops_pred (metadata, begin_date, end_date):

    params = {'begin_date':begin_date, 'end_date':end_date}
    coopsdata = None
    for row in metadata.itertuples ():
        params['station'] = row.id
        pred = pull_heights (**params)

        if coopsdata is None:
            coopsdata = pred
            continue

        coopsdata = coopsdata.merge (pred,left_index=True, right_index=True)

    return coopsdata

def pull_stations ():

    from_api = {'id':[], 'name':[], 'lat':[], 'lon':[]}

    for sid, name in stations.items():

        params = {**{'station':sid}, **dataAPI_params}
        api = metadataAPI_template.format (**params)

        content = pull_data (api)
        if content is None: return None
        metadata = content['stations'][0]

        from_api['lat'].append (metadata['lat'])
        from_api['lon'].append (metadata['lng'])
        from_api['name'].append (name)
        from_api['id'].append (sid)
    
    return pandas.DataFrame (from_api)

def get_distance (pos1, pos2):

    lat1 = numpy.radians(pos1[0])
    lon1 = numpy.radians(pos1[1])
    lat2 = numpy.radians(pos2[0])
    lon2 = numpy.radians(pos2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = numpy.sin(dlat / 2)**2 + numpy.cos(lat1) * numpy.cos(lat2) * numpy.sin(dlon / 2)**2
    c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))

    return earth_radius * c # km

def match_stations_by_ofs_indices (metadata, ofsdata):

    ofslats, ofslons = numpy.array ([column.split ('_') for column in ofsdata.columns]).T
    ofslats = ofslats.astype (float)
    ofslons = ofslons.astype (float)

    distance, index = [], []
    for ith, station in metadata.iterrows():
        pos1 = (station.lat, station.lon)

        ncdistances = []
        for lat, lon in zip (ofslats, ofslons):
            pos2 = (lat, lon)
            ncdistances.append (get_distance (pos1, pos2))

        distance.append (numpy.min (ncdistances))
        index.append (numpy.argmin (ncdistances))
    
    metadata['nearest_dist'] = distance
    metadata['nearest_ofsIndex'] = index
    return metadata

def plot_a_prediction (station, distance, data):

    h = plt.figure (figsize=(20, 5))
    gs = gridspec.GridSpec (2, 1, height_ratios=[3,1])
    gs.update (bottom=0.15)

    ## top: water level
    axis = h.add_subplot (gs[0])
    xvalues = numpy.arange (len (data['ofs']))
    ylimit = [numpy.inf, -numpy.inf]
    for key in ['coops', 'ofs']:
        yvalues = data[key].values
        color   = 'blue' if key == 'coops' else 'red'
        label   = 'CO-OPS pred' if key == 'coops' else 'OFS pred'
        axis.plot (xvalues[numpy.isfinite (yvalues)], yvalues[numpy.isfinite (yvalues)],
                    color=color, alpha=0.6, linewidth=0.5, linestyle='-', label=label)
        if min (yvalues) < ylimit[0]: ylimit[0] = min (yvalues) - 0.5
        if max (yvalues) > ylimit[1]: ylimit[1] = max (yvalues) + 0.5
    ##  Add legend to plot
    axis.legend (loc=2, prop={'size':10})
    ##  Format x-axis
    axis.set_xlim ([min(xvalues), max(xvalues)])
    is_xticks = xvalues % 876 == 0
    axis.set_xticks (xvalues[is_xticks])    
    axis.get_xaxis ().set_ticklabels ([])
    ##  Format y-axis
    axis.set_ylim (ylimit)
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel ('water level (m) MLLW', fontsize=10)
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)

    ## bottom: difference
    axis = h.add_subplot (gs[1])
    yvalues = data['ofs'] - data['coops']
    axis.plot (xvalues[numpy.isfinite (yvalues)], yvalues[numpy.isfinite (yvalues)],
                color='gray', alpha=0.7, linewidth=0.5, linestyle='-')
    ##  Format x-axis
    axis.set_xlim ([min(xvalues), max(xvalues)])
    axis.set_xticks (xvalues[is_xticks])
    times = numpy.array (list (data.index))
    xticklabels = [datetime.strftime (atime, '%Y-%m-%d\n%H:%M')
                   for atime in times[is_xticks]]
    axis.set_xticklabels (xticklabels)
    axis.tick_params (axis='x', labelsize=8, labelrotation=30)     
    ##  Format y-axis
    axis.set_ylim (min (yvalues)-0.25, max (yvalues)+0.25)
    axis.tick_params (axis='y', labelsize=8)
    axis.set_ylabel ('ofs - coops (m)', fontsize=10)
    ##  Plot grid lines
    for ytick in axis.yaxis.get_majorticklocs():
        axis.axhline (y=ytick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)
    for xtick in axis.xaxis.get_majorticklocs():
        axis.axvline (x=xtick, color='gray', alpha=0.3, linestyle=':', linewidth=0.2)    

    ### Store plot as PDF
    plt.suptitle ('Pred at {0} ({1:.3f} km)'.format (station, distance), fontsize=15)
    h.savefig (outpath + '/CB_stations/predictions_' + station + '.pdf')
    plt.close ('all')
    return

def plot_predictions (metadata, ofsdata, coopsdata):

    for row in metadata.itertuples ():
        ofs = ofsdata[row.id].to_frame()
        ofs.columns = ['ofs']
        coops = coopsdata[row.id].to_frame()
        coops.columns = ['coops']
        data = ofs.merge (coops, right_index=True, left_index=True)
        plot_a_prediction (row.id, row.nearest_dist, data)

#####################################
## Script starts here!
#####################################

if __name__ == '__main__':

    ## Read OFS dataframe
    ofsdata = pandas.read_csv (ofsAllFile)
    ofsdata.index = pandas.to_datetime (ofsdata['datetime'])
    ofsdata = ofsdata.drop (axis=1, columns=['datetime'])

    ## Obtain and massage data from physical stations
    metadata = pull_stations ()
    metadata = match_stations_by_ofs_indices (metadata, ofsdata)

    ## Clean up data from OFS based on the physical stations
    ofsdata = ofsdata.iloc[:, metadata.nearest_ofsIndex.values]
    ofsdata.columns = metadata.id.values

    ## Obtain co-ops predctions from obs-based HA
    begin_date = ofsdata.index[0].strftime ('%Y%m%d %H:%M')
    end_date = ofsdata.index[-1].strftime ('%Y%m%d %H:%M')
    coopsdata = pull_coops_pred (metadata, begin_date, end_date)

    ## Generate plots at all stations
    plot_predictions (metadata, ofsdata, coopsdata)

    ## Dump out the massaged CSV files for T-tide
    ofsdata.to_csv (ofsFile)
    coopsdata.to_csv (coopsFile)

    