"""
Synthia 4.2 - Live Call Launcher

Starts the voice server, opens a public tunnel, and calls the user.
Synthia answers with full autonomous Claude reasoning, persistent memory,
and multilingual support.

Usage:
    python call_synthia.py               # Call default number (+13234842914)
    python call_synthia.py +123456789    # Call specific number
"""

import os
import sys
import time
import signal
import asyncio
import threading

sys.path.insert(0, os.path.dirname(__file__))

# Load environment
from dotenv import load_dotenv
env_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(env_dir, '.env'))
load_dotenv(os.path.join(env_dir, 'master.env'), override=True)

VOICE_SERVER_PORT = 8002
DEFAULT_CALLEE = "+13234842914"


def start_voice_server():
    """Start the FastAPI voice server in a background thread."""
    import uvicorn
    from services.voice_server import app

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=VOICE_SERVER_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    print(f"🎙️  Voice server starting on port {VOICE_SERVER_PORT}...")
    time.sleep(2)
    return server


def open_tunnel(port: int) -> str:
    """Open a public tunnel to the voice server."""
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(port, "http")
        public_url = tunnel.public_url
        print(f"🌐 Tunnel open: {public_url}")
        return public_url
    except Exception as e:
        print(f"⚠️  Tunnel failed ({e}). Trying localtunnel...")
        # Fallback: try localtunnel via npx
        import subprocess
        proc = subprocess.Popen(
            ["npx", "localtunnel", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(5)
        output = proc.stdout.readline()
        if "url" in output.lower() or "https://" in output:
            url = output.strip().split()[-1]
            print(f"🌐 LocalTunnel open: {url}")
            return url

    print("❌ No tunnel available. Install ngrok: https://ngrok.com/download")
    print("   Or set NGROK_AUTH_TOKEN env var for pyngrok")
    sys.exit(1)


def place_call(to_number: str, webhook_url: str) -> str:
    """Place the outbound call via Twilio with WebSocket media stream."""
    from twilio.rest import Client
    from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    api_key = os.getenv("TWILIO_API_KEY_SID")
    api_secret = os.getenv("TWILIO_API_KEY_SECRET")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if api_key and api_secret:
        client = Client(api_key, api_secret, account_sid)
    else:
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        client = Client(account_sid, auth_token)

    # Build TwiML: short greeting then connect WebSocket for bidirectional audio
    response = VoiceResponse()
    response.say(
        "Connecting you to Synthia, your AI design and strategy partner from The Pauli Effect.",
        voice="Polly.Joanna",
    )
    response.pause(length=1)
    connect = Connect()
    ws_url = webhook_url.replace("https://", "wss://").replace("http://", "ws://")
    stream = Stream(
        url=f"{ws_url}/ws/twilio-stream",
    )
    # Pass caller number as custom parameter
    stream.parameter(name="callerNumber", value=to_number)
    connect.append(stream)
    response.append(connect)

    twiml = str(response)
    print(f"\n📋 TwiML:\n{twiml}\n")

    call = client.calls.create(
        twiml=twiml,
        to=to_number,
        from_=from_number,
    )
    print(f"📞 Call placed! SID: {call.sid}")
    print(f"   From: {from_number} → To: {to_number}")
    return call.sid


def main():
    to_number = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CALLEE

    print("═" * 60)
    print("  SYNTHIA 4.2 — AUTONOMOUS VOICE AGENT")
    print("  The Pauli Effect | Mexico City")
    print("═" * 60)
    print(f"\n🎯 Target: {to_number}")
    print(f"🧠 Brain: Claude Sonnet 4 (with fallback chain)")
    print(f"🗣️  Languages: English, Mexican Spanish, Hindi")
    print(f"💾 Memory: Persistent (SQLite)")
    print()

    # 1. Start voice server
    server = start_voice_server()

    # 2. Open tunnel
    public_url = open_tunnel(VOICE_SERVER_PORT)

    # Update env so TwilioService knows the webhook URL
    os.environ["VOICE_WEBHOOK_URL"] = public_url

    # 3. Place the call
    print(f"\n🔥 Calling {to_number}...")
    call_sid = place_call(to_number, public_url)

    print(f"\n✅ Synthia is on the line! (Call: {call_sid})")
    print("   She has Claude Sonnet 4 reasoning, persistent memory,")
    print("   and speaks English, Mexican Spanish (CDMX), and Hindi.")
    print("\n   Press Ctrl+C to shut down.\n")

    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except Exception:
            pass


if __name__ == "__main__":
    main()
