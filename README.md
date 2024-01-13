# livekit_hello_world

Run [DirectAI](https://directai.io) on a [LiveKit](https://livekit.io) stream and see the results in real time!

You'll need DirectAI credentials to use the API, which can be obtained on our website. At the moment, by default new users do not have streaming permissions, so if you're interested please email us at ben@directai.io to get permissions!

Generate two LiveKit tokens for the same room, one for a bot powered by DirectAI and one for your user. We will open a browser using LiveKit's [meet](https://meet.livekit.io) product and have DirectAI join the room using the token. We'll then build on the fly detectors matching your descriptions and track objects in the video feed in real time!

Run `cp .env.template .env` and populate the env variables.

Run `python stream_script.py` to start a LiveKit room and get started with object tracking.
