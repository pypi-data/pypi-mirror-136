from enum import Enum
from typing import Any, NamedTuple

class _corner(NamedTuple):
    top_left: Any
    top_right: Any
    bottom_left: Any
    bottom_right: Any

class AprilTagFamily(Enum):
    TAG_16h5: Any
    TAG_25h9: Any
    TAG_36h10: Any
    TAG_36h11: Any

class AprilTagDetection:
    def __init__(self, top_right, top_left, bottom_right, bottom_left, tag_id) -> None: ...
    def markup_image(self, image, tag_id: bool = ...): ...
    @property
    def tag_id(self): ...
    @property
    def corners(self): ...

class AprilTagDetector:
    def __init__(self, family: AprilTagFamily) -> None: ...
    def detect(self, image): ...
