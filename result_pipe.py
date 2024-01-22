from livekit import rtc 
from typing import Literal, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
import uuid
from datetime import datetime
import json
import time




CLASSIFIER_RESULT_TOPIC = "classifier-result-topic"
DETECTOR_RESULT_TOPIC = "detector-result-topic"
TRACKER_RESULT_TOPIC = "tracker-result-topic"
TOPICS_LIST = [CLASSIFIER_RESULT_TOPIC, DETECTOR_RESULT_TOPIC, TRACKER_RESULT_TOPIC]
TOPICS_TYPE = Literal[CLASSIFIER_RESULT_TOPIC, DETECTOR_RESULT_TOPIC, TRACKER_RESULT_TOPIC]


async def connect_to_room(url, token):
    room = rtc.Room()
    await room.connect(url, token)
    return room


def get_unique_id():
    return str(uuid.uuid4())


# an implementation of receiving results via data channel
# following LiveKit's ChatManager interface

@dataclass
class ModelResult:
    message: Optional[str] = None
    id: str = field(default_factory=get_unique_id)
    timestamp: datetime = field(default_factory=datetime.now)
    deleted: bool = field(default=False)

    # These fields are not part of the wire protocol. They are here to provide
    # context for the application.
    participant: Optional[rtc.room.Participant] = None
    is_local: bool = field(default=False)

    @classmethod
    def from_jsondict(cls, d: Dict[str, Any]) -> "ModelResult":
        # older version of the protocol didn't contain a message ID, so we'll create one
        id = d.get("id") or get_unique_id()
        timestamp = datetime.now()
        if d.get("timestamp"):
            timestamp = datetime.fromtimestamp(d.get("timestamp", 0) / 1000.0)
        msg = cls(
            id=id,
            timestamp=timestamp,
        )
        msg.update_from_jsondict(d)
        return msg

    def update_from_jsondict(self, d: Dict[str, Any]) -> None:
        self.message = d.get("message")
        self.deleted = d.get("deleted", False)

    def asjsondict(self):
        """Returns a JSON serializable dictionary representation of the message."""
        d = {
            "id": self.id,
            "message": self.message,
            "timestamp": int(self.timestamp.timestamp() * 1000),
        }
        if self.deleted:
            d["deleted"] = True
        return d


class ResultPipe(rtc._event_emitter.EventEmitter[Literal["message_received",]]):
    def __init__(self, room: rtc.Room):
        super().__init__()
        self.room = room
        self.lp = room.local_participant
    
        room.on("data_received", self._on_data_received)
    
    def close(self):
        self.room.off("data_received", self._on_data_received)
    
    async def send_message(self, message: str, topic: TOPICS_TYPE):
        datum = ModelResult(message=message, is_local=True, participant=self.lp)
        await self.lp.publish_data(
            payload=json.dumps(datum.asjsondict()),
            kind=rtc.DataPacketKind.KIND_RELIABLE,
            topic=topic,
        )
        return datum
    
    def _on_data_received(self, pkt: rtc.DataPacketKind):
        if pkt.topic in TOPICS_LIST:
            print(f"data received by {self.lp.name} with topic {pkt.topic}")
            result = ModelResult.from_jsondict(json.loads(pkt.data))
            result_message_json = json.loads(result.message)
            print(result_message_json)
            backend_received_frame_timestamp = result_message_json["metadata"]["timestamp"]
            latency = time.time() - backend_received_frame_timestamp
            print(f"Latency from DirectAI backend receiving frame to receiving results via data channel: {latency}")
            self.emit("message_received", result)
            # # #
            # add other logic here
            # # #