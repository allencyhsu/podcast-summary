import os
import sys
import os
import sys
from google import genai
from google.genai import types

# --- Configuration ---
# 請在此填入您的 API Key，或是設定環境變數 GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY") or "your_api_key"

# 請在此填入您的提示詞 (Prompt)
PROMPT = """
# Role
你是一位精通矽谷科技生態與前沿技術的資深分析師。你具備極強的邏輯歸納能力，擅長從雜亂的口語對話中提煉出高價值的技術報告。

# Task
請分析提供的 Podcast 內容，撰寫一份深度技術報告。

# Language & Tone
- **語言**：繁體中文（台灣用語）。請注意術語轉換（例如：Software -> 軟體, Project -> 專案, Information -> 資訊, Optimization -> 最佳化, Interface -> 介面）。
- **語氣**：專業、客觀、深度，避免行銷術語或過度修飾。

# Output Structure
請依照以下 Markdown 格式輸出：

## 1. 核心論述 (The One Thing)
用一段精煉的文字（約 100 字）闡述這集 Podcast 試圖傳達的最重要概念或技術突破。

## 2. 關鍵技術與概念拆解 (Technical Deep Dive)
針對對話中提到的 3-5 個核心技術或概念進行深度解析。
- **概念名稱**：(中英對照)
- **原理/定義**：講者是如何解釋這個概念的？
- **應用場景**：這項技術解決了什麼具體問題？
- **Gemini 補充**：(請利用你的知識庫，用一句話補充這個概念在目前市場上的其他競爭技術)

## 3. 非共識觀點 (Contrarian Views)
找出講者提出的「反直覺」或「挑戰主流看法」的觀點。
- **主流觀點**：大眾通常怎麼想？
- **講者觀點**：講者為什麼反對？他的論據是什麼？

## 4. 市場預測與時間軸 (Future Outlook)
整理講者對於未來 1 年、5 年、10 年的預測。請區分「確定性高」的趨勢與「賭注性質」的預測。

## 5. 精彩問答摘要 (Q&A Highlights)
挑選 3 個最犀利的問題與回答，以「Q: ... / A: ...」的方式呈現精華。

## 6. 延伸思考題 (Reflection)
基於內容，提出 2 個值得讀者深入思考的開放性問題。

# Input Data
"""
# ---------------------

def summarize_transcript(file_path):
    if not os.path.exists(file_path):
        print(f"找不到檔案: {file_path}")
        return

    if API_KEY == "YOUR_API_KEY_HERE":
        print("錯誤: 請先設定 API Key (在 summarize.py 中設定或是環境變數 GEMINI_API_KEY)")
        return

    base_name = os.path.splitext(file_path)[0]
    output_file = f"{base_name}_summary.md"

    if os.path.exists(output_file):
        print(f"摘要檔案已存在，跳過: {output_file}")
        return

    print(f"正在讀取文字稿: {file_path} ...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"讀取檔案失敗: {e}")
        return

    print("正在呼叫 Gemini API 進行摘要...")
    try:
        client = genai.Client(api_key=API_KEY)
        
        # 組合 Prompt 與內容
        full_prompt = PROMPT + "\n" + content
        
        # 避免 token 數過多，這裡可以做簡單的長度檢查或截斷 (視情況而定)
        # 簡單截斷範例 (Gemini 1.5 Flash context window 很大，通常不需要太擔心，但以防萬一)
        # full_prompt = full_prompt[:1000000] 

        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3
            )
        )
        
        summary = response.text
        
        # 儲存摘要
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"摘要完成! 已儲存至: {output_file}")
        
    except Exception as e:
        print(f"摘要產生失敗: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方式: python3 summarize.py <transcript_file>")
    else:
        target_file = sys.argv[1]
        summarize_transcript(target_file)
