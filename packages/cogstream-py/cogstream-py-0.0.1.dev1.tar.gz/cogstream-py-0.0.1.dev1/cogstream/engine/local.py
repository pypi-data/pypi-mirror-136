import logging
import queue
import time
from typing import Optional

import cv2

from cogstream.engine import Frame, EngineResult, FrameReceiveChannel
from cogstream.engine.channel import EngineChannel, ResultSendChannel, ResultReceiveChannel

logger = logging.getLogger(__name__)


class VideoCaptureChannel(FrameReceiveChannel):
    """
    FrameReceiveChannel that reads frames directly from a cv2.VideoCapture object.
    """

    def __init__(self, video_capture: cv2.VideoCapture):
        self.video_capture = video_capture
        self.frame_counter = 0

    def recv(self) -> Optional[Frame]:
        more, image = self.video_capture.read()
        if not more:
            raise ConnectionResetError

        frame = Frame(image, frame_id=self.frame_counter, timestamp=time.time())
        self.frame_counter += 1
        return frame


class ResultQueueChannel(ResultSendChannel, ResultReceiveChannel):
    """
    ResultSendChannel that writes results into a queue
    """

    def __init__(self, result_queue: queue.Queue):
        self.queue = result_queue

    def send_result(self, result: EngineResult):
        self.queue.put(result)

    def recv_result(self) -> Optional[EngineResult]:
        return self.queue.get()


class LocalEngineChannel(EngineChannel):
    """
    EngineChannel to serve an engine locally directly attached to a camera and sending the results to a queue.
    """

    def __init__(self, video_capture, result_queue: queue.Queue) -> None:
        super().__init__(VideoCaptureChannel(video_capture), ResultQueueChannel(result_queue))
