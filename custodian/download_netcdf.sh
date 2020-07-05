#!/bin/bash

## By Elim Thompson 2020/06/06
##
## This bash script downloads the 1-year CBOFS forecast outputs from
## NOS FTP sites.
#########################################################################

## +---------------------------------------------
## | Read argument
## +---------------------------------------------
FILETYPE=$1
YEAR=$2
DATAPATH=$3

## +---------------------------------------------
## | Define constants
## +---------------------------------------------
REGION='cbofs'
FTP="ftp://tidepool.nos.noaa.gov/pub/outgoing/ofs/${REGION}/netcdf/"

echo "+-----------------------------------------------------"
echo "| Download latest ${REGION} outputs from ..."
echo "|   ${FTP}"
echo "| Date time now at `date` "
echo "| "
echo "| Your inputs ..."
echo "|   File type (stations or fields)? ${FILETYPE}"
echo "|   Year: ${YEAR}"
echo "|   File path: ${DATAPATH}"
echo "|"

## +------------------------------------------------
## | Figure out the available months for this year
## +------------------------------------------------
echo "| Check index.html to look for months in ${YEAR}"
#  Download index.html from FTP 
wget --quiet -O index.html ${FTP}
if [ -f "index.html" ]; then
    echo "|    - index.html succssfully downloaded"
else
    echo "|    - index.html download failed"
    echo "| Please check the FTP to make sure it is working."
    echo "+-----------------------------------------------------"
    exit
fi 

#  Declare an array holder to store the available month
YYYYMMs=()
#  Loop through each line and look for YYYYMM in the requested year 
echo "|    - look for YYYYMM of requested year from index.html"
while IFS= read -r line; do
    # Extract the /YYYYMM/ pattern
    subtext=`echo ${line} | grep -Eo '/[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+[0-9]+/';`
    # Next line if no pattern found
    if [ -z ${subtext} ]; then continue; fi
    # If the year in /YYYYMM/ matches the requested year, store this!
    if [ "${subtext:1:4}" == "${YEAR}" ]; then
        yyyymm="${subtext:1:6}"
        YYYYMMs+=( ${yyyymm} )
    fi
done < "index.html"

#  Let user know how many months.
nYYYYMMs=${#YYYYMMs[@]}
if [ ${nYYYYMMs} -eq 0 ]; then
    echo "|    - 0 month is available for ${YEAR} in FTP"
    echo "| Make sure there is data for the requested year."
    echo "+-----------------------------------------------------"    
    exit
else
    echo "|    - ${nYYYYMMs} months are available for ${YEAR} in FTP"
    echo "|"
fi 

#  Remove the index.html that was downloaded
rm index.html

## +------------------------------------------------
## | Loop through each month and download files
## +------------------------------------------------
echo "| Download each month into separate folder"

for YYYYMM in ${YYYYMMs[@]}; do

    echo "|    - ${YYYYMM} ..."

    NETCDF_FILEURL=${FTP}/${YYYYMM}
    SUBDATAPATH=${DATAPATH}/${YYYYMM}

    if [ ! -d ${SUBDATAPATH} ]; then 
        mkdir -p ${SUBDATAPATH}
    fi

    PATTERN="nos.${REGION}.${FILETYPE}.forecast.${YYYYMM}??.t??z.nc"
    wget --quiet -r -nH --cut-dirs=7 "${NETCDF_FILEURL}" -P ${SUBDATAPATH} -A ${PATTERN}
done

echo "| "
echo "| Download completed :)"
echo "+-----------------------------------------------------"