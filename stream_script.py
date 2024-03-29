import os
import requests
import webbrowser
from dotenv import load_dotenv
import time
import asyncio
import sys

load_dotenv()


LIVEKIT_TOKEN_FOR_DIRECTAI = os.getenv("LIVEKIT_TOKEN_FOR_DIRECTAI")
LIVEKIT_TOKEN_FOR_USER = os.getenv("LIVEKIT_TOKEN_FOR_USER")
LIVEKIT_TOKEN_FOR_RESULTS = os.getenv("LIVEKIT_TOKEN_FOR_RESULTS", '')
LIVEKIT_WS_URL = os.getenv("LIVEKIT_WS_URL")
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")

DIRECTAI_BASE_URL = "https://api.free.directai.io"

REBROADCAST_ANNOTATIONS = True


def assemble_tracker_webrtc_config():
    ### TO MODIFY AS YOU WISH ###
    ### Add more detectors, add more things to include/exclude ###
    ## There are optional threshold parameters in the tracker config as well ##
    
    detector_configs = []
    
    # add a basic face detector
    # make sure it doesn't mistake a whole person for a face
    detector_configs.append(
        {
            "name": "face",
            "incs": ["face"],
            "excs": ["person"]
        }
    )
    
    # add an eye detector
    # make sure it gets eyes regardless of whether they're open or closed
    detector_configs.append(
        {
            "name": "eye",
            "incs": ["eye", "closed eye", "open eye"],
            "excs": []
        }
    )
    
    # add a nose detector
    # make sure it doesn't mistake a nostril for a nose
    detector_configs.append(
        {
            "name": "nose",
            "incs": ["nose"],
            "excs": ["nostril"]
        }
    )
    
    # add a detector that goes off when it sees a smile
    # reduce false positives by excluding other mouth-related objects
    detector_configs.append(
        {
            "name": "smile",
            "incs": ["smile"],
            "excs": ["mouth", "closed mouth", "open mouth", "teeth", "lips"]
        }
    )
    
    # add a detector that goes off when it sees a fist
    # reduce false positives by saying that by default when it sees a hand, it's not a fist
    detector_configs.append(
        {
            "name": "fist",
            "incs": ["fist"],
            "excs": ["hand", "open hand"]
        }
    )
    
    # add anything else you want! :)
    # you can test detectors by going to https://directai.io

    tracker_config = {
        "detectors": detector_configs,
        
        # whether or not to rebroadcast detections as annotations
        "rebroadcast_annotations": REBROADCAST_ANNOTATIONS,
        
        # these control how much a new detection must match a track to be considered a match
        # higher means more nonlinear motion is allowed, but more false positives
        # lower assumes more linear / less motion
        "first_match_thresh": 1.1,
        "second_match_thresh": 1.05,
        "third_match_thresh": 1.01,
        
        # these control confidence required to detect an object
        "det_thresh": 0.15,
        "track_thresh": 0.15,
        "min_thresh": 0.05,
        
        # these control how much to rely on visual as opposed to motion priors for tracking
        "reid_weight": 5.0,
        "reid_decay": 0.99,
    }
    
    webrtc_stream_tracker_config = {
        "return_via_data_channel": LIVEKIT_TOKEN_FOR_RESULTS != '',
        "tracker_config": tracker_config,
        "webhook_url": "",
        "webrtc_url": LIVEKIT_WS_URL,
        "token": LIVEKIT_TOKEN_FOR_DIRECTAI,
        "timeout": 5,
    }
    
    return webrtc_stream_tracker_config


