"""Place a live Synthia call with full bidirectional WebSocket media stream."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
env_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(env_dir, '.env'))
load_dotenv(os.path.join(env_dir, 'master.env'), override=True)

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

TUNNEL_URL = "https://calm-rings-dance.loca.lt"
TO_NUMBER = sys.argv[1] if len(sys.argv) > 1 else "+13234842914"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
api_key = os.getenv("TWILIO_API_KEY_SID")
api_secret = os.getenv("TWILIO_API_KEY_SECRET")
from_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(api_key, api_secret, account_sid)

# Build TwiML with bidirectional WebSocket stream
response = VoiceResponse()
response.say(
    "Connecting you to Synthia, your AI design and strategy partner from The Pauli Effect.",
    voice="Polly.Joanna",
)
response.pause(length=1)
connect = Connect()
ws_url = TUNNEL_URL.replace("https://", "wss://").replace("http://", "ws://")
stream = Stream(url=f"{ws_url}/ws/twilio-stream")
stream.parameter(name="callerNumber", value=TO_NUMBER)
connect.append(stream)
response.append(connect)

twiml = str(response)
print(f"TwiML:\n{twiml}\n")

call = client.calls.create(
    twiml=twiml,
    to=TO_NUMBER,
    from_=from_number,
)
print(f"Call placed! SID: {call.sid}")
print(f"From: {from_number} -> To: {TO_NUMBER}")
print(f"Tunnel: {TUNNEL_URL}")
print("Synthia will greet you with Claude Sonnet 4 reasoning.")
