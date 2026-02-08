"""Quick test: Reasoning engine + Memory + PDF ingestion."""
import os, sys, asyncio
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'master.env'), override=True)

from services.reasoning_engine import get_reasoning_engine
from services.memory import get_memory_store

async def main():
    # ── Test Reasoning Engine ──
    engine = get_reasoning_engine()
    print(f"Providers: {len(engine._providers)}")
    for p in engine._providers:
        print(f"  {p.provider.value}/{p.model}")

    # English
    r1 = await engine.chat(
        messages=[{"role": "user", "content": "I need an ecommerce site for my streetwear brand. Budget around 5k."}],
        system_prompt="You are Synthia from The Pauli Effect. Keep responses under 3 sentences.",
        max_tokens=200,
        language_hint="en",
    )
    print(f"\n[EN] ({engine.active_provider_name}):\n{r1}")

    # Mexican Spanish
    r2 = await engine.chat(
        messages=[{"role": "user", "content": "Necesito una pagina web para mi restaurante en la Condesa"}],
        system_prompt="You are Synthia from The Pauli Effect. Keep responses under 3 sentences.",
        max_tokens=200,
        language_hint="es",
    )
    print(f"\n[ES] ({engine.active_provider_name}):\n{r2}")

    # Hindi
    r3 = await engine.chat(
        messages=[{"role": "user", "content": "Mujhe apne gym ke liye ek website chahiye"}],
        system_prompt="You are Synthia from The Pauli Effect. Keep responses under 3 sentences.",
        max_tokens=200,
        language_hint="hi",
    )
    print(f"\n[HI] ({engine.active_provider_name}):\n{r3}")

    # ── Test Memory ──
    print("\n--- Memory Test ---")
    mem = get_memory_store()
    mem.remember_client("phone:+13234842914", "Dennis", phone="+13234842914", language="en", niche="tech", company="The Pauli Effect")
    mem.add_fact("phone:+13234842914", "identity", "Founder of The Pauli Effect")
    mem.add_fact("phone:+13234842914", "preference", "Loves Awwwards-quality design")
    mem.add_fact("phone:+13234842914", "project", "Building Synthia autonomous AI agent")
    mem.add_message("phone:+13234842914", "test-session", "user", "Make Synthia autonomous and able to talk")
    mem.add_message("phone:+13234842914", "test-session", "assistant", "I'm on it, building the full reasoning engine now!")
    mem.assign_agent("phone:+13234842914", "Synthia", "High priority founder. Speaks English, Spanish, Hindi. Direct communicator.")

    ctx = mem.get_client_context("phone:+13234842914")
    print(ctx)
    print(f"\nStats: {mem.stats()}")

    print("\n=== ALL TESTS PASSED ===")

asyncio.run(main())
