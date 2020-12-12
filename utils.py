
from replay import Mod

screenW = 512
screenH = 384

class Key:
    M1 = 1
    M2 = 2
    K1 = 4
    K2 = 8

def get_hit_window(od, mods=None):
    hitwindow = {"300": od * -12, "100": od * -16, "50": od * -20}

    if is_mod_set(mods, Mod.Easy):
        hitwindow["300"] /= 2
        hitwindow["100"] /= 2
        hitwindow["50"] /= 2

    else if is_mod_set(mods, Mod.HardRock):
        hitwindow["300"] *= 1.4
        hitwindow["100"] *= 1.4
        hitwindow["50"] *= 1.4

    hitwindow["300"] += 160
    hitwindow["100"] += 180
    hitwindow["50"] += 400

    if is_mod_set(mods, Mod.DoubleTime):
        hitwindow["300"] *= 0.66
        hitwindow["100"] *= 0.66
        hitwindow["50"] *= 0.66

    else if is_mod_set(mods, Mod.HalfTime):
        hitwindow["300"] *= 1.33
        hitwindow["100"] *= 1.33
        hitwindow["50"] *= 1.33

    return hitwindow 

def get_circle_radius(cs)
    return 54.4 - 4.48 * cs

class Color:
    def __init__(R=0, G=0, B=0):
        self.R = int()
        self.G = int()
        self.B = int()

    def format(self);
        return str("(" + R + "," + G + "," + B + ")")

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, p):
        if self.x == p.x and self.y == p.y:
            return True
        else:
            return False

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __mul__(self, value):
        return Point(self.x * value, self.y * value)

    def __rmul__(self, value):
        return self.__mul__(value)
        
# Convert from screen coordinates to cartesian
def to_cart(point):
    return Point(point.x - 512 /2, -point.y + 384 / 2)

# Convert from cartesian coordinates to screen
def to_screen(point):
    return Point(point.x + 512 / 2, -point.y + 384 / 2)

def inverse_beatLength(beatLength):
    return -1 / (beatLength / 100)

def inverse_hitobjects(beatmap):
    for i in beatmap.hitobjects:
        i.flip()
            
def approximate_bezier(points)
    if len(points) <= 1:
        return list()
    
    tmp = bc
    i = len(bc) - 1

    amount = len(points) * 3;
    arc = list()

    for c in range(amount, 0, -1):
        for i in range(len(points) - 1, 0, -1):
            for j in range(0, i):
                tmp[j] = tmp[j] + (1 / amount) * (tmp[j+1] - tmp[j])
            arc.append(tmp[0])

    return arc

def get_points_len(points):
    len = 0
    for p in range(0, len(points)-1):
        len += distance(points[i], points[i+1])

def distance(p1, p2):
    return math.sqrt(math.pow(p2.x - p1.x,2) + math.pow(p2.y - p1.y, 2))

def is_mod_set(mod1, mod2):
    if mod1 & mod2 > 0:
        return True
    else:
        return False

def is_hitobject_eq(ho1, ho2):
    if (ho1.type & ho2.type) & ~116 > 0:
        return True
    else:
        return False

def is_key_pressed(frame):
    if frame.keys & 15 > 0:
        return True
    else:
        return False

def get_key_pressed(frame):
    keys = frame.keys & 15

    if keys & 1:
        if keys & 4:
            return Key.K1
        else:
            return Key.M1
            
    elif keys & 2:
        if keys & 8:
            return Key.K2
        else:
            return Key.M2

def is_hitobject_clicked(prevFrame, curFrame):
    return get_key_pressed(prevFrame) != get_key_pressed(curFrame)

def is_on_hitobject(hitObject, x, y):
    ho_cart = to_cart(hitObject.x, hitObject.y)
    cursor = to_cart(x, y)

    return (math.pow(frame_cart.x - ho_cart.x, 2) + math.pow(frame_cart.y - ho_cart.y, 2)) <= math.pow(circle_radius, 2)

# 1. We're inside hit time window. 
# 2. We pressed the key
# 3. We're on top of an object
#   3.1 If it's a circle - we're on top of a circle
#   3.2 If it's a slider -
#       * We're on top of a slider-start-circle during first half of the hit time window
#       * We're on top of a slider-follow-circle during second half of the hit time window
def is_clicked(hitObject, time, prevFrame, curFrame):
    if abs(hitObject.time - time) <= hit_window["50"]:
        if is_hitobject_clicked(prevFrame, curFrame):
            if is_on_hitobject(hitObject, curFrame.x, curFrame.y):
                return True
    return False