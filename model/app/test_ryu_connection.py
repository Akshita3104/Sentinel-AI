import requests

RYU_IP = "10.190.169.7"
RYU_PORT = 8080

try:
    # test the Ryu switch list API
    url = f"http://{RYU_IP}:{RYU_PORT}/stats/switches"
    print(f"Testing Ryu Controller at {url}")

    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        print("✅ Successfully connected to Ryu Controller!")
        print("Switches:", response.json())
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
