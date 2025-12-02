import os
import time
start_time = time.time()

import pynvml

def get_optimal_device():
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        best_device_index = 0
        max_free_memory = 0

        print(f"Found {device_count} GPUs.")

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            free_memory_mb = mem_info.free / 1024 / 1024
            print(f"GPU {i}: {free_memory_mb:.2f} MB free")

            if free_memory_mb > max_free_memory:
                max_free_memory = free_memory_mb
                best_device_index = i
        
        pynvml.nvmlShutdown()
        print(f"Selected GPU {best_device_index} with {max_free_memory:.2f} MB free memory.")
        return best_device_index
    except Exception as e:
        print(f"Error detecting GPU memory: {e}. Defaulting to GPU 0.")
        return 0

from faster_whisper import WhisperModel

model_size = "large-v2"
# model_size = "deepdml/faster-whisper-large-v3-turbo-ct2"
device_index = get_optimal_device()
model = WhisperModel(model_size, device="cuda", device_index=device_index, compute_type="float16")
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# model = WhisperModel(model_size, device="cuda", device_index=1, compute_type="float32")

prompt = "播客內容"

words = [
    "伯樂"
]
hwords = ", ".join(words)

import sys

def transcribe_file(file_path, model, prompt, hwords):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    txt_filename = os.path.splitext(file_path)[0] + ".txt"
    
    # Check if the corresponding .txt file already exists
    if os.path.exists(txt_filename):
        print(f"Skipping {file_path} (corresponding .txt file already exists)\r\n")
        print(f"Output file: {txt_filename}")
        return

    trans_start_time = time.time()

    segments, info = model.transcribe(
        file_path,
        # language="zh",
        # multilingual=True,
        initial_prompt=prompt,
        temperature=0.0,
        vad_filter=True,
        vad_parameters = dict(min_silence_duration_ms=500, min_speech_duration_ms=150, max_speech_duration_s=15),
        repetition_penalty=1.1,
        beam_size=10,
        hotwords=hwords
    )

    print(f"File: {file_path}")
    # print(info)

    with open(txt_filename, "w", encoding="utf-8") as txt_file:
        for segment in segments:
            # print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
            txt_file.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")

    print()  # Print an empty line for better readability

    trans_end_time = time.time()
    trans_execution_time = trans_end_time - trans_start_time
    print(f"Transcribe time: {trans_execution_time:.2f} seconds\r\n")
    print(f"Output file: {txt_filename}")

# Specify the directory containing the mp3 files
directory = "."
extensions = (".m4a", ".mp3")

if len(sys.argv) > 1:
    target_file = sys.argv[1]
    transcribe_file(target_file, model, prompt, hwords)
else:
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        # Check if the file has the mp3 extension
        if filename.endswith(extensions):
            file_path = os.path.join(directory, filename)
            transcribe_file(file_path, model, prompt, hwords)

end_time = time.time()
execution_time = end_time - start_time
print(f"Total execution time: {execution_time:.2f} seconds\r\n")