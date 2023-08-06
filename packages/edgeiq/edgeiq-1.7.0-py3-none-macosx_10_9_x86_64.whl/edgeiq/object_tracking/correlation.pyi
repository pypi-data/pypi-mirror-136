from .object_tracking import DEFAULT_DEREGISTER_FRAMES as DEFAULT_DEREGISTER_FRAMES, DEFAULT_MAX_DISTANCE as DEFAULT_MAX_DISTANCE, DEFAULT_MIN_INERTIA as DEFAULT_MIN_INERTIA, TrackablePrediction as TrackablePrediction, TrackerAlgorithm as TrackerAlgorithm, TrackingResults as TrackingResults
from enum import Enum
from typing import Any

class TrackingState(Enum):
    DETECT: str
    REDETECT: str

class TrackableCorrelationPrediction(TrackablePrediction):
    state: Any
    tracker: Any
    def init(self) -> None: ...
    def handle_found(self, prediction, dereg_tracked_obj, **kwargs) -> None: ...
    def handle_disappeared(self, image, reg_tracked_obj, can_track_new_obj, **kwargs) -> None: ...

class CorrelationTracker:
    def __init__(self, max_objects: Any | None = ..., deregister_frames=..., max_distance=..., min_inertia=..., enter_cb: Any | None = ..., exit_cb: Any | None = ..., **kwargs) -> None: ...
    def update(self, predictions, image): ...
