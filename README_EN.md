# Podcast Summary Tool

This is an automated tool for downloading, transcribing, correcting, and summarizing podcasts. It integrates `yt-dlp` (or `requests` for RSS audio), `faster-whisper` for speech-to-text, and the Google Gemini API for typo correction and key point summarization.

## Features

1.  **Podcast Downloader (`dl_podcast.py`)**:
    *   Supports iTunes RSS Feed search and parsing.
    *   **Keyword Filtering**: Download specific episodes based on keywords.
    *   **Weekday Filtering**: Download episodes uploaded on specific days (e.g., Mondays).
    *   Automatically creates folders named after the podcast.
    *   Supports resuming interrupted downloads.

2.  **Transcription (`fwhisper.py`)**:
    *   Uses the `faster-whisper` model (default `large-v2`) for high-accuracy speech-to-text.
    *   Supports GPU acceleration (CUDA).
    *   Outputs transcripts with timestamps.

3.  **LLM Typo Correction (`correct.py`)**:
    *   Uses Google Gemini API (default `gemini-2.5-pro`) to correct typos and homophones in the transcript.
    *   **Hotwords Support**: Built-in list of proper nouns to force correction of specific terms (e.g., names, companies).
    *   **Large File Handling**: Automatically chunks large texts to avoid API Token limits.
    *   Preserves original timestamps.

4.  **Smart Summarization (`summarize.py`)**:
    *   **Dynamic Prompt Selection**: Built-in "Smart Routing" analyzes podcast content (e.g., Tech Trends, Business Strategy, Science) and selects the best analysis framework from `prompt_template.md`.
    *   **Diverse Templates**: Supports 8+ professional analysis templates, including:
        *   General Analysis
        *   VC Perspective
        *   Mental Models
        *   Academic Research
        *   Historical Strategy
        *   Science & Health
    *   **Traditional Chinese Output**: Enforces high-quality Traditional Chinese (Taiwan) output.

## Requirements

Ensure you have Python 3.8+ and the following packages installed:

```bash
pip install requests feedparser faster-whisper google-genai nvidia-ml-py
```

Additionally, you need a Google Gemini API Key.

## Configuration

Before running `correct.py` and `summarize.py`, please set the `GEMINI_API_KEY` environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Or modify the `API_KEY` variable directly in the scripts.

## Usage

### 1. Download and Process Podcasts

Edit the `target_podcasts` list in `dl_podcast.py` to configure the podcasts you want to download:

```python
target_podcasts = [
    ("Podcast Name", "Filter Keyword", 0), # 0 represents downloading only Monday episodes
    ("Another Podcast", "Keyword"),
]
```

Run the downloader:

```bash
python dl_podcast.py
```

The script will automatically execute the following flow:
Download -> Transcribe (`fwhisper.py`) -> Correct (`correct.py`) -> Summarize (`summarize.py`)

### 2. Use Modules Individually

*   **Transcribe**: `python fwhisper.py <audio_file>`
*   **Correct**: `python correct.py <transcript_file>`
*   **Summarize**: `python summarize.py <transcript_file>`
    *   `summarize.py` automatically reads `prompt_template.md` in the same directory for smart routing.

## File Structure

*   `dl_podcast.py`: Main program, handles downloading and the processing pipeline.
*   `fwhisper.py`: Speech transcription module.
*   `correct.py`: Typo correction module.
*   `summarize.py`: Summary generation module (includes Dynamic Prompt Selection).
*   `prompt_template.md`: Library of prompt templates for various analysis styles.

## License

Apache License 2.0
