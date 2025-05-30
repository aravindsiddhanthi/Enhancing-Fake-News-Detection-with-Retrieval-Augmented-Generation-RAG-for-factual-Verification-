import subprocess
import time
import datetime

def run_scripts():
    print(f"[{datetime.datetime.now()}] Running scrapers...")

    try:
        # subprocess.run([r"C:\Users\snoorhasan\Downloads\MyLearning\ChatBot\v2_venv\Scripts\python.exe", "test.py"], check=True)
        subprocess.run(["venv/Scripts/python.exe", "factcheck_scraper.py"], check=True)
        subprocess.run(["venv/Scripts/python.exe", "politifact_scraper.py"], check=True)
        subprocess.run(["venv/Scripts/python.exe", "train_model.py"], check=True)
        # subprocess.run(["python", "politifact_scraper.py"], check=True)
        print("Scrapers executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running scripts: {e}")

if __name__ == "__main__":
    while True:
        run_scripts()
        print("Waiting 5 minutes...\n")
        time.sleep(300)  # 5 minutes = 300 seconds
