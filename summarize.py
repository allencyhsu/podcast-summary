import os
import sys
import re
from google import genai
from google.genai import types

# --- Configuration ---
# 請在此填入您的 API Key，或是設定環境變數 GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY") or "your_api_key"
PROMPT_TEMPLATE_PATH = "prompt_template.md"

def parse_templates(file_path):
    """
    Parses the prompt_template.md file to extract template descriptions and contents.
    """
    if not os.path.exists(file_path):
        print(f"Warning: Prompt template file not found at {file_path}")
        return {}, {}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Extract Template Descriptions from the Table
    # Looking for lines like: | **範本 01** | ... | ... |
    table_pattern = re.compile(r"\|\s*\*\*範本\s*(\d+)\*\*\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|")
    descriptions = {}
    
    for match in table_pattern.finditer(content):
        template_id = match.group(1)
        # Combine "Applicable Type" and "Core Objective" for the AI to understand
        desc_type = match.group(2).replace("<br>", " ").strip()
        desc_objective = match.group(3).strip()
        descriptions[template_id] = f"{desc_type} - {desc_objective}"

    # 2. Extract Template Prompts
    # Looking for sections like: #### 範本 01：... ```markdown ... ```
    prompts = {}
    # Split by "#### 範本" to separate sections
    sections = re.split(r"#### 範本\s*(\d+)[：:]", content)
    
    # The first element is before the first template, so skip it.
    # Then we have pairs of (id, content)
    for i in range(1, len(sections), 2):
        template_id = sections[i]
        section_content = sections[i+1]
        
        # Extract the code block
        code_block_match = re.search(r"```markdown\s*(.*?)\s*```", section_content, re.DOTALL)
        if code_block_match:
            prompts[template_id] = code_block_match.group(1)

    return descriptions, prompts

def determine_best_template(client, content, descriptions):
    """
    Uses Gemini to analyze the content and select the best template.
    """
    # Construct the selection prompt
    options_text = ""
    for tid, desc in descriptions.items():
        if tid == "00": continue # Skip the auto-detect template itself
        options_text += f"- Template {tid}: {desc}\n"

    selection_prompt = f"""
You are an expert content classifier. Your task is to analyze the provided podcast transcript excerpt and select the most appropriate summary template from the list below.

# Available Templates
{options_text}

# Input Transcript (Excerpt)
{content[:5000]} ... (truncated)

# Instructions
1. Analyze the topic, tone, and structure of the transcript.
2. Select the ONE template that best fits the content.
3. Return ONLY the template number (e.g., "01", "07"). Do not output any other text.
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=selection_prompt,
            config=types.GenerateContentConfig(
                temperature=0.1 # Low temperature for deterministic selection
            )
        )
        selected_id = response.text.strip()
        # Handle potential extra text like "Template 01"
        match = re.search(r"(\d+)", selected_id)
        if match:
            return match.group(1)
        return "01" # Default fallback
    except Exception as e:
        print(f"Error selecting template: {e}")
        return "01" # Default fallback

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

    # Load Templates
    print(f"正在讀取 Prompt 範本: {PROMPT_TEMPLATE_PATH} ...")
    descriptions, prompts = parse_templates(PROMPT_TEMPLATE_PATH)
    
    if not prompts:
        print("錯誤: 無法讀取任何 Prompt 範本，請檢查 prompt_template.md")
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
        
        # Smart Routing / Dynamic Selection
        print("正在分析內容以選擇最佳範本...")
        selected_template_id = determine_best_template(client, content, descriptions)
        
        if selected_template_id not in prompts:
            print(f"警告: 選擇的範本 {selected_template_id} 不存在，使用預設範本 01")
            selected_template_id = "01"
            
        selected_prompt = prompts[selected_template_id]
        print(f"已選擇範本: {selected_template_id} ({descriptions.get(selected_template_id, 'Unknown')})")

        # 組合 Prompt 與內容
        full_prompt = selected_prompt + "\n\n# Input Data\n" + content
        
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
