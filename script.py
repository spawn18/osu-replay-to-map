import math

from replay import Replay
from beatmap import Beatmap
from utils import applyMods, Point, svmToFile, unapplyMods, stoc
import sys
import getopt
import copy

sys.argv = ["osu!rtm.exe", "--beatmap=target.osu", "--replay=replay.osr"]

# Parameters
beatmap_path = str()
replay_path = str()

# Argument parsing
longopts = ["help", "beatmap=", "replay=", "gray"]
opts, args = getopt.getopt(sys.argv[1:], "ghb:r:", longopts)


# Help function
def usage():
    print("Usage:")
    print("-b or --beatmap [with argument]    absolute path to an .osu file. Keep it in \"\" quotes. It should be --beatmap=\"YOURPATH\" \n")
    print("-r or --replay [with argument]    absolute path to an .osr file. In \"\" quotes\n")
    print("-h or --help    print this usage guide\n")
    print("-g or --gray    to use gray anchors instead of red")
    print("Example 1: osu!rtm.exe -b \"C:\\Users\\Me\\AppData\\Local\\osu!\\Songs\\SomeSong\\SomeDifficulty.osu\" -r \"C:\\Users\\Me\\AppData\\Local\\osu!\\Replays\\SomeReplay.osr\"")
    print("Example 2: osu!rtm.exe --beatmap=\"C:\\Users\\Me\\AppData\\Local\\osu!\\Songs\\SomeSong\\SomeDifficulty.osu\" --replay=\"C:\\Users\\Me\\AppData\\Local\\osu!\\Replays\\SomeReplay.osr\"")
    print("Advice: You better put the replay and beatmap file in the same temporary folder and rename them to avoid long paths")

useGrayAnchors = False

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()

    if o in ("-b", "--beatmap"):
        if a.startswith("\""):
            beatmap_path = a[1:-1]
            tmp = beatmap_path.split("\\")
            beatmap_path = tmp[len(tmp) - 1]
        else:
            beatmap_path = a

    if o in ("-r", "--replay"):
        if a.startswith("\""):
            replay_path = a[1:-1]
            tmp = replay_path.split("\\")
            replay_path = tmp[len(tmp) - 1]
        else:
            replay_path = a

    if o in ("-g", "--gray"):
        useGrayAnchors = True

# Replay
replay = Replay(replay_path)

beatmapOld = Beatmap(beatmap_path)
beatmapNew = Beatmap(beatmap_path)

applyMods(beatmapNew, replay.mods)
applyMods(beatmapOld, replay.mods)



# Keys that were pressed on the previous frame
lastKeys = 0

def isClicked(totalTime, hitobject, frame, lastKeys):

    if abs(hitobject.time - totalTime) <= beatmapNew.hitTimeWindows["50"]:
        if (frame.keys != lastKeys and frame.keys != 0 and lastKeys != 15):
            coordsPoint = stoc(Point(hitobject.x, hitobject.y))
            framePoint = stoc(Point(frame.x, frame.y))
            if (math.pow(framePoint.x - coordsPoint.x, 2) + math.pow(framePoint.y - coordsPoint.y, 2)) <= math.pow(beatmapNew.circleRadius, 2):
                print("With lastKeys:{}".format(lastKeys))
                return True
    return False

startFrame = 0
totalTimeStamp = 0

#ttime = 0
#for j in replay.frames:
    #ttime += j.time
    #print("TotalTime:{} x:{} y:{} keys:{} ".format(ttime, j.x, j.y, j.keys))


# Iterate over beatmap objects
for i in range(0, len(beatmapNew.hitobjects)):

    # Skip spinners
    if beatmapNew.hitobjects[i].type & 8:
        continue

    # Set total time to total time of last click
    replay.totalTime = totalTimeStamp

    # Iterate over replay frames to find objects clicked
    for f in range(startFrame, len(replay.frames) - 1):

        replay.totalTime += replay.frames[f].time

        # We found an object
        if isClicked(replay.totalTime, beatmapNew.hitobjects[i], replay.frames[f], lastKeys):

            totalTimeStamp = replay.totalTime

            beatmapNew.hitobjects[i].x = int(replay.frames[f].x)
            beatmapNew.hitobjects[i].y = int(replay.frames[f].y)

            # If slider
            if beatmapNew.hitobjects[i].type & 2:

                print("Clicked slider at ^")
                beatmapNew.hitobjects[i].curvePoints = list()
                beatmapNew.hitobjects[i].curveType = "B"

                lastKeys = replay.frames[f].keys

                g = f + 1
                replay.totalTime += replay.frames[g].time
                while replay.totalTime <= (beatmapNew.hitobjects[i].time + (beatmapNew.hitobjects[i].duration / beatmapNew.hitobjects[i].slides)):

                    beatmapNew.hitobjects[i].curvePoints.append(Point(round(replay.frames[g].x), round(replay.frames[g].y)))

                    lastKeys = replay.frames[g].keys
                    g += 1
                    replay.totalTime += replay.frames[g].time

                # This branch has little chance of happening yet it does happen
                # It is difficult to explain as to why it works this way
                # But if you were into project hard like me this would be the only acceptable solution. At least for me now
                if (len(beatmapNew.hitobjects[i].curvePoints) == 0) :
                    beatmapNew.hitobjects[i].curvePoints.append(Point(round(replay.frames[g-1].x + 1), round(replay.frames[g-1].y + 1)))

                # Compensate point if no exact ending frame
                """
                TODO ???
                else:
                    ms = replay.frames[g].time - replay.frames[g - 1].time
                    if (int(ms) != 0):
                        distance = math.sqrt(math.pow(replay.frames[g].x - replay.frames[g-1].x,2) + math.pow(replay.frames[g].y - replay.frames[g-1].y,2 ))
                """

                # If the length is none - extend the slider artificially
                # This branch has 99.9% more chance of occuring with mouse players. Guess why...
                # First one to guess pm me and get supporter on osu
                while True:
                    if not useGrayAnchors:
                        beatmapNew.hitobjects[i].calcLength()
                    else:
                        beatmapNew.hitobjects[i].calcBezierLength()

                    if int(beatmapNew.hitobjects[i].length) != 0:
                        break
                    beatmapNew.hitobjects[i].curvePoints.append(Point(round(replay.frames[g - 1].x + 1), round(replay.frames[g - 1].y + 1)))

                if not useGrayAnchors:
                    beatmapNew.hitobjects[i].curvePoints = [x for x in beatmapNew.hitobjects[i].curvePoints for _ in range(2)]

                # Calculate new timing point for slider
                uninheritedPoint = beatmapNew.getUninheritedPoint(beatmapOld.hitobjects[i].time)
                inheritedPointCopy = copy.deepcopy(beatmapOld.getInheritedPoint(uninheritedPoint, beatmapNew.hitobjects[i].time))
                if(inheritedPointCopy == None):
                    inheritedPointCopy = copy.deepcopy(uninheritedPoint)
                    inheritedPointCopy.type = 0

                inheritedPointCopy.time = beatmapNew.hitobjects[i].time
                inheritedPointCopy.beatLength = (beatmapOld.hitobjects[i].slides * uninheritedPoint.beatLength * beatmapNew.hitobjects[i].length) / (beatmapOld.hitobjects[i].duration * beatmapNew.difficulty["SliderMultiplier"] * 100)

                # If SVM is less than 0.1 (osu counts any svm's less than that as 0.1)
                # Compensate speed with uninherited point
                """
                if (inheritedPointCopy.beatLength < 0.1):
                    beatLength = uninheritedPoint.beatLength

                        # Divide beat length for current object and write it
                        uninheritedPoint.beatLength *= 2
                        beatmapNew.addTimingPoint(uninheritedPoint)

                        if not isLastHitobject:
                            nextUninheritedPointCopy = copy.deepcopy(beatmapOld.getUninheritedPoint(beatmapOld.hitobjects[i + 1].time))

                            # If the next object doesnt have uninherited point (BPM will get messed up), write the old one
                            if nextUninheritedPointCopy.time == uninheritedPoint.time:
                                nextUninheritedPointCopy.beatLength = beatLength
                                beatmapNew.addTimingPoint(nextUninheritedPointCopy)
                        else:
                            break

                    else:
                        break
                """

                inheritedPointCopy.beatLength = svmToFile(inheritedPointCopy.beatLength)
                beatmapNew.addTimingPoint(inheritedPointCopy)

            lastKeys = replay.frames[f].keys
            startFrame = f + 1
            break

        lastKeys = replay.frames[f].keys


beatmapNew.metadata["Tags"].append("osu!rtm")
beatmapNew.metadata["Version"] = "osu!rtm's " + beatmapNew.metadata["Version"]
beatmapNew.filename = beatmapNew.metadata["Artist"] + " - " + beatmapNew.metadata["Title"] + " (" + beatmapNew.metadata[
    "Creator"] + ")" + " [" + beatmapNew.metadata["Version"] + "].osu"


# Write to new file
unapplyMods(beatmapNew, replay.mods)
beatmapNew.writeFile()
