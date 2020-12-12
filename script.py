from osrparse import Replay
from beatmap import Beatmap
from utils import *
from hitobjects import *
import math
import sys
import getopt
import re
import copy

def usage():
    print("Usage:\n"
          "  -b, --beatmap=PATH     absolute path to an .osu file in \"\" quotes\n"
          "  -r, --replay=PATH      absolute path to an .osr file in \"\" quotes\n"
          "  -f, --folder           read files from the\n"
          "  -a, --anchor=TYPE      gray or red\n"
          "  -h, --help             print this message\n")

beatmap_path = str()
replay_path = str()
anchor_type = str()

longopts = ["help", "beatmap=", "replay=", "anchor="]
opts, args = getopt.getopt(sys.argv[1:], "hb:r:a:", longopts)

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit()      

    if opt in ("-f", "--folder"):
        beatmap_path = sys.argv[0]
          
    if opt in ("-b", "--beatmap"):
        beatmap_path = arg
             
    if opt in ("-r", "--replay"):
        replay_path = arg

    if opt in ("-a", "--anchor"):
        if arg == "red" or arg == "gray":
            anchor_type = arg

beatmap = Beatmap(beatmap_path)
replay = Replay(replay_path)

if is_mod_set(replay.mods, Mod.HardRock):
    inverse_hitobjects(beatmap)
        
last_key = None
hit_window = get_hit_window(beatmap.difficulty["OverallDifficulty"], replay.mods)
circle_radius = get_circle_radius(beatmap.difficulty["CircleSize"])
time = replay.frames[0].time
is_last_hitobject = False
start = 1

# Iterate over beatmap objects
for hitobject in beatmap.hitobjects:
    
    if hitobject == len(beatmap.hitobjects)-1:
        is_last_hitobject = True

    if is_hitobject_eq(hitobject, Hitobject.Spinner): 
        continue;
    
    for f in range(start, len(replay.frames)):
        start = f
        time += frame.time
 
        if is_clicked(hitobject, time, frame[::-1], frame):

            lastKeys = replay.frames[f].keys
            time -= replay.frames[f].time

            break;



beatmap.metadata["Tags"].append("osu!rtm")
beatmap.metadata["Version"] = "osu!rtm's " + beatmap.metadata["Version"]

filename = beatmap.metadata["Artist"] 
        + " - " + beatmap.metadata["Title"] 
        + " ("  + beatmap.metadata["Creator"] + ")" 
        + " ["  + beatmap.metadata["Version"] + "].osu"

with open(filename, "w") as file:
    write_beatmap(beatmap, file)




######################################
## inside loop
######################################
oldHitobject = copy.deepcopy(beatmap.hitobjects[i])
            beatmap.hitobjects[i].x = int(replay.frames[f].x)
            beatmap.hitobjects[i].y = int(replay.frames[f].y)
            
            # If slider
            if beatmap.hitobjects[i].type & 2:

                # Relative time
                relativeTime = 0

                lastKeys = replay.frames[f].keys
                    
                # Slider curve loop i.e. here we process the slider points
                # 'g' is the index of frame inside loop
                # Dividing duration by slides gives you the raw slider duration (without return back)
                # Then we just add points to the list, change some inner variables, calculate length of the slider, and set the amount of slides
                beatmap.hitobjects[i].curvePoints = list()
                g = f + 1
                while (relativeTime <= (beatmap.hitobjects[i].duration / beatmap.hitobjects[i].slides)):
                    beatmap.hitobjects[i].curvePoints.append(Point(int(replay.frames[g].x), int(replay.frames[g].y)))
                    beatmap.hitobjects[i].curvePoints.append(Point(int(replay.frames[g].x), int(replay.frames[g].y)))

                    relativeTime += replay.frames[g].time
                    lastKeys = replay.frames[g].keys
                    g += 1
                
                beatmap.hitobjects[i].calcLength()

                # If the length is too small, artificially extend it and recalculate length
                if beatmap.hitobjects[i].length <= 5:
                    beatmap.hitobjects[i].curvePoints.append(Point(replay.frames[g-1].x+5, replay.frames[g-1].y+5))
                    beatmap.hitobject[i].curvePoints.append(Point(replay.frames[g-1].x+5, replay.frames[g-1].y+5))
 
                # Find slider's timing point
                inheritedPointCopy = copy.deepcopy(beatmap.getTimingPoint(beatmap.hitobjects[i].time, 0))
                inheritedPointCopy.time = beatmap.hitobjects[i].time
                uninheritedPoint = beatmap.getTimingPoint(beatmap.hitobjects[i].time, 1)

                # ERROR
                while True:
                    # Calculate new SVM for timing point according to new slider
                    inheritedPointCopy.svm = (oldHitobject.slides * uninheritedPoint.beatLength * beatmap.hitobjects[i].length) / (oldHitobject.duration * beatmap.difficulty["SliderMultiplier"] * 100)
                    print(inheritedPointCopy.svm)
                    if(inheritedPointCopy.svm < 0.1):
    
                        # Temp
                        beatLength = uninheritedPoint.beatLength

                        # Divide beat length for current object and write it
                        uninheritedPoint.beatLength *= 2
                        beatmap.addTimingPoint(uninheritedPoint)
                        
                        if not isLastHitobject:
                            nextUninheritedPointCopy = copy.deepcopy(beatmap.getTimingPoint(beatmap.hitobjects[i+1].time, 1))
                            
                            # If the next object doesnt have uninherited point (BPM will get messed up), write the old one
                            if not (nextUninheritedPointCopy.time <= beatmap.hitobjects[i+1].time and nextUninheritedPointCopy.time != uninheritedPoint.time):
                                nextUninheritedPointCopy.beatLength = beatLength   
                                beatmap.addTimingPoint(nextUninheritedPointCopy)
                        else:
                            break;
                        
                    else:
                        break

                beatmap.addTimingPoint(inheritedPointCopy)