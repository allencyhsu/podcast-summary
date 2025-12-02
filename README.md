# Podcast Summary Tool

這是一個自動化的 Podcast 下載、轉錄、校正與摘要工具。它整合了 `yt-dlp` (或是 `requests` 下載 RSS 音檔)、`faster-whisper` 進行語音轉文字，並利用 Google Gemini API 進行錯字校正與重點摘要。

## 功能特色 (Features)

1.  **Podcast 下載 (`dl_podcast.py`)**:
    *   支援 iTunes RSS Feed 搜尋與解析。
    *   **關鍵字過濾**: 可指定關鍵字下載特定單集。
    *   **週間過濾**: 可指定下載特定星期（如週一）上傳的節目。
    *   自動建立以節目名稱命名的資料夾。
    *   支援斷點續傳。

2.  **語音轉錄 (`fwhisper.py`)**:
    *   使用 `faster-whisper` 模型 (預設 `large-v2`) 進行高準確度的語音轉文字。
    *   支援 GPU 加速 (CUDA)。
    *   輸出帶有時間軸的文字稿。

3.  **LLM 錯字校正 (`correct.py`)**:
    *   使用 Google Gemini API (預設 `gemini-2.5-pro`) 修正轉錄稿中的錯別字與同音異字。
    *   **Hotwords 支援**: 內建專有名詞列表，強制修正特定詞彙（如人名、公司名）。
    *   **長文處理**: 自動將長文本切塊 (Chunking) 處理，避免超過 API Token 限制。
    *   保留原始時間軸。

4.  **智慧摘要 (`summarize.py`)**:
    *   **動態 Prompt 選擇**: 內建「智慧路由」功能，自動分析 Podcast 內容類型（如科技趨勢、商業戰略、心理科普等），並從 `prompt_template.md` 中選擇最適合的分析框架。
    *   **多樣化範本**: 支援 8 種以上的專業分析範本，包括：
        *   全域分析 (General Analysis)
        *   創投獵手 (VC Perspective)
        *   大師思維 (Mental Models)
        *   學術研讀 (Academic Research)
        *   科技史觀 (Historical Strategy)
        *   科普新知 (Science & Health) 等。
    *   **繁體中文輸出**: 強制輸出高品質的台灣繁體中文摘要。

## 安裝需求 (Requirements)

請確保已安裝 Python 3.8+ 以及以下套件：

```bash
pip install requests feedparser faster-whisper google-genai nvidia-ml-py
```

此外，你需要一組 Google Gemini API Key。

## 設定 (Configuration)

在執行 `correct.py` 與 `summarize.py` 之前，請設定環境變數 `GEMINI_API_KEY`：

```bash
export GEMINI_API_KEY="your_api_key_here"
```

或者直接修改腳本中的 `API_KEY` 變數。

## 使用方式 (Usage)

### 1. 下載並處理 Podcast

編輯 `dl_podcast.py` 中的 `target_podcasts` 列表，設定你想下載的節目：

```python
target_podcasts = [
    ("Podcast名稱", "過濾關鍵字", 0), # 0 代表只下載週一的節目
    ("另一個Podcast", "關鍵字"),
]
```

執行下載器：

```bash
python dl_podcast.py
```

腳本會自動執行以下流程：
下載 -> 轉錄 (`fwhisper.py`) -> 校正 (`correct.py`) -> 摘要 (`summarize.py`)

### 2. 單獨使用各個模組

*   **轉錄**: `python fwhisper.py <audio_file>`
*   **校正**: `python correct.py <transcript_file>`
*   **摘要**: `python summarize.py <transcript_file>`
    *   `summarize.py` 會自動讀取同目錄下的 `prompt_template.md` 進行智慧路由。

## 檔案結構

*   `dl_podcast.py`: 主程式，負責下載與串接流程。
*   `fwhisper.py`: 語音轉錄模組。
*   `correct.py`: 錯字校正模組。
*   `summarize.py`: 摘要生成模組 (含動態 Prompt 選擇)。
*   `prompt_template.md`: 存放各種分析風格的 Prompt 範本庫。

## License

Apache License 2.0
