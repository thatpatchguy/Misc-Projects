#!/usr/bin/env python
# coding: utf-8

# In[71]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import gmaps
from pprint import pprint
import requests
import json


# In[72]:


from config import gmaps_key
gmaps.configure(api_key=gmaps_key)


# In[73]:


tour_file = pd.read_csv('tour_schedule.csv')
tour_file


# In[74]:


tour_file['State'] = ''
tour_file['Country'] = ''
tour_file['Cast'] = ''
for index, row in tour_file.iterrows():
    splitd = row['City'].split(', ')
    if len(splitd) == 1:
        tour_file.loc[index, 'State'] = '-'
        tour_file.loc[index, 'City'] = splitd[0]
        tour_file.loc[index, 'Country'] = splitd[0]
    elif len(splitd) == 2:
        tour_file.loc[index, 'State'] = '-'
        tour_file.loc[index, 'City'] = splitd[0]
        tour_file.loc[index, 'Country'] = splitd[1]
    elif len(splitd) == 3:
        tour_file.loc[index, 'State'] = splitd[1]
        tour_file.loc[index, 'City'] = splitd[0]
        tour_file.loc[index, 'Country'] = splitd[2]
    splitt = row['Tour'].split(' ')
    if splitt[0] == 'Spring':
        cast = 'A'
    elif splitt[0] == 'Fall':
        cast = 'B'
    tour_file.loc[index, 'Cast'] = cast + splitt[1][-2] + splitt[1][-1] 
tour_file.head()


# In[75]:


tour_file


# In[76]:


tour_file['Country'].value_counts()


# In[77]:


cast = input('What cast did you travel in?')
cast_tour = tour_file.loc[tour_file['Cast'] == cast]


# In[78]:


url = f'https://maps.googleapis.com/maps/api/geocode/json?key={gmaps_key}'
cast_tour['Lat'] = ''
cast_tour['Long'] = ''
for index, row in cast_tour.iterrows():
    if row['State'] != '-':
        append_url = f'&address=' + str(row['City']) + '%20' + str(row['State']) + '%20' + str(row['Country'])
    else:
        append_url = f'&address=' + str(row['City']) + '%20' + str(row['Country'])
    response = requests.get(url+append_url).json()
    cast_tour.loc[index, 'Lat'] = response['results'][0]['geometry']['location']['lat']
    cast_tour.loc[index, 'Long'] = response['results'][0]['geometry']['location']['lng']
    
        
cast_tour


# In[79]:


marker_locations = cast_tour[['Lat', 'Long']]

info_box_template = """
<dl>
<dt>City</dt><dd>{City}</dd>
<dt>State</dt><dd>{State}</dd>
<dt>Country</dt><dd>{Country}</dd>
</dl>
"""
# Store the DataFrame Row
tour_info = [info_box_template.format(**row) for index, row in cast_tour.iterrows()]
fig = gmaps.figure()
markers = gmaps.marker_layer(marker_locations, info_box_content=tour_info)
fig.add_layer(markers)
fig


# In[ ]:




