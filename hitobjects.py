import copy

from utils import screen_height, Point, calc_length, calc_distance, get_point


class TimingPoint:
    def __init__(self,
                 time,
                 beat_length,
                 meter,
                 sample_set,
                 sample_index,
                 volume,
                 ttype,
                 effect):

        self.time = time
        self.meter = meter
        self.sampleSet = sample_set
        self.sampleIndex = sample_index
        self.volume = volume
        self.type = ttype
        self.effect = effect

        if self.type == 1:
            self.beatLength = float(beat_length)

        elif self.type == 0:
            self.beatLength = beat_length

        
class Hitobject:
    def __init__(self,
                 x,
                 y,
                 time,
                 object_type,
                 hit_sound):
        self.x = x
        self.y = y
        self.time = time
        self.type = object_type
        self.hitsound = hit_sound

    def flip(self):
        self.y = screen_height - self.y

        
class Circle(Hitobject):
    def __init__(self, x, y, time, object_type, hit_sound):
        super().__init__(x, y, time, object_type, hit_sound)
        self.hitsample = None
        
class Slider(Hitobject):
    def __init__(self,
                 x,
                 y,
                 time,
                 object_type,
                 hit_sound):
        
        super().__init__(x, y, time, object_type, hit_sound)
        
        self.curveType = "B"
        self.curvePoints = list()
        self.slides = None
        self.length = None
        self.edgeSounds = None
        self.edgeSets = None
        self.hitsample = None


    # Calculates only B splines for now
    # Because all resulting sliders are B type
    def calcLength(self):
        if self.curveType == "B":
            if len(self.curvePoints) <= 1:
                return 0

            points = list()
            points.append(Point(self.x, self.y))
            points.extend(self.curvePoints)

            self.length = calc_length(points)


    def calcBezierLength(self):
        if self.curveType == "B":
            if len(self.curvePoints) <= 1:
                return 0

            # If the curve is too dense and big - give up and calculate it the easy way

            points = list()
            points.append(Point(self.x, self.y))
            points.extend(self.curvePoints)

            tmp = copy.deepcopy(points)

            self.calcLength()
            amount = int(self.length)

            arcPoints = list()

            # B Spline
            t = 0
            while amount != t:

                # One point
                i = len(tmp) - 1
                while i > 0:

                    k = 0
                    while k < i:
                        tmp[k] = get_point(tmp[k], tmp[k+1], t/amount)
                        k += 1
                    i -= 1

                arcPoints.append(copy.deepcopy(tmp[0]))
                t += 1

            #for i in range(0, 150):
                #if(len(arcPoints)) <= 2:
                    #break

                #for i in range(0, len(arcPoints) - 2):
                    #arcPoints[i+1].x = (arcPoints[i].x + arcPoints[i+2].x) / 2
                    #arcPoints[i+1].y = (arcPoints[i].y + arcPoints[i+2].y) / 2

            self.length = calc_length(arcPoints)

            
    def calcDuration(self, beatmapSV, beatLength, svm):
        self.duration = (self.length / (beatmapSV * svm * 100)) * self.slides * beatLength

    def flip(self):
        super().flip()
        for i in self.curvePoints:
            i.y = screen_height - i.y
                                                                                                                                                    
        
class Spinner(Hitobject):
    def __init__(self,
                 x,
                 y,
                 time,
                 object_type,
                 hit_sound):
        
        super().__init__(x, y, time, object_type, hit_sound)

        self.endtime = None
        self.hitsample = None
        
