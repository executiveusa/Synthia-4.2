"""
Synthia 4.2 - Launch voice server + tunnel + call

Single script that:
1. Starts the FastAPI voice server on port 8002
2. Opens a localtunnel
3. Places a Twilio call with bidirectional media stream
"""
import os, sys, time, threading, subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from dotenv import load_dotenv
env_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(env_dir, '.env'))
load_dotenv(os.path.join(env_dir, 'master.env'), override=True)

PORT = 8002
TO_NUMBER = sys.argv[1] if len(sys.argv) > 1 else "+13234842914"

# Verify keys
for key in ["ELEVEN_LABS_API", "OPENAI_API_KEY", "ANTHROPIC_API_KEY_2", "TWILIO_ACCOUNT_SID"]:
    val = os.getenv(key, "")
    status = f"...{val[-8:]}" if val else "MISSING!"
    print(f"  {key}: {status}")

print(f"\n1/3 Starting voice server on :{PORT}...")

def start_server():
    import uvicorn
    from services.voice_server import app
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    server.run()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
time.sleep(3)

# Verify server is up
import httpx
try:
    r = httpx.get(f"http://localhost:{PORT}/health", timeout=5)
    print(f"  Server health: {r.json()['status']}")
except Exception as e:
    print(f"  Server failed to start: {e}")
    sys.exit(1)

print("\n2/3 Opening tunnel...")

# Start localtunnel as subprocess and capture URL
lt_proc = subprocess.Popen(
    "npx localtunnel --port " + str(PORT),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    shell=True,
)

tunnel_url = None
for _ in range(30):  # Wait up to 30 seconds
    line = lt_proc.stdout.readline()
    if line:
        line = line.strip()
        print(f"  lt: {line}")
        if "https://" in line:
            # Extract URL
            parts = line.split()
            for part in parts:
                if part.startswith("https://"):
                    tunnel_url = part.rstrip("/")
                    break
            if tunnel_url:
                break
    time.sleep(0.5)

if not tunnel_url:
    print("  Tunnel failed to start!")
    sys.exit(1)

print(f"  Tunnel: {tunnel_url}")
os.environ["VOICE_WEBHOOK_URL"] = tunnel_url

print(f"\n3/3 Calling {TO_NUMBER}...")

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
api_key = os.getenv("TWILIO_API_KEY_SID")
api_secret = os.getenv("TWILIO_API_KEY_SECRET")
from_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(api_key, api_secret, account_sid)

response = VoiceResponse()
response.say(
    "Connecting you to Synthia from The Pauli Effect. One moment.",
    voice="Polly.Joanna",
)
response.pause(length=1)
connect = Connect()
ws_url = tunnel_url.replace("https://", "wss://").replace("http://", "ws://")
stream = Stream(url=f"{ws_url}/ws/twilio-stream")
stream.parameter(name="callerNumber", value=TO_NUMBER)
connect.append(stream)
response.append(connect)

twiml = str(response)
print(f"\n  TwiML: {twiml[:200]}...")

call = client.calls.create(twiml=twiml, to=TO_NUMBER, from_=from_number)
print(f"\n  CALL PLACED! SID: {call.sid}")
print(f"  {from_number} -> {TO_NUMBER}")
print(f"  Brain: Claude Sonnet 4 | Memory: persistent | Languages: en/es/hi")
print(f"\n  Press Ctrl+C to shut down.\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    lt_proc.kill()
