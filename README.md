# Social Media Summarizing tool

**Read full blog here - https://app.capacities.io/home/f4a1ac95-6b67-4204-b154-629fa44c3576**  

A workflow tool for downloading social media videos, extracting audio, transcribing speech, and generating AI-powered notes using local LLMs.

## Features

- **Video Download & Processing**: Downloads videos from social media URLs and extracts high-quality audio (WAV, 16kHz mono)
- **Speech Transcription**: Uses Vosk to transcribe audio into text, Download the vosk model and unzip it before running the app.
- **AI Note Generation**: Streams local LLM completions (LFM2_5-230M-IQ4_XS) to generate research notes from transcriptions
- **Streamlit UI**: Interactive interface for controlling the workflow

## Project Structure

```
workflow-post-py/
├── config/
│   └── loader.py       # Configuration loading
├── src/
│   ├── chat.py         # Local LLM streaming with llama.cpp
│   └── media.py        # Video download, audio extraction, transcription
├── pyproject.toml      # Project metadata and dependencies
```

## Installation

### Prerequisites

- Python 3.12 or later
- A local `llama.cpp` server running (default port 8080)

### Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

Or install directly from `pyproject.toml`:

```bash
pip install .
```

### Configuration

The project reads configuration from `config/server.toml`:

```toml
[server]
server = "http://127.0.0.1:6767"
api-key = "no"
```

Update the `server` and `api-key` values in `config/server.toml` to match your local setup.

**For sound extracting purposes, it uses ffmpeg. Install the ffmpeg here - `C:\ffmpeg\bin`**
## Quick Start

1. **Start the llama.cpp server** (if not already running):
   ```bash
   # Example: start llama.cpp on port 8080
   ./llama.cpp server --port 8080
   ```

2. **Run the application**:
   ```bash
   streamlit run main.py
   ```

3. **Use the interface**:
   - Enter a video URL in the left panel
   - Click "Download and Process" to download and extract audio
   - Click "Generate Summary Note" to stream a note using the local LLM

## How It Works

### Video Download & Audio Extraction

The `download_social_video` function uses `yt-dlp` to download the video and simultaneously extract audio using `FFmpegExtractAudio` with:
- 16kHz sample rate (`-ar 16000`)
- Mono channel (`-ac 1`)
- The original video is preserved (`keepvideo: True`)

### Speech Transcription

The `transcribe_wav` function uses the Vosk speech recognition model (`Models/vosk-model-small-en-us-0.15`) to transcribe the extracted WAV file into text.

### AI Note Generation

The `stream_local_completion` function streams a chat completion from a local llama.cpp instance. It uses the system prompt to guide the model in generating research notes based on the transcription.

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `server` | `http://127.0.0.1:6767` | Local llama.cpp server URL |
| `api-key` | `no` | API key for the server |
| `model_name` | `unsloth/LFM2_5-230M-IQ4_XS` | LLM model for note generation |


## Limitations

1. **Private Video URLs** – Some private video URLs are not compatible with YT-Dlp, which limits the ability to download content that requires authentication or is restricted.

2. **Long Video Processing** – Long videos take considerable time to process, leading to slower download times and potentially incomplete or delayed results.

## Possible Upgrades

1. **Multimodal LLM Processing** – Integrate other multimodal large language models to process entire videos at once, potentially reducing processing time and improving efficiency for long or complex content.


## Requirements

- Python 3.14+
- llama.cpp server running locally
- `ipykernel>=7.3.0`
- `openai>=2.53.0`
- `orjson>=3.11.9`
- `requests>=2.34.2`
- `rich>=15.0.0`
- `streamlit>=1.61.1`
- `vosk>=0.3.45`
- `yt-dlp[curl-cffi,default]>=2026.7.4`

## License

This project is licensed under the MIT License (see `LICENSE` file for details).

## Contributing

Contributions are welcome! Please ensure any changes maintain compatibility with the local llama.cpp server and the streaming workflow.

