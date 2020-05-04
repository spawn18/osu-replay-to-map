import math

from replay import Mod

screen_width = 512
screen_height = 384

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, value):
        return Point(self.x * value, self.y * value)

    def __rmul__(self, value):
        return self.__mul__(value)



def getUninheritedPoint(timingPoints, objectTime):
    r = None

    for point in timingPoints:
        if point.time <= objectTime:
            if point.type == 1:
                r = point
        else:
            break

    return r

def getInheritedPoint(timingPoints, uninheritedPoint, objectTime):
    r = None

    for point in timingPoints:
        if point.time <= objectTime:
            if point.time >= uninheritedPoint.time and point.type == 0:
                r = point
        else:
            break

    return r

# Convert from screen coordinates to cartesian
def stoc(p):
    return Point(p.x - 512 /2, -p.y + 384 / 2)

# Convert from cartesian coordinates to screen
def ctos(p):
    return Point(p.x + 512 / 2, -p.y + 384 / 2)

def svmToFile(sv):
    return 1 / (sv / -100)
    
def fileToSvm(sv):
    return (1 / sv) * -100



def get_point(p1, p2, t):
    return p1 + t * (p2-p1)

def calc_distance(p1, p2):
    return math.sqrt(math.pow(p2.x - p1.x, 2) + math.pow(p2.y - p1.y, 2))

def calc_length(points):
    length = 0

    for i in range(0, len(points) - 1):
        length += calc_distance(points[i], points[i+1])

    return length



def applyMods(beatmap, mods):

    if not mods:
        return

    for i in mods:
        if i == Mod.HardRock:

            # Yet hardrock makes replay be reversed
            # Probably a legacy thing

            for j in beatmap.hitobjects:
                j.flip()

            beatmap.difficulty["CircleSize"] *= 1.3
            beatmap.difficulty["ApproachRate"] *= 1.4
            beatmap.difficulty["OverallDifficulty"] *= 1.4
            beatmap.difficulty["HPDrainRate"] *= 1.4

            beatmap.hitTimeWindows["300"] /= 1.4
            beatmap.hitTimeWindows["100"] /= 1.4
            beatmap.hitTimeWindows["50"] /= 1.4
            beatmap.hitTimeWindows["miss"] /= 1.4

        elif i == Mod.DoubleTime or i == Mod.Nightcore:
            # Turns out peppy saves DT replays as nomod replays (lol)
            # What a strange decision, DT timing would take 0.(6) less space
            # and osu has to convert DT data to nomod after a play or something

            # Would have changed OD and then calculate hitwindow
            # But there's no data how accurately OD changes with DT and HT
            # All we know is that how timings change, OD/AR follow non linear formula
            # So i have to write these explicitly though they dont fit my view
            beatmap.hitTimeWindows["300"] *= (2/3)
            beatmap.hitTimeWindows["100"] *= (2/3)
            beatmap.hitTimeWindows["50"] *= (2/3)
            beatmap.hitTimeWindows["miss"] *= (2/3)

        elif i == Mod.Easy:
            beatmap.difficulty["CircleSize"] /= 2
            beatmap.difficulty["ApproachRate"] /= 2
            beatmap.difficulty["OverallDifficulty"] /= 2
            beatmap.difficulty["ApproachRate"] /= 2

            beatmap.hitTimeWindows["300"] *= 0.5
            beatmap.hitTimeWindows["100"] *= 0.5
            beatmap.hitTimeWindows["50"] *= 0.5
            beatmap.hitTimeWindows["miss"] *= 0.5

        elif i == Mod.HalfTime:
            beatmap.hitTimeWindows["300"] *= (4/3)
            beatmap.hitTimeWindows["100"] *= (4/3)
            beatmap.hitTimeWindows["50"] *= (4/3)
            beatmap.hitTimeWindows["miss"] *= (4/3)

def unapplyMods(beatmap, mods):
    if not mods:
        return
            
    for i in mods:
        if i == Mod.HardRock:

            for j in beatmap.hitobjects:
                j.flip()

            beatmap.difficulty["CircleSize"] /= 1.3
            beatmap.difficulty["ApproachRate"] /= 1.4
            beatmap.difficulty["OverallDifficulty"] /= 1.4
            beatmap.difficulty["HPDrainRate"] /= 1.4

            beatmap.hitTimeWindows["300"] *= 1.4
            beatmap.hitTimeWindows["100"] *= 1.4
            beatmap.hitTimeWindows["50"] *= 1.4
            beatmap.hitTimeWindows["miss"] *= 1.4

        elif i == Mod.DoubleTime or i == Mod.Nightcore:
            beatmap.hitTimeWindows["300"] /= (2 / 3)
            beatmap.hitTimeWindows["100"] /= (2 / 3)
            beatmap.hitTimeWindows["50"] /= (2 / 3)
            beatmap.hitTimeWindows["miss"] /= (2 / 3)

        elif i == Mod.Easy:
            beatmap.difficulty["CircleSize"] *= 2
            beatmap.difficulty["ApproachRate"] *= 2
            beatmap.difficulty["OverallDifficulty"] *= 2
            beatmap.difficulty["ApproachRate"] *= 2

            beatmap.hitTimeWindows["300"] /= 0.5
            beatmap.hitTimeWindows["100"] /= 0.5
            beatmap.hitTimeWindows["50"] /= 0.5
            beatmap.hitTimeWindows["miss"] /= 0.5

        elif i == Mod.HalfTime:
            beatmap.hitTimeWindows["300"] /= (4 / 3)
            beatmap.hitTimeWindows["100"] /= (4 / 3)
            beatmap.hitTimeWindows["50"] /= (4 / 3)
            beatmap.hitTimeWindows["miss"] /= (4 / 3)



def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print("")


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

def isClicked(beatmap, totalTime, hitobject, frame, lastKeys):

    if abs(hitobject.time - totalTime) <= beatmap.hitTimeWindows["50"]:
        if (frame.keys != lastKeys and frame.keys != 0 and lastKeys != 15):
            coordsPoint = stoc(Point(hitobject.x, hitobject.y))
            framePoint = stoc(Point(frame.x, frame.y))
            if (math.pow(framePoint.x - coordsPoint.x, 2) + math.pow(framePoint.y - coordsPoint.y, 2)) <= math.pow(beatmap.circleRadius, 2):
                return True
    return False
