import copy
import getopt
import sys

from beatmap import Beatmap
from replay import Replay
from utils import *

sys.argv = ["osu!rtm.exe", "--beatmap=target.osu", "--replay=replay.osr"]

# Parameters
beatmap_path = str()
replay_path = str()

# Argument parsing
longopts = ["help", "beatmap=", "replay=", "gray"]
opts, args = getopt.getopt(sys.argv[1:], "ghb:r:", longopts)


useGrayAnchors = False
beatmap = None
replay = None
for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()

    if o in ("-b", "--beatmap"):
        beatmap = Beatmap(a)
        print("[GOOD] Found beatmap!")

    if o in ("-r", "--replay"):
        replay = Replay(a)
        print("[GOOD] Found replay!")

    if o in ("-g", "--gray"):
        useGrayAnchors = True


applyMods(beatmap, replay.mods)


# Loop variables
startFrame = 0
totalTimeStamp = 0
lastKeys = 0


oldTimingPoints = copy.deepcopy(beatmap.timingPoints)

print("Starting...")

# Iterate over beatmap objects
for i in range(0, len(beatmap.hitobjects)):

    if i == len(beatmap.hitobjects) - 1:
        isLastObject = True

    # Skip spinners
    if beatmap.hitobjects[i].type & 8:
        continue

    # Set total time to total time of last click
    replay.totalTime = totalTimeStamp

    # Iterate over replay frames to find objects clicked
    for f in range(startFrame, len(replay.frames) - 1):

        replay.totalTime += replay.frames[f].time

        # We found an object
        if isClicked(beatmap, replay.totalTime, beatmap.hitobjects[i], replay.frames[f], lastKeys):

            totalTimeStamp = replay.totalTime

            beatmap.hitobjects[i].x = int(replay.frames[f].x)
            beatmap.hitobjects[i].y = int(replay.frames[f].y)

            # If slider
            if beatmap.hitobjects[i].type & 2:

                beatmap.hitobjects[i].curvePoints = list()
                beatmap.hitobjects[i].curveType = "B"

                lastKeys = replay.frames[f].keys
                g = f + 1
                replay.totalTime += replay.frames[g].time

                hitobjectEndTime = round((beatmap.hitobjects[i].time + (beatmap.hitobjects[i].duration / beatmap.hitobjects[i].slides)))
                while replay.totalTime <= hitobjectEndTime:

                    curPoint = Point(round(replay.frames[g].x), round(replay.frames[g].y))
                    prevPoint = Point(round(replay.frames[g-1].x), round(replay.frames[g-1].y))

                    # Exclude duplicates
                    if curPoint != prevPoint:
                        beatmap.hitobjects[i].curvePoints.append(Point(round(replay.frames[g].x), round(replay.frames[g].y)))

                    lastKeys = replay.frames[g].keys
                    g += 1
                    replay.totalTime += replay.frames[g].time


                if len(beatmap.hitobjects[i].curvePoints) <= 1:
                    beatmap.hitobjects[i].curvePoints.append(Point(round(replay.frames[g - 1].x + 1), round(replay.frames[g - 1].y + 1)))

                # Compensate point if no exact ending frame
                """
                if replay.frames[g-1].time != hitobjectEndTime:
                    amount = calc_distance(Point(replay.frames[g-1].x, replay.frames[g-1].y), Point(replay.frames[g].x, replay.frames[g].y))
                    t = 0
                    while True:
                        p1 = Point(replay.frames[g-1].x, replay.frames[g-1].y)
                        p2 = Point(replay.frames[g].x, replay.frames[g].y)
                        p3 = p1 + (t/amount) * (p2-p1)

                        if int(
                        t += 1
                """

                # Calculate length for new slider
                if useGrayAnchors:
                    beatmap.hitobjects[i].calcBezierLength()
                else:
                    beatmap.hitobjects[i].calcLength()


                # If red anchors are used duplicate every point
                if not useGrayAnchors:
                    beatmap.hitobjects[i].curvePoints = [copy.copy(x) for x in beatmap.hitobjects[i].curvePoints for _ in range(2)]


                # Calculate new timing point for slider
                originalBeatLength = 0
                wasLess = False
                while True:
                    uninheritedPoint = copy.deepcopy(getUninheritedPoint(beatmap.timingPoints, beatmap.hitobjects[i].time))
                    inheritedPoint = copy.deepcopy(getInheritedPoint(beatmap.timingPoints, uninheritedPoint, beatmap.hitobjects[i].time))
                    if(inheritedPoint == None):
                        inheritedPoint = copy.deepcopy(uninheritedPoint)
                        inheritedPoint.type = 0

                    inheritedPoint.time = beatmap.hitobjects[i].time
                    inheritedPoint.beatLength = (beatmap.hitobjects[i].slides * uninheritedPoint.beatLength * beatmap.hitobjects[i].length) / (beatmap.hitobjects[i].duration * beatmap.difficulty["SliderMultiplier"] * 100)

                    # If SVM is less than 0.1 Compensate speed with uninherited point
                    if (inheritedPoint.beatLength < 0.1):

                        # Bad design
                        if not wasLess:
                            originalBeatLength = uninheritedPoint.beatLength
                            wasLess = True

                        # Divide beat length for current object and write it
                        uninheritedPoint.beatLength *= 2
                        uninheritedPoint.time = beatmap.hitobjects[i].time
                        beatmap.addTimingPoint(uninheritedPoint)

                    else:
                        break

                # Add new uninherited point for the next object
                if wasLess:
                    nextUninheritedPoint = copy.deepcopy(getUninheritedPoint(oldTimingPoints, beatmap.hitobjects[i + 1].time))

                    # If there's a new manual point for the next object don't add new
                    if nextUninheritedPoint.time != uninheritedPoint.time:
                        nextUninheritedPoint.beatLength = originalBeatLength
                        nextUninheritedPoint.time = beatmap.hitobjects[i + 1].time
                        beatmap.addTimingPoint(nextUninheritedPoint)


                inheritedPoint.beatLength = svmToFile(inheritedPoint.beatLength)
                beatmap.addTimingPoint(inheritedPoint)

            lastKeys = replay.frames[f].keys
            startFrame = f + 1

            printProgressBar(i, len(beatmap.hitobjects), prefix='Generating hitobjects:', suffix='Done', length=50)
            break

        lastKeys = replay.frames[f].keys

beatmap.metadata["Tags"].append("osu!rtm")
beatmap.metadata["Version"] = "osu!rtm's " + beatmap.metadata["Version"]
beatmap.filename = beatmap.metadata["Artist"] + " - " + beatmap.metadata["Title"] + " (" + beatmap.metadata[
    "Creator"] + ")" + " [" + beatmap.metadata["Version"] + "].osu"

printProgressBar(len(beatmap.hitobjects), len(beatmap.hitobjects), prefix='Generating hitobjects:', suffix='Done', length=50)

unapplyMods(beatmap, replay.mods)
print("Writing new beatmap...")
beatmap.writeFile()
print("Done!")
