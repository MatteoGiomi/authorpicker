# randomly assign authors to papers, using weights that takes into 
# account position & effort. A possible schema is the following:
#
#	position related points:
#	- PhD students & postdoc + 5
#	- master students + 3
#	- staff + 0
#
#	effor related points:
#	- lead gets + 2 point extra
#	- 2 points for every completed C&C projects
#	- minus 1 point for every 6 month of inactivity
#
#	software contributions:
#	- 1 point for each calibration tool made available on github.
#
#	a floor of 1 point is granted, so that there is a non-zero probability 
#	of being cited.

import numpy as np
from astropy.time import Time

class Contributor:
	"""
		class to represent one contributor, and to 
		compute its total point score depending on
		merit, position, and time.
	"""

	points_for_phd		= 5		# position related points
	points_for_postdoc	= 5
	points_for_master	= 3
	points_for_staff	= 0
	points_for_lead		= 2		# points for the lead of the C&C WG
	points_for_project	= 2		# points for every completed C&C project
	points_for_sofware	= 1		# points for each relevant made available on github. 
	points_inactive		= 1		# every 6 months of inactivity, you loose these points
	minimum_wage		= 1		# if one has no points, we give him a tiny bit of hope

	allowed_postions = ['phd', 'master', 'postdoc', 'staff']

	def __init__(self, name, **kwargs):
		"""
			mandatory kwargs:
				'position'			: `str`
				'lead'				: `bool`
				'completed_tasks'	: `float`
				'software_packages'	: `float`
				'last_active'		: `str` #astropy.time acceptable
				'affiliation'		: `str`
		"""
		self.name				= name
		self.lead				= kwargs['lead']
		self.completed_tasks	= kwargs['completed_tasks']
		self.software_packages	= kwargs['software_packages']
		self.position			= kwargs['position']
		self.affiliation		= kwargs['affiliation']
		
		# see if contributor is currently active or not
		if kwargs['last_active'] != 'current':
			self.is_active = False
			self.time_since_last_active = Time(kwargs['last_active'])
		elif kwargs['last_active'] == 'current':
			self.is_active = True
		else:
			raise ValueError("last_active either 'current' or astropy.time.Time string. got %s"%
					kwargs['last_active'])

	def sum_points(self):
		
		# all hail the great leader!
		total = 0
		if self.lead:
			total += Contributor.points_for_lead
		
		# points on current position
		if self.position == 'phd':
			total += Contributor.points_for_phd
		elif self.position == 'master':
			total += Contributor.points_for_master
		elif self.position == 'postdoc':
			total += Contributor.points_for_postdoc
		elif self.position == 'staff':
			total += Contributor.points_for_staff
		else:
			raise ValueError("position %s not recognized. Allowed are %s"%
				(position, Contributor.allowed_positions))
		
		# points for each completed project and software
		total += Contributor.points_for_project * self.completed_tasks
		total += Contributor.points_for_sofware * self.software_packages
		
		# decrease for inactivity
		if not self.is_active:
			days_since_last_active = (Time.now() - Time(self.time_since_last_active)).jd
			total -= Contributor.points_inactive * days_since_last_active / (30 * 6)
		else:
			pass
		
		# add a floor & return
		if total <= 0:
			total = Contributor.minimum_wage
		return total


class Eligibles:
	"""
		class to represent a collection of contributors,
		and to pick among them.
	"""
	
	# let's have our own random generator, so results will be reproducible
	np.random.seed(42)
	my_choice = np.random.choice
	
	def __init__(self, contributors_def):
		"""
			contributors_def: `dict`
				each entry in the dict must represent one contributors, e.g.:
				{
					'auth1': {
						'position'			: `str`
						'lead'				: `bool`
						'completed_tasks'	: `float`
						'software_packages'	: `float`
						'last_active'		: `str`
					},
					'auth2': {
						...
					},
					...
				}
		"""
		
		self.contributors = [
			Contributor(name, **pars) for name, pars in contributors_def.items()]
		
		# normalize total poitns
		self.points = np.array([cc.sum_points() for cc in self.contributors])
		self.names	= [cc.name for cc in self.contributors]
		self.total_points = sum(self.points)

	def pprint(self):
		for icc, cc in enumerate(self.contributors):
			print ("%d) %s : %.2f points"%(icc, cc.name, cc.sum_points()))

	def pick_author(self):
		return Eligibles.my_choice(self.contributors, p = self.points/self.total_points)
	
	def assign(self, paper_list):
		out = [self.pick_author() for _ in range(len(paper_list))]
		for ip in range(len(paper_list)):
			print ("%d) %s --> %s %s"%(
				ip, paper_list[ip], out[ip].name, out[ip].affiliation))
		return out
