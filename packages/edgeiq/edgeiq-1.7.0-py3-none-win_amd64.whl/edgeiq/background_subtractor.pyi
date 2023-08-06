from enum import Enum
from typing import Any

class MOG2:
    cuda: Any
    history: Any
    var_threshold: Any
    detect_shadows: Any
    bgmog2: Any
    def __init__(self, history: int = ..., var_threshold: int = ..., detect_shadows: bool = ..., cuda: bool = ...) -> None: ...
    frame: Any
    def process_frame(self, frame, learning_rate: int = ...): ...

def get_contours(raw_contours): ...
def get_boundingboxes(contours): ...
def get_moments(contours): ...

class SortingMethod(Enum):
    LEFT_RIGHT: str
    RIGHT_LEFT: str
    BOTTOM_TOP: str
    TOP_BOTTOM: str

def get_sorted(method: SortingMethod, contours): ...