def assemble_classifier_webrtc_config(headers):
    ### TO MODIFY AS YOU WISH ###
    ### Add more classes, add more things to include/exclude ###
    
    config = {
        "classifier_configs": [
            {
                "name": "happy",
                "examples_to_include": [
                    "happy person", "happy", "person who is happy", "person smiling", "feeling happy"
                ],
                "examples_to_exclude": []
            },
            {
                "name": "sad",
                "examples_to_include": [
                    "sad person", "sad", "person who is sad", "person frowning", "person crying", "upset person", "feeling sad"
                ]
            },
            {
                "name": "angry",
                "examples_to_include": [
                    "angry person", "angry", "person who is angry", "feeling angry"
                ]
            },
            {
                "name": "scared",
                "examples_to_include": [
                    "scared person", "scared", "person who is scared", "fearful person", "fearful", "person who is fearful", "feeling scared"
                ]
            },
            {
                "name": "neutral",
                "examples_to_include": [
                    "person showing no emotion", "emotionless person", "person with a blank expression", "person with no expression"
                ],
                "examples_to_exclude": [
                    "person showing emotion", "facial expression", "person expressing emotion", "emotional person", "emotion"
                ]
            }
        ]
    }
    
    response = requests.post(
        DIRECTAI_BASE_URL + "/deploy_classifier",
        json=config,
        headers=headers
    )
    
    deployed_id = response.json()["deployed_id"]
    print(f"Deployed ID for classifier: {deployed_id}")
    
    webrtc_stream_tracker_config = {
        "return_via_data_channel": LIVEKIT_TOKEN_FOR_RESULTS != '',
        "webhook_url": "",
        "webrtc_url": LIVEKIT_WS_URL,
        "token": LIVEKIT_TOKEN_FOR_DIRECTAI,
        "deployed_id": deployed_id,
        "timeout": 5,
        "rebroadcast_annotations": REBROADCAST_ANNOTATIONS,
    }
    
    return webrtc_stream_tracker_config
    

def get_directai_access_token(
    client_id,
    client_secret,
    base_url = DIRECTAI_BASE_URL
):
    body = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(f"{base_url}/token", json=body)
    return response.json()["access_token"]


def start_classifier():
    directai_access_token = get_directai_access_token(
        DIRECTAI_CLIENT_ID,
        DIRECTAI_CLIENT_SECRET
    )
    
    headers = {
        'Authorization': directai_access_token,
        'Content-Type': 'application/json'
    }
    webrtc_config = assemble_classifier_webrtc_config(headers)
    
    run_livekit_tracker_endpoint = DIRECTAI_BASE_URL + "/run_classifier_on_livekit_stream"
    resp = requests.post(run_livekit_tracker_endpoint, json=webrtc_config, headers=headers)
    response = resp.json()
    print(response)
    tracker_id = response['tracker_instance_id']
    
    return tracker_id, headers


def start_tracker():
    directai_access_token = get_directai_access_token(
        DIRECTAI_CLIENT_ID,
        DIRECTAI_CLIENT_SECRET
    )
    
    headers = {
        'Authorization': directai_access_token,
        'Content-Type': 'application/json'
    }
    webrtc_config = assemble_tracker_webrtc_config()
    
    run_livekit_tracker_endpoint = DIRECTAI_BASE_URL + "/run_tracker_on_livekit_stream"
    resp = requests.post(run_livekit_tracker_endpoint, json=webrtc_config, headers=headers)
    response = resp.json()
    print(response)
    tracker_id = response['tracker_instance_id']
    
    return tracker_id, headers


async def main():
    streaming_url = "https://meet.livekit.io/custom?liveKitUrl={}&token={}".format(
        LIVEKIT_WS_URL,
        LIVEKIT_TOKEN_FOR_USER
    )
    webbrowser.open(streaming_url)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'tracker'
    assert mode in ['tracker', 'classifier'], "Mode must be either 'tracker' or 'classifier'"
    print(f"Running in {mode} mode.")
    
    tracker_id, headers = start_tracker() if mode == 'tracker' else start_classifier()
    
    result_pipe = None
    
    try:
        if LIVEKIT_TOKEN_FOR_RESULTS != '':
            # only create livekit dependency if we need it
            from result_pipe import ResultPipe, connect_to_room
            
            room = await connect_to_room(LIVEKIT_WS_URL, LIVEKIT_TOKEN_FOR_RESULTS)
            result_pipe = ResultPipe(room)
    
        print("Press CTRL-C to stop stream.")
        while True:
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        print("Stopping stream inference...")
        stop_livekit_tracker_endpoint = DIRECTAI_BASE_URL + "/stop_tracker"
        resp = requests.post(stop_livekit_tracker_endpoint, params={"tracker_instance_id": tracker_id}, headers=headers)
        if "OK" in resp.text:
            print("Stream inference stopped successfully.")
        else:
            print("Stream inference did not stop successfully.")
            print(resp.text)
            
        if result_pipe is not None:
            result_pipe.close()
            await room.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Done.")