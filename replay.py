from enum import Enum
import lzma, struct, datetime

class GameMode(Enum):
    Standard = 0
    Taiko = 1
    CatchTheBeat = 2
    Osumania = 3


class Mod(Enum):
    NoMod          = 0
    NoFail         = 1
    Easy           = 2
    NoVideo        = 4
    Hidden         = 8
    HardRock       = 16
    SuddenDeath    = 32
    DoubleTime     = 64
    Relax          = 128
    HalfTime       = 256
    Nightcore      = 512
    Flashlight     = 1024
    Autoplay       = 2048
    SpunOut        = 4096
    Autopilot      = 8192
    Perfect        = 16384
    Key4           = 32768
    Key5           = 65536
    Key6           = 131072
    Key7           = 262144
    Key8           = 524288
    keyMod         = 1015808
    FadeIn         = 1048576
    Random         = 2097152
    LastMod        = 4194304
    TargetPractice = 8388608
    Key9           = 16777216
    Coop           = 33554432
    Key1           = 67108864
    Key3           = 134217728
    Key2           = 268435456

class ReplayFrame():
    def __init__(self, time, x, y, keys):
        self.time = time
        self.x = x
        self.y = y
        self.keys = keys


class Replay(object):
    __BYTE = 1
    __SHORT = 2
    __INT = 4
    __LONG = 8

    #Order of field initilization matters.
    def __init__(self, replay_path):
        self.offset = 0
        self.game_mode = None
        self.game_version = None
        self.beatmap_hash = None
        self.player_name = None
        self.replay_hash = None
        self.number_300s = None
        self.number_100s = None
        self.number_50s = None
        self.gekis = None
        self.katus = None
        self.misses = None
        self.score = None
        self.max_combo = None
        self.is_perfect_combo = None
        self.mods = None
        self.life_bar_graph = None
        self.timestamp = None
        self.frames = None
        self.totalTime = 0

        try:
            with open(replay_path, 'rb') as f:
                data = f.read()
        except IOError:
            print("[ERROR] Replay couldn't be opened")
        
        self.parse_replay_and_initialize_fields(data)

    def parse_replay_and_initialize_fields(self, replay_data):
        self.parse_game_mode_and_version(replay_data)
        self.parse_beatmap_hash(replay_data)
        self.parse_player_name(replay_data)
        self.parse_replay_hash(replay_data)
        self.parse_score_stats(replay_data)
        self.parse_life_bar_graph(replay_data)
        self.parse_timestamp_and_replay_length(replay_data)
        self.parse_play_data(replay_data)

    def parse_game_mode_and_version(self, replay_data):
        format_specifier = "<bi"
        data = struct.unpack_from(format_specifier, replay_data, self.offset)
        self.offset += struct.calcsize(format_specifier)
        self.game_mode, self.game_version = (GameMode(data[0]), data[1])

    def unpack_game_stats(self, game_stats):
        self.number_300s, self.number_100s, self.number_50s, self.gekis, self.katus, self.misses, self.score, self.max_combo, self.is_perfect_combo, self.mods = game_stats

    def parse_mod_combination(self):
        # Generator yielding value of each bit in an integer if it's set + value
        # of LSB no matter what .
        def bits(n):
            if n == 0:
                yield 0
            while n:
                b = n & (~n+1)
                yield b
                n ^= b

        bit_values_gen = bits(self.mods)
        self.mods = frozenset(Mod(mod_val) for mod_val in bit_values_gen)

    def parse_score_stats(self, replay_data):
        format_specifier = "<hhhhhhih?i"
        data = struct.unpack_from(format_specifier, replay_data, self.offset)
        self.unpack_game_stats(data)
        self.parse_mod_combination()
        self.offset += struct.calcsize(format_specifier)

    @staticmethod
    def __parse_as_int(bytestring):
        return int.from_bytes(bytestring, byteorder='little')

    def __decode(self, binarystream):
        result = 0
        shift = 0
        while True:
            byte = binarystream[self.offset]
            self.offset += 1
            result = result |((byte & 0b01111111) << shift)
            if (byte & 0b10000000) == 0x00:
                break
            shift += 7
        return result

    def parse_player_name(self, replay_data):
        self.player_name = self.parse_string(replay_data)

    def parse_string(self, replay_data):
        if replay_data[self.offset] == 0x00:
            self.offset += Replay.__BYTE
        elif replay_data[self.offset] == 0x0b:
            self.offset += Replay.__BYTE
            string_length = self.__decode(replay_data)
            offset_end = self.offset + string_length
            string = replay_data[self.offset:offset_end].decode("utf-8")
            self.offset = offset_end
            return string
        else:
            #TODO: Replace with custom exception
            raise Exception("Invalid replay")

    def parse_beatmap_hash(self, replay_data):
        self.beatmap_hash = self.parse_string(replay_data)

    def parse_replay_hash(self, replay_data):
        self.replay_hash = self.parse_string(replay_data)

    def parse_life_bar_graph(self, replay_data):
        self.life_bar_graph = self.parse_string(replay_data)

    def parse_timestamp_and_replay_length(self, replay_data):
        format_specifier = "<qi"
        (t, self.__replay_length) = struct.unpack_from(format_specifier, replay_data, self.offset)
        self.timestamp = datetime.datetime.min + datetime.timedelta(microseconds=t/10)
        self.offset += struct.calcsize(format_specifier)

    def parse_play_data(self, replay_data):
        offset_end = self.offset+self.__replay_length
        if self.game_mode != GameMode.Standard:
            self.frames = None
        else:
            datastring = lzma.decompress(replay_data[self.offset:offset_end], format=lzma.FORMAT_AUTO).decode('ascii')[:-1]
            events = [eventstring.split('|') for eventstring in datastring.split(',')]
            self.frames = [ReplayFrame(int(event[0]), float(event[1]), float(event[2]), int(event[3])) for event in events]
        self.offset = offset_end

