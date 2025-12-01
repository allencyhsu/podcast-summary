import requests
import feedparser
import os
import re
import subprocess
import sys

def get_itunes_feed_url(term):
    """
    利用 iTunes Search API 搜尋 Podcast 並取得 RSS Feed URL
    """
    search_url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "media": "podcast",
        "entity": "podcast",
        "limit": 1
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["resultCount"] == 0:
            print(f"找不到節目: {term}")
            return None
            
        # 取得第一個搜尋結果的 feedUrl
        feed_url = data["results"][0]["feedUrl"]
        collection_name = data["results"][0]["collectionName"]
        print(f"找到節目: {collection_name}")
        return feed_url
    except Exception as e:
        print(f"搜尋錯誤: {e}")
        return None

def sanitize_filename(filename):
    """
    移除檔名中的非法字元 (如 / : * ? " < > |)
    """
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_latest_episodes(feed_url, num_episodes=3, save_dir="downloads", keyword=None, target_weekday=None):
    """
    解析 RSS 並下載最新 N 集
    """
    if not feed_url:
        return

    # 解析 RSS
    print(f"正在解析 RSS: {feed_url} ...")
    feed = feedparser.parse(feed_url)
    
    # 建立儲存資料夾
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 取得最新 N 集 (feed.entries 通常是按時間排序的，最新的在最前面)
    all_episodes = feed.entries
    episodes_to_process = all_episodes

    if keyword:
        print(f"正在篩選包含關鍵字 '{keyword}' 的單集...")
        episodes_to_process = [ep for ep in episodes_to_process if keyword in ep.title]
        if not episodes_to_process:
            print(f"  [提示] 找不到包含關鍵字 '{keyword}' 的單集")
            return

    if target_weekday is not None:
        print(f"正在篩選星期 {target_weekday} (0=週一) 的單集...")
        # published_parsed is a time.struct_time, tm_wday is 0-6 (Monday is 0)
        episodes_to_process = [ep for ep in episodes_to_process if ep.get('published_parsed') and ep.published_parsed.tm_wday == target_weekday]
        if not episodes_to_process:
            print(f"  [提示] 找不到符合星期 {target_weekday} 的單集")
            return

    episodes = episodes_to_process[:num_episodes]

    for i, ep in enumerate(episodes):
        title = ep.title
        safe_title = sanitize_filename(title)
        
        # 尋找音檔連結 (通常在 enclosures 裡)
        audio_url = None
        for link in ep.enclosures:
            if link.type.startswith("audio"):
                audio_url = link.href
                break
        
        if not audio_url:
            print(f"  [跳過] 找不到音檔連結: {title}")
            continue

        # 決定副檔名 (通常是 mp3 或 m4a)
        ext = "mp3"
        if "m4a" in audio_url:
            ext = "m4a"
            
        filename = f"{save_dir}/{safe_title}.{ext}"
        
        # 檢查是否已存在部分檔案
        resume_header = {}
        mode = 'wb'
        existing_size = 0
        
        if os.path.exists(filename):
            existing_size = os.path.getsize(filename)
            if existing_size > 0:
                resume_header = {'Range': f'bytes={existing_size}-'}
                print(f"  [續傳] 偵測到既有檔案 ({existing_size} bytes)，嘗試續傳...")

        # 開始下載
        print(f"  [{i+1}/{num_episodes}] 下載中: {title}")
        try:
            with requests.get(audio_url, headers=resume_header, stream=True) as r:
                # 處理 416 Range Not Satisfiable (通常代表已下載完成)
                if r.status_code == 416:
                    print(f"     -> 檔案似乎已完整下載，跳過下載步驟。")
                
                else:
                    # 檢查是否支援續傳 (206 Partial Content)
                    if r.status_code == 206:
                        mode = 'ab'
                        print(f"     -> 伺服器支援續傳，從 {existing_size} bytes 開始")
                    elif r.status_code == 200:
                        # 如果伺服器不支援續傳 (回傳 200)，則必須重頭下載
                        if existing_size > 0:
                            print(f"     -> 伺服器不支援續傳 (回傳 200)，重新下載")
                        mode = 'wb'
                    else:
                        r.raise_for_status()

                    with open(filename, mode) as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"     -> 下載完成")

            # 呼叫 fwhisper.py 進行轉錄
            fwhisper_script = "fwhisper.py"
            if os.path.exists(fwhisper_script):
                print(f"     -> 開始轉錄: {filename}")
                try:
                    subprocess.run([sys.executable, fwhisper_script, filename], check=True)
                    print(f"     -> 轉錄完成")
                    
                    txt_filename = os.path.splitext(filename)[0] + ".txt"

                    # 呼叫 correct.py 進行校正
                    correct_script = "correct.py"
                    corrected_filename = os.path.splitext(filename)[0] + "_corrected.txt"
                    
                    if os.path.exists(correct_script) and os.path.exists(txt_filename):
                        print(f"     -> 開始校正: {txt_filename}")
                        try:
                            subprocess.run([sys.executable, correct_script, txt_filename], check=True)
                            print(f"     -> 校正完成")
                            # 如果校正成功，使用校正後的檔案進行摘要
                            if os.path.exists(corrected_filename):
                                txt_filename = corrected_filename
                        except subprocess.CalledProcessError as e:
                            print(f"     -> 校正失敗: {e}")

                    # 呼叫 summarize.py 進行摘要
                    summarize_script = "summarize.py"
                    
                    if os.path.exists(summarize_script) and os.path.exists(txt_filename):
                        print(f"     -> 開始摘要: {txt_filename}")
                        try:
                            subprocess.run([sys.executable, summarize_script, txt_filename], check=True)
                            print(f"     -> 摘要完成")
                        except subprocess.CalledProcessError as e:
                            print(f"     -> 摘要失敗: {e}")
                    
                except subprocess.CalledProcessError as e:
                    print(f"     -> 轉錄失敗: {e}")
            else:
                print(f"     -> 找不到 {fwhisper_script}，跳過轉錄")

        except Exception as e:
            print(f"     -> 下載失敗: {e}")

# --- 主程式執行區 ---
if __name__ == "__main__":
    # 你想要抓取的節目名稱列表
    target_podcasts = [
        # "Y Combinator Startup Podcast",
        # "a16z Podcast",
        # "Lex Fridman Podcast",
        # "Soft & Share 軟體開發資訊分享",
        # ("馨天地", "陳鳳馨 ╳ 馮勃翰", 0), # 0 = Monday
        ("馨天地", "經濟學人"),
        # ("馨天地", "醒醒腦！科學")
    ]

    for item in target_podcasts:
        keyword = None
        target_weekday = None
        
        if isinstance(item, tuple):
            if len(item) == 2:
                podcast_name, keyword = item
            elif len(item) == 3:
                podcast_name, keyword, target_weekday = item
        else:
            podcast_name = item

        print(f"\n=== 處理 Podcast: {podcast_name} (關鍵字: {keyword}, 星期: {target_weekday}) ===")
        
        # 搜尋 Podcast
        feed_url = get_itunes_feed_url(podcast_name)
        
        if feed_url:
            # 下載最新單集
            # 建立專屬資料夾
            # Use sanitize_filename for the directory name to avoid issues with special characters
            save_dir = f"podcasts/{sanitize_filename(podcast_name)}"
            download_latest_episodes(feed_url, num_episodes=1, save_dir=save_dir, keyword=keyword, target_weekday=target_weekday)
        
        print("\n" + "="*30 + "\n")