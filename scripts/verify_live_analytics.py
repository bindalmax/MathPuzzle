import requests
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:5005"

def verify_live_analytics():
    print(f"--- Starting Live Analytics Test against {BASE_URL} ---")

    # 1. Setup Session
    session = requests.Session()
    # Bypass verification for self-signed cert
    session.verify = False 

    player_name = f"TestPlayer_{int(time.time())}"

    # Create game
    payload = {
        "player_name": player_name,
        "category": "percentage",
        "difficulty": "medium",
        "game_type": "single"
    }

    print(f"Registering player: {player_name}")
    session.post(f"{BASE_URL}/", data=payload)

    # 2. Play a few games to generate data
    print("Simulating game answers...")
    for i in range(3):
        session.post(f"{BASE_URL}/submit_answer", data={"answer": "0"})
        print(f"Submitted answer {i+1}")

    # 3. Check Analytics
    print("Fetching analytics...")
    resp = session.get(f"{BASE_URL}/analytics")

    if resp.status_code == 200:
        print("✅ Analytics page loaded successfully.")
        if "Progress" in resp.text:
            print("✅ Dashboard content verified.")
        else:
            print("⚠️ Dashboard loaded, but expected headers not found.")
    else:
        print(f"❌ Failed to load analytics (Status {resp.status_code})")


if __name__ == "__main__":
    try:
        verify_live_analytics()
    except Exception as e:
        print(f"❌ Test failed: {e}")
