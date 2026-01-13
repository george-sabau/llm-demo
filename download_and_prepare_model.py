import os
import urllib.request
import gzip
import shutil
import sys
import time

# --- KONFIGURATION ---
BASE_MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.de.300.bin.gz"
PROJECT_DIR = "fasttext_project"

# Global variable to track start time
start_time = None

def progress_report(block_num, block_size, total_size):
    global start_time
    if start_time is None:
        start_time = time.time()

    downloaded = block_num * block_size
    elapsed_time = time.time() - start_time

    # Avoid division by zero
    if elapsed_time > 0:
        speed = downloaded / elapsed_time  # Bytes per second
    else:
        speed = 0

    if total_size > 0:
        percent = downloaded * 100 / total_size
        remaining_bytes = total_size - downloaded

        # Estimate remaining time (ETA)
        if speed > 0:
            eta_seconds = remaining_bytes / speed
            eta_str = time.strftime("%M:%S", time.gmtime(eta_seconds))
        else:
            eta_str = "--:--"

        # Format output
        msg = (f"\rProgress: {percent:6.2f}% | "
               f"{downloaded / 1024**2:7.1f} / {total_size / 1024**2:7.1f} MB | "
               f"Speed: {speed / 1024**2:5.2f} MB/s | "
               f"ETA: {eta_str}")

        sys.stdout.write(msg)
        sys.stdout.flush()

def download_and_prepare():
    root_dir = os.getcwd()
    base_gz = os.path.join(root_dir, "cc.de.300.bin.gz")
    base_bin = os.path.join(root_dir, "cc.de.300.bin")

    if not os.path.exists(base_bin):
        if not os.path.exists(base_gz):
            print(f"Starting Download of Facebook Base Model...")
            try:
                urllib.request.urlretrieve(BASE_MODEL_URL, base_gz, reporthook=progress_report)
                print("\n\nDownload Complete.")
            except Exception as e:
                print(f"\nDownload Error: {e}")
                return

        print(f"Decompressing {base_gz} into 3+1 dimensional space...")
        with gzip.open(base_gz, 'rb') as f_in:
            with open(base_bin, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print("Extraction complete.")

        # Remove the .gz file immediately after successful extraction
        if os.path.exists(base_gz):
            print(f"Removing compressed file {base_gz} to save space...")
            os.remove(base_gz)

    # Manage directories
    if not os.path.exists(PROJECT_DIR):
        os.makedirs(PROJECT_DIR)

    print(f"\nSuccess! Base model is ready at: {base_bin}")

if __name__ == "__main__":
    download_and_prepare()