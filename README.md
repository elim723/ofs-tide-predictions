# ofs-tide-predictions
Research &amp; Development project on OFS tide and tidal current prediction

# Overview

For additional information, contact: Elim Thompson, NOAA Center for Operational Oceanographic Products and Services, elim.thompson@noaa.gov

Other team memebers include Greg Dusek, Armin Pruessner, Jiangtao Xu

# Documentation and code

For progress, please visit Elim's [confluence page](https://confluence.co-ops.nos.noaa.gov/x/ZAXzAQ).

### Background
Tide and tidal current predictions are two of the major products in CO-OPS. Currently, predictions at a specific location are calculated from a set of harmonic constituents determined by Harmonic Analysis (HA). Harmonic constituents are updated regularly at active stations, where water level and current are observed. Because of that, CO-OPS provides tide and tidal current predictions only at specific, discrete locations.
A potential alternative to HA prediction from observed water level or currents is to use the Operational Forecast System (OFS) model. The OFS model simultaneously solves for multiple environmental variables in a continuous body of water. These variables include water temperature, surface elevation, water current, and salinity. Because the OFS model covers a continuous region, the modelled surface elevation and water current potentially provide dramatically greater spatial coverage of predicted tides and tidal currents than presently possible using existing observations. 

### Proposed R&D
This project investigates the potential of using the OFS model to provide tide and tidal current predictions in Chesapeake Bay (CB). We would like to study the hourly time-series from the CBOFS nowcast and forecast outputs. In particular, we are interested in comparing the CBOFS modelled predictions against observations as well as the existing observed HA predictions. By performing an HA on the modelled data and comparing the constituents to those from observed data, we will check the accuracy at which expected tidal frequencies are resolved. At active water level and current stations with years of data, we will extend our study to multi-year comparisons between predictions and observations within the same time windows as well as beyond the observed time periods. We are also interested in investigating any differences seen in the constituent constants between the HA performed on OFS predicted data and that on observations. The resultant differences in time-series predictions will also be studied. 

# NOAA Open Source Disclaimer
This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project code is provided on an ?as is? basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

# License
Software code created by U.S. Government employees is not subject to copyright in the United States (17 U.S.C. �105). The United States/Department of Commerce reserve all rights to seek and obtain copyright protection in countries other than the United States for Software authored in its entirety by the Department of Commerce. To this end, the Department of Commerce hereby grants to Recipient a royalty-free, nonexclusive license to use, copy, and create derivative works of the Software outside of the United States.
