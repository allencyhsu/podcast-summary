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
    *   Uses Google Gemini API to generate deep technical report-style summaries.
    *   Includes structured content such as Core Thesis, Key Technical Concepts, Contrarian Views, and Future Outlook.

## Requirements

Ensure you have Python 3.8+ and the following packages installed:

```bash
pip install requests feedparser faster-whisper google-genai
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

## File Structure

*   `dl_podcast.py`: Main program, handles downloading and the processing pipeline.
*   `fwhisper.py`: Speech transcription module.
*   `correct.py`: Typo correction module.
*   `summarize.py`: Summary generation module.

## License

Apache License 2.0
