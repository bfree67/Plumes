# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 20:55:11 2019

@author: Brian
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import os

os.chdir('c:\\TARS\\CIMS_EQuIS\\KNPC')

##### read data file and choose chemical of interest
Site = pd.read_excel('MAB-all.xls')

Site_count = Site.groupby(['chemical_name']).count()['result_numeric'].reset_index()

chem_correct = 'n'
while chem_correct == 'n':
    ### count the number of samples for each chemical
    print(Site_count)
    x_chem = input('Select the number of the chemical you want to graph : ')
   
    #### chemicals and variables 
    Chemical = Site_count['chemical_name'].values[int(x_chem)]
    chem_correct = input('You selected ' + Chemical +'. Is this correct? (y/n) ')   

Chem_X = Site[Site.chemical_name== Chemical]

try:
    Exceedance = input('What is the limit for this chemical in mg/l? (Default = 0 mg/l): ')
except ValueError:
    Exceedance = 0 

Exceedance = int(Exceedance)

### sort and add date groups
Chem_X = Chem_X.sort_values('sample_date', ascending=True)
## add month and year column
Chem_X['month'] = pd.to_datetime(Chem_X['sample_date']).dt.strftime('%m')
Chem_X['year'] = pd.to_datetime(Chem_X['sample_date']).dt.strftime('%Y')
Chem_X['day_of_week_n'] = Chem_X['sample_date'].apply(lambda x: x.weekday()) # get the weekday index, between 0 and 6
Chem_X['day_of_week'] = Chem_X['day_of_week_n'].apply(lambda x: calendar.day_name[x])


################### Begin plotting
plt.figure()
plt.plot(Chem_X['sample_date'], Chem_X['result_numeric'])
#plt.yscale('log')
plt.axhline(y= Exceedance, color='r', linestyle='-')  ### add reg limit at 3 mg/l
plt.xticks(rotation='vertical')
plt.ylabel('mg/l')
plt.grid(axis='y', alpha=0.75)
plt.title(Chemical + ' daily sample (linear scale)')
plt.show()

plt.figure()
plt.plot(Chem_X['sample_date'], Chem_X['result_numeric'])
plt.yscale('log')
plt.axhline(y= Exceedance, color='r', linestyle='-')  ### add reg limit at 3 mg/l
plt.xticks(rotation='vertical')
plt.ylabel('mg/l')
plt.grid(axis='y', alpha=0.75)
plt.title(Chemical + ' daily sample (log scale)')
plt.show()

### hist of all values
plt.figure()
plt.hist(Chem_X.result_numeric, bins= 40, color='#0504aa',
                               alpha=0.7, rwidth=0.85)
plt.yscale('log')
plt.xlabel('mg/l')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.title(Chemical + ' historgram (all samples)')
plt.show()

##### Plot monthly averages
monthly = Chem_X.groupby(['year', 'month'], )['result_numeric']
df2 = monthly.mean()
plt.figure()
df2.plot(kind='bar', color = 'blue')
#plt.yscale('log')
plt.axhline(y= Exceedance, color='r', linestyle='-')  ### add reg limit line
plt.xticks(rotation='vertical')
plt.xlabel('Year - Month')
plt.ylabel('mg/l')
plt.title(Chemical + ' monthly average')
plt.grid(axis='y', alpha=0.75)
plt.show()

#### show exceedances 
Chem_X_X = Chem_X[Chem_X.result_numeric > Exceedance]

plt.figure()
plt.hist(Chem_X_X.result_numeric, bins= 40, color='#0504aa',
                               alpha=0.7, rwidth=0.85)
plt.xlabel('mg/l')
plt.ylabel('Frequency')
plt.title(Chemical + ' historgram (exceedances)')
plt.grid(axis='y', alpha=0.75)
plt.show()

plt.figure()
df = Chem_X_X.groupby(['year']).count()['result_numeric']
df.plot(kind = 'bar', rot = False, color = 'blue')
plt.ylabel('# of exceedances')
plt.title(Chemical + ' exceedances by year')           
plt.show()

plt.figure()
df = Chem_X_X.groupby(['month']).count()['result_numeric']
df.plot(kind = 'bar', rot = False, color = 'blue')
plt.ylabel('# of exceedances')
plt.title(Chemical + ' exceedances by month') 
plt.show()

plt.figure()

df = Chem_X_X.groupby(['day_of_week']).count()['result_numeric'].reset_index()
df['cat_day'] = [5,1,6,0,4,2,3]
df=df.sort_values(by=['cat_day']).reset_index(drop = True)
df.plot(x = 'day_of_week', y = 'result_numeric', kind = 'bar', 
        color = 'blue', legend = False)
plt.ylabel('# of exceedances')
plt.xlabel('Day of week')
plt.title(Chemical + ' exceedances by day of week') 
plt.show()

print('\nThere were a total of ' + str(Chem_X_X['result_numeric'].count()) + ' exceedances in the report.')