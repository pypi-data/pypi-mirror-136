from edgeiq import barcode_detection as barcode_detection, bounding_box as bounding_box, image_classification as image_classification, object_detection as object_detection, object_tracking as object_tracking, pose_estimation as pose_estimation, qrcode_detection as qrcode_detection, zones as zones
from edgeiq._production_client import PRODUCTION_CLIENT as PRODUCTION_CLIENT
from typing import Any

POSE_ESTIMATION_RESULT: Any
OBJECT_DETECTION_RESULT: Any
CLASSIFICATION_RESULT: Any
TRACKING_RESULT: Any
ZONE_RESULT: Any
BARCODE_RESULT: Any
QRCODE_RESULT: Any

def load_analytics_results(filepath): ...
def publish_analytics(results, tag: Any | None = ...) -> None: ...
