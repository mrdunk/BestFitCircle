#!/usr/bin/env python3

from typing import Tuple, List
from enum import Enum
import sys
import math
import random
import matplotlib.pyplot as plt

Point = Tuple[float, float]
Vector2 = Tuple[float, float]

class Tactic(Enum):
    """ Either comparing the angle from each point to a proposed circle's center
    with the expected value
    or
    comparing the radius from each point to a proposed circle's center with the
    expected value can be used to determine the best fit.
    """
    ANGLE = 1
    RADIUS = 2

def generatePoints(centre: Point, radius: float, numPoints: int, jitterRatio: float = 0) -> List[Point]:
    """ Generate a set of points representing a perturbed circle. """
    def jitter() -> float:
        diamiter = radius * math.pi * 2
        jitterSize = jitterRatio * diamiter / numPoints
        return random.random() * 2 * jitterSize - jitterSize

    points: List[Point] = []
    angle_segment = math.pi * 2 / numPoints
    angle = 0

    while angle < math.pi * 2:
        point = (centre[0] + radius * math.cos(angle) + jitter(),
                 centre[1] + radius * math.sin(angle) + jitter())
        points.append(point)
        angle += angle_segment

    return points

def display(points: List[Point], color, width=1) -> None:
    """ Display a set of points representing a line. """
    x = []
    y = []
    for point in points:
        x.append(point[0])
        y.append(point[1])
    plt.plot(x, y, c=color, linewidth=width)

def normal(point0: Point, point1: Point) -> Tuple[Point, float]:
    """ Calculate the mid point between 2 points and the normal of the line segment
    joining them. """
    mid: Point = ((point0[0] + point1[0]) / 2, (point0[1] + point1[1]) / 2)
    v: Vector2 = (point1[0] - point0[0], point1[1] - point0[1])
    normal: Vector2 = (-v[1], v[0])

    angle = math.atan(v[1] / v[0])
    angleNorm = math.atan(normal[1] / normal[0])
    assert(abs(abs(angle - angleNorm) - math.pi / 2) < 0.001)

    x = [mid[0], mid[0] + normal[0]]
    y = [mid[1], mid[1] + normal[1]]
    plt.plot(x, y, ":")

    return (mid, angleNorm)

def fitAt(centerHint: Point, scanRange: float, points: List[Point], tactic: Tactic) -> (Point, float):
    """ Find the circle that fits the points best who's center is within `scanRange`
    distance of the point `centerHint`. """
    bestDiff = None
    bestPoint = None
    avRadius = None

    # Try using various x,y points on map as center of circle.
    x = centerHint[0] - scanRange
    while x < centerHint[0] + scanRange:
        y = centerHint[1] - scanRange
        while y < centerHint[1] + scanRange:

            if tactic == Tactic.RADIUS:
                avRadius = averageRadius((x, y), points)
            sampleCount = 0
            sampleAngleDiff = 0
            sampleRadiusDiff = 0
            lastPoint = None
            for point in points:
                if lastPoint:
                    midPoint, angleNorm = normal(lastPoint, point)

                    # Compare the normal angle of this line segment to the expected
                    # angle of a line between the line segment's mid point and
                    # the circle we are comparing against mid point.
                    # TODO: We should also compare against the radius of the circle
                    # as well as the angle..
                    angleToCenter = math.atan((float(y) - midPoint[1]) / (float(x) - midPoint[0]))
                    radius = math.sqrt((float(y) - midPoint[1]) ** 2 + (float(x) - midPoint[0]) ** 2)
                    sampleCount += 1
                    if tactic == Tactic.ANGLE:
                        sampleAngleDiff += abs(angleToCenter - angleNorm)
                    else:
                        sampleRadiusDiff += abs(radius - avRadius)

                lastPoint = point

            # We have 2 ways of calculating the circle's fit:
            if tactic == Tactic.ANGLE:
                # The center point who's normal angles deviate least from those expected
                # has the best fit.
                if bestDiff is None or bestDiff > sampleAngleDiff / sampleCount:
                    bestDiff = sampleAngleDiff / sampleCount
                    bestPoint = (x, y)
            else:  # tactic == Tactic.RADIUS
                # The center point who's radius to each point deviates least from the average radius
                # has the best fit.
                if bestDiff is None or bestDiff > sampleRadiusDiff / sampleCount:
                    bestDiff = sampleRadiusDiff / sampleCount
                    bestPoint = (x, y)

            y += scanRange / 2
        x += scanRange / 2

    return (bestPoint, bestDiff)


