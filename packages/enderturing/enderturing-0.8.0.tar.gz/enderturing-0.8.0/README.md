# Ender Turing

Ender Turing is a solution for voice content understanding, analytics and business insights.
Check [enderturing.com](https://enderturing.com/) for details.

## Installation

```shell
$ pip install enderturing
```

For using streaming speech recognition functions, you'll also need FFmpeg installed.

Ubuntu:
```shell
$ sudo apt install ffmpeg
```

MacOS homebrew:
```shell
$ brew install ffmpeg
```

For other OS, please follow FFmpeg installation guides.

## Quick Start

```python
import asyncio
from enderturing import Config, EnderTuring, RecognitionResultFormat

# create configuration
config = Config.from_url("https://admin%40local.enderturing.com:your_password@enterturing.yourcompany.com")
et = EnderTuring(config)

# access sessions list
sessions = et.sessions.list()
print(sessions)

# get recognizer for one of configured languages
recognizer = et.get_speech_recognizer(language='en')

async def run_stream_recog(f, r, result_format):
    async with r.stream_recognize(f, result_format=result_format) as rec:
        text = await rec.read()
    return text

# recognize specified file
loop = asyncio.get_event_loop()
task = loop.create_task(run_stream_recog("my_audio.mp3", recognizer, result_format=RecognitionResultFormat.text))
loop.run_until_complete(task)
print(task.result())
```

## Usage

SDK contains two major parts:

- Using Ender Turing REST API
- Speech recognition

## Using Ender Turing API

All API calls are accessible via an instance or `EnderTuring`. API methods are grouped, and each
group is a property of `EnderTuring`. Examples:
```python
from enderturing import Config, EnderTuring, RecognitionResultFormat

et = EnderTuring(Config.from_env())

# access sessions list
sessions = et.sessions.list()

# working with ASR
et.asr.get_instances(active_only=True)

# accessing raw json
et.raw.create_event(caller_id='1234', event_data={"type": "hold"})
```

## Access Configuration

To access API, you need to know an authentication key (login), authentication secret (password), and
installation URL (e.g. https://enderturing.yourcompany.com/)

There are multiple ways to pass config options:

- from environmental variables (`Config.from_env()`).
- creating `Config` with parameters (e.g. `Config(auth_key="my_login", auth_secret="my_secret"")`)
- using Enter Turing configuration URL (`Config.from_url()`)

## Creating Speech Recognizer

There two options to create a speech recognizer:

### If you have access to API configured:
```python
recognizer = et.get_speech_recognizer(language='en')
```

### If you know URL and sample rate of desired ASR instance:
```python
from enderturing import AsrConfig, SpeechRecognizer

config = AsrConfig(url="wss://enderturing", sample_rate=8000)
recognizer = SpeechRecognizer(config)
```

## Recognizing a File

`SpeechRecognizer.recognize_file` method returns an async text stream. Depending on parameters,
each line contains either a text of utterance or serialized JSON.

If you are only interested in results after recognition is complete, you can use the `read()` method. E.g.

```python
async with recognizer.recognize_file("my_audio.wav", result_format=RecognitionResultFormat.text) as rec:
    text = await rec.read()
```

If you prefer getting words and phrases as soon as they are recognized - you can
use the `readline()` method instead. E.g.

```python
async with recognizer.recognize_file(src, result_format=RecognitionResultFormat.jsonl) as rec:
    line = await rec.readline()
    while line:
        # Now line contains a json string, you can save it or do something else with it
        line = await rec.readline()

```

## Working With Multichannel Audio

If an audio file has more than one channel - by default system will recognize each channel and
return a transcript for each channel. To change the default behavior - you can use `channels`
parameter of `SpeechRecognizer.recognize_file`. Please check method documentation for details.

Sometimes an audio is stored as a file per channel, e.g., contact center call generates two files:
one for a client and one for a support agent. But for analysis, it's preferable to see transcripts
of the files merged as a dialog. In this scenario, you can use
`recognizer.recognize_joined_file([audio1, audio2])`.

## License

Released under the MIT license.
