import requests
import time
import json

URL = "http://127.0.0.1:11434/api/generate"

payload = {
    "model": "phi3:mini",
    "prompt": "Say hello in one short sentence.",
    "stream": True,
    "options": {
        "num_predict": 10
    }
}

start = time.time()

print("Sending request...")

response = requests.post(
    URL,
    json=payload,
    stream=True,
    timeout=(5, 120),
)

print("HTTP STATUS:", response.status_code)
print("Connected in:", round(time.time() - start, 2), "seconds")
print()
print("JARVIS STREAM:")

full_response = ""

for line in response.iter_lines():

    if not line:
        continue

    data = json.loads(line.decode("utf-8"))

    token = data.get("response", "")

    if token:
        print(token, end="", flush=True)
        full_response += token

    if data.get("done"):
        break

print()
print()
print("Total time:", round(time.time() - start, 2), "seconds")
print("Final response:", full_response)