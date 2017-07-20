# file: rangefinder.py
import numpy as np
def run(self,Inputs):
  th0_rad = self.th0 * np.pi/180.

  self.tf = time_of_flight(self.v0, th0_rad, self.g)

  self.R = x_position(self.v0, th0_rad, self.tf)

  vx = self.v0 * np.cos(th0_rad)
  vy = velocity_y(self.v0, th0_rad, self.g, self.tf)
  self.vf = velocity_mag(vx,vy)

def time_of_flight(v0,th0,g):
  return 2. * v0 * np.sin(th0) / g

def x_position(v0,th0,t):
  return v0 * np.cos(th0) * t

def velocity_y(v0,th0,g,t):
  return v0*np.sin(th0) - g*t

def velocity_mag(vx,vy):
  return np.sqrt(vx*vx + vy*vy)
