# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 20:55:11 2019 Python 3.5
Reads Excel file with AQM data and converts ppb into ug/m3
Also creates rows to groupby dates
@author: Brian
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import calendar
import os
import time

def MW_gmole(MW_name):
    MWg =	{
      "NO": 30.01,
      "NO2": 46.0055,
      "NOx": 1964,
      "SO2": 64.066,
      "H2S": 34.1,
      "O3": 48,
      "CH4": 16.04,
      "CO": 28.01
    }
    return MWg[MW_name]

def ppb2ugm3(Cppb,P, T, MW_name):
    
    R = 8.3144 ### ideal gas constant in m3-kPa/K-mol
    
    MW = MW_gmole(MW_name)  ## get MW from MW_gmole function

    Cug = round((Cppb*MW*P*0.01)/(R*T),2) ## convert to ug/m3
    
    return Cug

########################Start program execution
start = time.time()

#sheets = ['2013','2014','2015', '2016', '2017']
sheets = ['2013','2014','2015', '2016']

Site_all = pd.DataFrame()

for i in range(len(sheets)):
    
    print('Loading Year ' + sheets[i] + ' ....')
    ##### read data file and choose chemical of interest
    Site = pd.read_excel('FS_AQMS.xlsx', sheet_name= sheets[i])
    
    #### break out time and data from time/date
    Site['date'] = pd.to_datetime(Site['Time']).dt.strftime('%D')
    Site['day'] = pd.to_datetime(Site['Time']).dt.strftime('%d')
    Site['month'] = pd.to_datetime(Site['Time']).dt.strftime('%m')
    Site['year'] = pd.to_datetime(Site['Time']).dt.strftime('%Y')
    
    #Site['day_of_week_n'] = Site['Time'].apply(lambda x: x.weekday()) # get the weekday index, between 0 and 6
    #Site['day_of_week'] = Site['day_of_week_n'].apply(lambda x: calendar.day_name[x])  ## weekday name
    Site['hour'] = pd.to_datetime(Site['Time']).dt.strftime('%H')
    
    chemical = ['NO', 'NO2', 'SO2', 'O3', 'H2S', 'CH4', 'CO']
    
    ## create new columns with chemical names that can be converted into ug/m3
    for i in range(len(chemical)):
        
        chem_name = chemical[i]
    
        Site[chem_name+'-ugm3'] = ppb2ugm3(Site[chem_name + '-ppb'], Site['BP-hpa'], Site['Temp-degC'], chem_name)
    
    ### add modified columns
    Site['CO-mgm3'] = Site['CO-ugm3'] / 1000
    Site['CH4-mgm3'] = Site['CH4-ugm3'] / 1000
    Site['H2S-mgm3'] = Site['H2S-ugm3'] / 1000
    
    Site['BP-kpa'] = Site['BP-hpa'] * 0.1
    
    Site['8hrO3'] = Site['O3-ugm3'].rolling(window=8).mean()
    Site['8hrCO'] = Site['CO-ugm3'].rolling(window=8).mean()
    Site['24hrPM10'] = Site['PM10-ug/m3'].rolling(window=24).mean()
    Site['24hrNO2'] = Site['NO2-ugm3'].rolling(window=24).mean()
    Site['24hrSO2'] = Site['SO2-ugm3'].rolling(window=24).mean()
    
    Site_all = Site_all.append(Site)  ## collect each year

### reset index
Site_all = Site_all.reset_index(drop=True)

######################################################
#### make revised dataframe with sequence for AQMIS - no ppb only fields like NMHC
Site_new = Site_all[['date', 
                    'hour', 
                    'NO-ugm3',  
                    'O3-ugm3',
                    'SO2-ugm3',
                    'NO2-ugm3', 
                    'CH4-mgm3',
                    'H2S-mgm3',  
                    'CO-mgm3', 
                    'PM10-ug/m3', 
                    'WS-m/s', 
                    'WD', 
                    'Temp-degC', 
                    'RH-percent', 
                    'BP-kpa', 
                    'SW-w/m2',
                    '8hrO3']].copy()

Site_new = Site_new.replace(np.inf, np.nan)

end = time.time()

duration = round(end - start,2) # total time in seconds

print('Loaded and processed in ' + str(duration) + ' seconds.\n')

#############################################
### write results to spreadsheet in Excel
try:
    save_files = input('Save output files (Default = n)? (y/n) ')
except:
    save_files = 'n' 

if save_files == 'y':
    #################################################
    ### write raw data results to spreadsheet in Excel
    file_saved = 0
    while file_saved == 0:
        try:
            filename_out = 'AMS-rawdata-out'
            writer = pd.ExcelWriter(filename_out + '.xlsx')
            Site_all.to_excel(writer,'FS')
            writer.save()
            file_saved = 1
            print('File ' + filename_out + '.xlsx saved')
            
        except:
            print('File ' + filename_out + '.xls is open. Close it and try again.')

    
    file_saved = 0
    while file_saved == 0:
        try:
            filename_out = 'AMS-AQMISdata-out'
            writer = pd.ExcelWriter(filename_out + '.xlsx')
            Site_new.to_excel(writer,'FS')
            writer.save()
            file_saved = 1
            print('File ' + filename_out + '.xlsx saved')
            
        except:
            print('File ' + filename_out + '.xls is open. Close it and try again.')

########################################################
##### 
a = list(Site_new) ## make list of column headers
last_col = np.shape(Site_new)[1] - 1
     
finish_plot = 0
while finish_plot == 0:
    for i in range (len(a)):
        print (i, a[i])
        
    # pick column to predict
    try:
        target_col = int(input("Select the column number to plot (default = " + a[last_col] + "): "))
    except ValueError:
        target_col = last_col   #choose last column as default
    
    
    print('You selected ' + a[target_col])
    
    try:
        Exceedance = float(input('What is the regulatory limit for this chemical in ug/m3? (Default = 0 ug/m3): '))
    except ValueError:
        Exceedance = 0. 

    try:
        time_ave = int(input('What is the regulatory time average period? (Default = 1 hr): '))
    except ValueError:
        time_ave = 1
        
    Site_new['plot_chem'] = Site_new[a[target_col]].rolling(window=time_ave).mean()
    
    sum_exceed = sum((Site_new['plot_chem']>Exceedance) + 0.)
    missing = Site_new[a[target_col]].isna().sum()
    tot_hrs = len(Site_new)
    
    print('Total hours in reporting period = ', tot_hrs)
    print('Missing data pts = ', missing, '('+str(round((missing/tot_hrs)*100,1))+'%)')
    print('# of exceedances in reporting period = ', int(sum_exceed))
        
    ################### Begin plotting
      
    plt.figure()
    plt.plot(Site_new['plot_chem'])
    #plt.yscale('log')
    plt.axhline(y= Exceedance, color='r', linestyle='-')  ### add reg limit at 3 mg/l
    plt.xticks(rotation='vertical')
    plt.ylabel('$\mu g/m^{3}$')
    plt.grid(axis='y', alpha=0.75)
    #plt.title(Chemical + ' daily sample (linear scale)')
    plt.show()
    
    ################################################
    ### Finish up
    try:
        last_time = input("Finished (y/n)? (default = y): ")
    except ValueError:
        last_time = 'y'   #choose last column as default    
        
    if last_time == 'y':
        finish_plot = 1

        
    