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
            for i in beatmap.hitobjects:
                i.flip()

            beatmap.difficulty["CircleSize"] *= 1.3
            beatmap.difficulty["ApproachRate"] *= 1.4
            beatmap.difficulty["OverallDifficulty"] *= 1.4
            beatmap.difficulty["HPDrainRate"] *= 1.4

            beatmap.hitTimeWindows["300"] /= 1.4
            beatmap.hitTimeWindows["100"] /= 1.4
            beatmap.hitTimeWindows["50"] /= 1.4
            beatmap.hitTimeWindows["miss"] /= 1.4

        if i == Mod.DoubleTime or i == Mod.Nightcore:
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

        if i == Mod.Easy:
            beatmap.difficulty["CircleSize"] /= 2
            beatmap.difficulty["ApproachRate"] /= 2
            beatmap.difficulty["OverallDifficulty"] /= 2
            beatmap.difficulty["ApproachRate"] /= 2

            beatmap.hitTimeWindows["300"] *= 0.5
            beatmap.hitTimeWindows["100"] *= 0.5
            beatmap.hitTimeWindows["50"] *= 0.5
            beatmap.hitTimeWindows["miss"] *= 0.5

        if i == Mod.HalfTime:
            beatmap.hitTimeWindows["300"] *= (4/3)
            beatmap.hitTimeWindows["100"] *= (4/3)
            beatmap.hitTimeWindows["50"] *= (4/3)
            beatmap.hitTimeWindows["miss"] *= (4/3)

def unapplyMods(beatmap, mods):
    if not mods:
        return
            
    for i in mods:
        if i == Mod.HardRock:
            for i in beatmap.hitobjects:
                i.flip()

            beatmap.difficulty["CircleSize"] /= 1.3
            beatmap.difficulty["ApproachRate"] /= 1.4
            beatmap.difficulty["OverallDifficulty"] /= 1.4
            beatmap.difficulty["HPDrainRate"] /= 1.4

            beatmap.hitTimeWindows["300"] *= 1.4
            beatmap.hitTimeWindows["100"] *= 1.4
            beatmap.hitTimeWindows["50"] *= 1.4
            beatmap.hitTimeWindows["miss"] *= 1.4

        if i == Mod.DoubleTime:
            beatmap.hitTimeWindows["300"] /= (2 / 3)
            beatmap.hitTimeWindows["100"] /= (2 / 3)
            beatmap.hitTimeWindows["50"] /= (2 / 3)
            beatmap.hitTimeWindows["miss"] /= (2 / 3)

        if i == Mod.Easy:
            beatmap.difficulty["CircleSize"] *= 2
            beatmap.difficulty["ApproachRate"] *= 2
            beatmap.difficulty["OverallDifficulty"] *= 2
            beatmap.difficulty["ApproachRate"] *= 2

            beatmap.hitTimeWindows["300"] /= 0.5
            beatmap.hitTimeWindows["100"] /= 0.5
            beatmap.hitTimeWindows["50"] /= 0.5
            beatmap.hitTimeWindows["miss"] /= 0.5

        if i == Mod.HalfTime:
            beatmap.hitTimeWindows["300"] /= (4 / 3)
            beatmap.hitTimeWindows["100"] /= (4 / 3)
            beatmap.hitTimeWindows["50"] /= (4 / 3)
            beatmap.hitTimeWindows["miss"] /= (4 / 3)