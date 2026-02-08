"""Check Synthia's memory after calls."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'master.env'), override=True)

from services.memory import get_memory_store

mem = get_memory_store()
print("=== Memory Stats ===")
print(mem.stats())
print()

clients = mem.list_clients()
for c in clients:
    cid = c["client_id"]
    name = c.get("name", "Unknown")
    lang = c.get("language", "?")
    print(f"Client: {name} ({cid}) lang={lang}")

    history = mem.get_all_history(cid)
    if history:
        print(f"  Messages: {len(history)}")
        for msg in history[-10:]:
            role = msg["role"]
            text = msg["content"][:150]
            print(f"    [{role}] {text}")

    facts = mem.get_facts(cid)
    if facts:
        print(f"  Facts: {len(facts)}")
        for f in facts:
            print(f"    [{f['category']}] {f['fact']}")
    print()