def fit(points: List[Point], tactic: Tactic) -> Point:
    """ Return an estimated center point for an ark passing through a list of points. """
    xTotal = 0
    yTotal = 0
    minX = None
    maxX = None
    minY = None
    maxY = None
    for point in points:
        xTotal += point[0]
        yTotal += point[1]
        if minX is None or point[0] < minX:
            minX = point[0]
        if maxX is None or point[0] > maxX:
            maxX = point[0]
        if minY is None or point[1] < minY:
            minY = point[1]
        if maxY is None or point[1] > maxY:
            maxY = point[1]
    scanRange = max(maxX - minX, maxY - minY)
    centerHint = (xTotal / len(points), yTotal / len(points))

    accuacy = None
    lastAccuracy = None
    print(centerHint, accuacy, scanRange)
    # Loop with increasing resolution until an acceptable fit is found.
    while accuacy is None or lastAccuracy is None or lastAccuracy - accuacy > 0.0001 or scanRange > 0.01:
        lastAccuracy = accuacy
        centerHint, accuacy = fitAt(centerHint, scanRange, points, tactic)
        scanRange /= 2
        print(centerHint, accuacy, scanRange)

    return centerHint

def averageRadius(center: Point, points: List[Point]) -> float:
    totDist = 0
    for point in points:
        totDist += math.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return totDist / len(points)


def help() -> None:
    print()
    print("Usage:")
    print("", sys.argv[0], "[NUMBER_OF_POINTS_IN_CIRCLE] [RATIO_OF_POINTS_DISPLAYED] [RATIO_OF_JITTER] [RADIUS/ANGLE]")
    exit()


def main():
    numPoints = 50
    arkRatio = 0.3
    jitterRatio = 0.05
    radius = 10
    tactic = Tactic.RADIUS

    if len(sys.argv) > 1:
        try:
            numPoints = int(sys.argv[1].strip())
        except ValueError:
            print("Invalid parameter: ", sys.argv[1].strip())
            print("Should be a positive integer.")
            help()

        if numPoints < 1:
            print("Invalid parameter: ", sys.argv[1].strip())
            print("Should be a positive integer.")
            help()

    if len(sys.argv) > 2:
        try:
            arkRatio = float(sys.argv[2].strip())
        except ValueError:
            print("Invalid parameter: ", sys.argv[2].strip())
            print("Should be a number between 0 and 1.")
            help()

        if arkRatio <= 0 or arkRatio > 1:
            print("Invalid parameter: ", sys.argv[2].strip())
            print("Should be a number between 0 and 1.")
            help()

    if len(sys.argv) > 3:
        try:
            jitterRatio = float(sys.argv[3].strip())
        except ValueError:
            print("Invalid parameter: ", sys.argv[3].strip())
            print("Should be a number between 0 and 1.")
            help()

        if jitterRatio <= 0 or jitterRatio > 1:
            print("Invalid parameter: ", sys.argv[3].strip())
            print("Should be a number between 0 and 1.")
            help()

    if len(sys.argv) > 4:
        t = sys.argv[4].strip().upper()
        names = [name for name, member in Tactic.__members__.items()]
        if t not in names:
            print("Invalid parameter: ", sys.argv[4].strip(), t)
            print("Should be one of", names)
            help()
        tactic = Tactic[t]

    if len(sys.argv) > 5:
        print("Too many arguments.")
        help()

    usePoints = int(arkRatio * numPoints)
    startCenter = ((random.random() * 2 * radius - radius), (random.random() * 2 * radius - radius))

    print("Using " + tactic.name + " to determine best fit.")
    print("Number of points in generated circle:", numPoints)
    print("Ratio of circle to use:", arkRatio, " ie: ", usePoints, " points")
    print("Ratio of distance between points to perturb coordinates by:", jitterRatio)
    print("Radius of generated circle:", radius)
    print("Center of generated circle:", startCenter)
    print()

    # Generate the perturbed points here.
    points = generatePoints(startCenter, radius, numPoints, jitterRatio)[:usePoints]
    display(points, "black", 2)

    # Try to fit a circle to the points.
    center = fit(points, tactic)

    # From here on we display results on graph.
    print("Calculated center:", center)
    marker = plt.plot(startCenter[0], startCenter[1], 'o', label='Generated', c="black")
    plt.setp(marker[0], markersize=5)
    marker = plt.plot(center[0], center[1], 'o', label='Fitted', c="red")
    plt.setp(marker[0], markersize=3)
    legend = plt.legend(loc='upper right', shadow=True)
    display(generatePoints(center, averageRadius(center, points), 90), "red")
    plt.show()


if __name__ == "__main__":
    main()
