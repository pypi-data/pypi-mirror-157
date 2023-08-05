from enum import Enum

class SequenceGeneratorType(Enum):
    PERLIN = 0
    DAN_MA_PERLIN = 1
    SINUSOID = 2

class SequenceType(Enum):
    FISP = 0
    TRUEFISP = 1