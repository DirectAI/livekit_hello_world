# livekit_hello_world

## About

Run [DirectAI](https://directai.io) on a [LiveKit](https://livekit.io) stream and see the results in real time!

We will open a browser using LiveKit's [meet](https://meet.livekit.io) product and have DirectAI join the room! We'll then build on-the-fly object detectors matching your descriptions and track objects in the video feed in real time!

## Getting Started
- You'll need DirectAI credentials to use the API - generate those by heading to our [landing page](https://directai.io) and logging in/signing up via the "Get API Access" button. New users get their first **10k streaming images free**!
- Generate two LiveKit tokens for the same room, one for a bot powered by DirectAI and one for your user. Check out Liveit's instructions on [Generating Keys & Tokens](https://docs.livekit.io/cloud/keys-and-tokens/). Note that you can also generate them via [Livekit's CLI](https://github.com/livekit/livekit-cli).
- Optionally, create a third token for the same room, which will be used to receive real-time results via the WebRTC data channel. (Results can also be received via a webhook.) Note that if you don't want the results listener to be visible, make sure to issue a LiveKit token that is marked as belonging to an invisible/hidden attendee.
- Note that LiveKit token permission checking isn't robust so without correct permissions there may be silent failures. The easiest path would be to ensure that each token has permission to subscribe to and publish tracks, and also to access the data channel.
- Run `cp .env.template .env` and populate the env variables.
- Run `pip install -r requirements.txt` in your environment (e.g. conda, venv) of choice.

## Running It
- Run `python stream_script.py tracker` to start a LiveKit room and get started with object tracking. If you include a token in LIVEKIT_TOKEN_FOR_RESULTS, you'll see printed in the terminal real-time object tracking results returned to the client via WebRTC data channels. In addition, you'll see a measure of latency from when DirectAI received the frame from LiveKit to when the client received the tracking results from the data channel. We would expect this latency to be <200ms if `rebroadcast_annotations = False`, and <500ms otherwise.
- Alternatively, you can run `python stream_script.py classifier` to get started with classification. By default, this will run a sentiment analysis model, with a configuration you can see in the code. The latency for the classifier should be less.
- Feel free to modify the objects / classes / configurations as you wish! Experiment with it and see what it can do :)
- Note that the predictions of the model will get worse as image quality decreases. For LiveKit, a worse internet connection will mean lower quality streams, which will therefore mean lower quality model results. So a better internet connection will yield better results!

## Stopping It
Just press CTRL-C to stop the process!
