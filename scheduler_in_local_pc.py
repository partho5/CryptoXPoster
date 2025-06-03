import subprocess
import threading
import time
import requests
import datetime

AUTH_CODE = "59bd0119d5fec5ffa3622e196ab5fd10"
BASE_URL = "http://localhost:8080"
POSTING_DELAY_MINUTES = 60*3  # minutes


def call_scrape():
    time.sleep(10)  # wait 1 minute after server starts
    print("Calling /scrape...")
    try:
        requests.get(f"{BASE_URL}/scrape?auth_code={AUTH_CODE}")
    except Exception as e:
        print("Error calling /scrape:", e)


def call_process_loop():
    while True:
        time.sleep(POSTING_DELAY_MINUTES * 60)  # some time gap between posting

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{current_time}] Calling /process...")

        try:
            response = requests.get(f"{BASE_URL}/process?auth_code={AUTH_CODE}")

            # Print response details
            print(f"[{current_time}] Response Status: {response.status_code}")
            print(f"[{current_time}] Response Headers: {dict(response.headers)}")

            # Print response content (truncated if too long)
            response_text = response.text
            if len(response_text) > 500:
                print(f"[{current_time}] Response Body (truncated): {response_text[:500]}...")
            else:
                print(f"[{current_time}] Response Body: {response_text}")

            # Check if response was successful
            if response.status_code == 200:
                print(f"[{current_time}] ✅ Process call successful")
            else:
                print(f"[{current_time}] ⚠️  Process call returned status {response.status_code}")

        except requests.exceptions.RequestException as e:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] ❌ Request Error calling /process: {e}")
        except Exception as e:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{current_time}] ❌ Unexpected Error calling /process: {e}")

        print("-" * 60)  # Separator for readability

def start_server_and_tasks():
    # Start the server
    print("Starting passenger_wsgi.py...")
    server_process = subprocess.Popen(["python", "passenger_wsgi.py"])

    # Start task threads
    threading.Thread(target=call_scrape, daemon=True).start()
    threading.Thread(target=call_process_loop, daemon=True).start()

    # Keep script alive as long as server runs
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("Stopping server...")
        server_process.terminate()


if __name__ == "__main__":
    start_server_and_tasks()
