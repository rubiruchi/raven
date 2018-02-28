
# download link for csvs:
# https://catalog.data.gov/dataset/anemometer-data-wind-speed-direction-for-beresford-south-dakota-2006

import datetime as dt
import time as tmod
import numpy as np
import os

def fixData(times,speed,interval,start,end):
  # collect data into interval-sized chunks
  newspeed = {}         # fixed speeds
  newtimes = {}         # fixed times
  # fix each year/period individually
  for year in alltimes.keys():
    print 'Fixing up',year,'...'
    low = 0.0             # lower end of current interval
    high = low + interval # upper end of current interval
    yspeed = np.array(speed[year])
    ytimes = np.array(times[year])
    newspeed[year] = []
    newtimes[year] = []
    # loop through year and collapse intervals
    while high <= end:
      newtimes[year].append(low)
      condition = (low<=ytimes)*(ytimes<high)
      newspeed[year].append(np.average(np.extract(condition,yspeed)))
      low = high
      high += interval
  return newspeed,newtimes

def readData(fname):
  print 'reading',fname,'...'
  # place to store results
  data = {'time':[],'speed':[]}
  # flag for when we start reading data
  start = False
  # keep file open to read from
  with open(fname,'r') as infile:
    # loop over lines in file
    for l,line in enumerate(infile):
      # if line is empty, skip it
      if line.strip() == '':
        continue
      # if we're not started but we find the start, read in headers and trigger a start
      if not start and line.split(',')[0].strip() == 'Year':
        headers = list(h.strip() for h in line.split(','))
        start = True
        firstTime = None
        continue
      # if not started yet, go to the next line
      if not start:
        continue
      # get the time, speed
      line = line.split(',')
      ## get time
      Y,M,D,h,m = list(int(number) for number in line[:-1])
      ## leap year is a pain!
      if M==2 and D==29:
        continue
      ### convert time into datetime object, then to seconds since epoch
      dt_time = dt.datetime(1970,M,D,h,m)
      time = tmod.mktime(dt_time.timetuple())
      if firstTime is None:
        firstTime = time
        time = 0.0
      else:
        time -= firstTime
      ## get speed
      speed = float(line[-1])
      # store results
      data['time'].append(time)
      data['speed'].append(speed)
  return data

def plotData(times,speeds):
  import matplotlib.pyplot as plt
  plt.figure()
  plt.plot(alltimes,allspeed)
  plt.show()

def writeData(times,speeds,outname):
  print 'Writing',outname,'...'
  with open(outname,'w') as outfile:
    # write main file
    outfile.writelines('period,scaling,filename'+os.linesep)
    for k,key in enumerate(allspeed.keys()):
      subfilename = '{}_{}.csv'.format(outname[:-4],str(k+1))
      outfile.writelines('{},{},{}'.format(key,1,subfilename)+os.linesep)
      with open(subfilename,'w') as subfile:
        subfile.writelines('Time,Speed'+os.linesep)
        for i in range(len(times[key])):
          subfile.writelines('{},{}'.format(times[key][i],speeds[key][i])+os.linesep)

# if run from command line
if __name__ == '__main__':
  datasets = ['101645-2007.csv',
              '101645-2008.csv',
              '101645-2009.csv',
              '101645-2010.csv',
              '101645-2011.csv',
              '101645-2012.csv']
  allspeed = {}
  alltimes = {}
  for d in datasets:
    new = readData(d)
    allspeed[d.split('.')[0].split('-')[1]] = new['speed']
    alltimes[d.split('.')[0].split('-')[1]] = new['time']

  start = 0.0 # start time after data is converted
  end = 31535700.0 # end time after data is converted
  interval = 3600 # collapsing interval
  allspeed,alltimes = fixData(alltimes,allspeed,interval,start,end)
  writeData(alltimes,allspeed,'raw_data.csv')



