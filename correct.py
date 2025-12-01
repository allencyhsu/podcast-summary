import os
import sys
from google import genai
from google.genai import types

# --- Configuration ---
# 請在此填入您的 API Key，或是設定環境變數 GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY") or "your_api_key"

# 請在此填入您的提示詞 (Prompt)
HOTWORDS = [
    "陳鳳馨", "郝哥"
]

PROMPT = f"""
# Role
你是一位精通繁體中文（台灣用語）的專業編輯，擅長校對語音轉錄的文字稿。

# Task
請閱讀提供的 Podcast 逐字稿，修正其中的錯別字與同音異字。

# Critical Instruction (Hotwords)
以下是用戶提供的正確專有名詞列表（Hotwords）。**請務必強制使用這些詞彙**。
如果你在文中發現與這些 Hotwords 發音相似或意思相近的詞（例如同音錯字），**必須**將其修正為列表中的正確寫法。

Hotwords 列表：
{{', '.join(HOTWORDS)}}

# Examples of Corrections
- 錯字：「陳鳳心」 -> 修正：「陳鳳馨」 (因為 "陳鳳馨" 在 Hotwords 列表中)
- 錯字：「好哥」 -> 修正：「郝哥」 (因為 "郝哥" 在 Hotwords 列表中)

# Constraints
1. **保持原意**：不要刪減或改寫內容，僅修正錯字。
2. **保留時間軸**：如果原文有時間軸（例如 [00:00.00]），請務必保留。
3. **輸出格式**：直接輸出修正後的全文，不需要任何開場白或結語。

# Input Text
"""

# Max characters per chunk (approx 30k-40k tokens depending on language, setting safe limit)
# User mentioned 50k tokens limit. 
# For Chinese, 1 char ~ 1 token. For English 1 token ~ 4 chars.
# 30,000 chars should be safe for < 50k tokens including prompt.
CHUNK_SIZE = 30000

def split_text_by_lines(text, max_chars=CHUNK_SIZE):
    """
    Splits text into chunks by lines, ensuring each chunk is under max_chars.
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1 # +1 for newline
        if current_length + line_len > max_chars:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_len
        else:
            current_chunk.append(line)
            current_length += line_len
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks

def correct_transcript(file_path):
    """
    Corrects typos in the transcript file using the Gemini API.
    """
    # Check if API key is set
    if not API_KEY or API_KEY == "your_api_key":
        print("Error: API Key not set. Please set API_KEY in correct.py or as an environment variable GEMINI_API_KEY")
        return

    base_name = os.path.splitext(file_path)[0]
    output_file = f"{base_name}_corrected.txt"

    if os.path.exists(output_file):
        print(f"校正後的檔案已存在，跳過: {output_file}")
        return output_file

    print(f"正在讀取文字稿: {file_path} ...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"讀取檔案失敗: {e}")
        return None

    print("正在呼叫 Gemini API 進行校正...")
    try:
        client = genai.Client(api_key=API_KEY)
        
        chunks = split_text_by_lines(content)
        corrected_chunks = []
        
        print(f"內容過長，將分為 {len(chunks)} 個片段處理...")

        for i, chunk in enumerate(chunks):
            print(f"  正在處理片段 {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            
            # 組合 Prompt 與內容
            full_prompt = PROMPT + "\n" + chunk
            
            response = client.models.generate_content(
                model='gemini-2.5-pro',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )
            
            corrected_chunks.append(response.text)
        
        corrected_text = "\n".join(corrected_chunks)
        
        # 儲存校正後的文字稿
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(corrected_text)
            
        print(f"校正完成: {output_file}")
        return output_file

    except Exception as e:
        print(f"Gemini API 呼叫失敗: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python correct.py <transcript_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    correct_transcript(file_path)
