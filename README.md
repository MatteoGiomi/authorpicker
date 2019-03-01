# authorpicker

assign papers to authors depending on number of contributions, time since last active, and position. Each author is assigned
points which are then used to weight the probability of being assigned to a certain paper.

The points are assigned to each author according to the following schema:

### position related points:
	- PhD students & postdoc + 5
	- master students + 3
	- staff + 0
  
###	effort related points:
	- lead gets + 2 point extra
	- 2 points for every completed projects
	- 1 point for each useful tool made available on github.

### points decrease with time since last activity
	- minus 1 point for every 6 month of inactivity

Finally, a floor of 1 point is granted, so that there is a non-zero probability of being cited. See the example jupyther notebook for more details.
