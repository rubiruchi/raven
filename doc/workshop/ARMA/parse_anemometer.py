
# download link for csvs:
# https://catalog.data.gov/dataset/anemometer-data-wind-speed-direction-for-beresford-south-dakota-2006

import datetime as dt
import time as tmod
import os

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
      if not start and line.split(',')[0].strip() == 'Time Stamp':
        headers = list(h.strip() for h in line.split(','))
        speedIndex = headers.index('Average Speed')
        start = True
        firstTime = None
        continue
      # if not started yet, go to the next line
      if not start:
        continue
      # get the time, speed
      line = line.split(',')
      ## get time
      raw_time = line[0].strip()
      ### convert time into datetime object, then to seconds since epoch
      dt_time = dt.datetime.strptime(raw_time, '%m/%d/%Y %H:%M')
      time = tmod.mktime(dt_time.timetuple())
      if firstTime is None:
        firstTime = time
        time = 0.0
      else:
        time -= firstTime
      ## get speed
      speed = float(line[speedIndex])
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
  with open(outname,'w') as outfile:
    outfile.writelines('Time,Speed'+os.linesep)
    for i in range(len(times)):
      outfile.writelines('{},{}'.format(times[i],speeds[i])+os.linesep)

# if run from command line
if __name__ == '__main__':
  datasets = ['beresford051201.csv',
              'beresford060102.csv',
              'beresford060131.csv',
              'beresford060301.csv',
              'beresford060402.csv',
              'beresford060501.csv',
              'beresford060601.csv',
              'beresford060710.csv',
              'beresford060731.csv',
              'beresford060830.csv',
              'beresford061005.csv',
              'beresford061101.csv',
              'beresford061203.csv']
  allspeed = []
  alltimes = []
  for d in datasets:
    new = readData(d)
    allspeed.extend(new['speed'])
    alltimes.extend(new['time'])

  writeData(alltimes,allspeed,'beresford06.csv')



