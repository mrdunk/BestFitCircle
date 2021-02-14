# BestFitCircle

A proof of concept for fitting a circle to an array of points.
This is somewhere between calculated and brute force.

2 tactics can be chosen from:
1. Compare the angle from each line segment on the ark to the center of the proposed circle. This should be as close as possible to the angle of the line segment's normal.
2. Compare the radius from each line segment on the ark to the center of the proposed circle. This should be as close as possible to the average radius.

Option 2. works better for noisy data.  
I suspect a combination of the 2 tactics would yield the best results.

An example from running with noisy data: `./main.py 50 0.5 1 radius`
![screenshot](https://github.com/mrdunk/BestFitCircle/blob/master/assets/BestFitCircle_screenshot.png)

This needs Python3 and the Matplotlib library to display output.
`python -m pip install -U matplotlib`

It is not optimized at all. I threw it together in an evening after discussing the concept with a friend who is interested in CNC machine CAM software.
