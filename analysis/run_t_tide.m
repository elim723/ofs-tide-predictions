% +-------------------------------------------
% | Define constants
% +-------------------------------------------
ofsFile = 'C:\Users\elim.thompson\Documents\ofsRD\outputs\ofs_preds.csv';
coopsFile = 'C:\Users\elim.thompson\Documents\ofsRD\outputs\coops_preds.csv';
outPath = 'C:\Users\elim.thompson\Documents\ofsRD\outputs\t_tide\';

cd 'C:\Users\elim.thompson\Documents\ofsRD\t-tide';

% +-------------------------------------------
% | Run t-tide on OFS predictions
% +-------------------------------------------
predType = 'ofs';

pred = readtable (ofsFile, 'ReadVariableNames', true);
start = pred.datetime(1);
start_time = [start.Year, start.Month, start.Day, start.Hour, start.Minute, start.Second];
interval = hours (pred.datetime(2) - start);

for var = pred.Properties.VariableNames
    if strcmp (var, 'datetime'); continue; end
    output = strcat (outPath, predType, '_', var{1}, '.dat');
    [NAME,FREQ,TIDECON,XOUT] = t_tide (table2array (pred(:,var)), 'interval', interval, 'start time', start_time, 'output', output);
end
    
% +-------------------------------------------
% | Run t-tide on OFS predictions
% +-------------------------------------------
predType = 'coops';

pred = readtable (coopsFile, 'ReadVariableNames', true);
start = pred.datetime(1);
start_time = [start.Year, start.Month, start.Day, start.Hour, start.Minute, start.Second];
interval = hours (pred.datetime(2) - start);

for var = pred.Properties.VariableNames
    if strcmp (var, 'datetime'); continue; end
    thisFile = strcat (predType, strcat ('_'));
    output = strcat (outPath, predType, '_', var{1}, '.dat');
    [NAME,FREQ,TIDECON,XOUT] = t_tide (table2array (pred(:,var)), 'interval', interval, 'start time', start_time, 'output', output);
end

