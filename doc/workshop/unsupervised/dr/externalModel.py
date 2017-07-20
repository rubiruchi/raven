import math
import numpy as np

def SwissRoll(t,x):
	"""
	Generates a Swiss roll by taking the t coordinate above and using it to
	determine the x and z coordinates by way of applying an Archimedean spiral
	to the point
	@In, t, float
	@In, x, float
	@Out, y, float
	@Out, z, float
	"""
	r = ArchimedeanSpiral(t)
	y = r*np.cos(t)
	z = r*np.sin(t)
	return y,z

def ArchimedeanSpiral(t):
	"""
	An equation that yields the distance of a point traveling at a constant
	speed with a fixed angular velocity.
	@In, t, floating point value specifying the elapsed travel time
	@Out, r, the current
	"""
	a = 0
	b = 1./2*math.pi
	c = 1.
	r = a + b*t**(1./c)
	return r

def run(self,Input):
  self.y,self.z = SwissRoll(self.t,self.x)
