# livekit_hello_world

## About

Run [DirectAI](https://directai.io) on a [LiveKit](https://livekit.io) stream and see the results in real time!

We will open a browser using LiveKit's [meet](https://meet.livekit.io) product and have DirectAI join the room! We'll then build on-the-fly detectors matching your descriptions and track objects in the video feed in real time!

## Getting Started
- You'll need DirectAI credentials to use the API - generate those by heading to our [landing page](https://directai.io) and logging in/signing up via the "Get API Access" button. New users get their first **10k streaming images free**!
- Generate two LiveKit tokens for the same room, one for a bot powered by DirectAI and one for your user. Check out Liveit's instructions on [Generating Keys & Tokens](https://docs.livekit.io/cloud/keys-and-tokens/). Note that you can also generate them via [Livekit's CLI](https://github.com/livekit/livekit-cli).
- Run `cp .env.template .env` and populate the env variables.
- Run `pip install -r requirements.txt` in your environment (e.g. conda, venv) of choice.

## Running It
Run `python stream_script.py` to start a LiveKit room and get started with object tracking.
