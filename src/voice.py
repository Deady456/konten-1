import asyncio
import os
import time
from pathlib import Path
import edge_tts
from .config import CONFIG
from elevenlabs.client import ElevenLabs


# ============================================================
# Voice Variety System
# ============================================================

def _get_voice_config() -> dict:
    """Get voice config with variety support."""
    cfg = CONFIG.get("voice", {})
    variety = cfg.get("variety", {})

    if variety.get("enabled", False):
        voices = variety.get("voices", [])
        strategy = variety.get("strategy", "round_robin")

        if voices:
            voice = _select_voice(voices, strategy)
            return {
                **cfg,
                "voice": voice["id"],
                "elevenlabs_voice_id": voice.get("elevenlabs_id"),
                "_voice_name": voice.get("name"),
                "_voice_gender": voice.get("gender"),
            }

    return cfg


def _select_voice(voices: list[dict], strategy: str) -> dict:
    """Select voice based on strategy."""
    from . import state

    s = state.load()
    voice_idx = s.get("_voice_idx", 0)

    if strategy == "round_robin":
        selected = voices[voice_idx % len(voices)]
        state.update({"_voice_idx": voice_idx + 1})
    elif strategy == "random":
        import random
        selected = random.choice(voices)
    else:
        selected = voices[voice_idx % len(voices)]
        state.update({"_voice_idx": voice_idx + 1})

    print(f"    voice: selected {selected.get('name', 'unknown')} ({selected.get('gender', '?')})")
    return selected


# ============================================================
# TTS Synthesis
# ============================================================

def _synth_edge(text: str, out_path: Path, v: dict) -> None:
    async def _go():
        com = edge_tts.Communicate(
            text,
            voice=v["voice"],
            rate=v.get("rate", "+0%"),
            pitch=v.get("pitch", "+0Hz"),
        )
        await com.save(str(out_path))
    asyncio.run(_go())


def _synth_elevenlabs(text: str, out_path: Path, v: dict, api_key: str) -> None:
    client = ElevenLabs(api_key=api_key)
    audio = client.text_to_speech.convert(
        voice_id=v.get("elevenlabs_voice_id", "3mAVBNEqop5UbHtD8oxQ"),
        text=text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    with open(out_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)


def synth(text: str, out_path: Path) -> Path:
    v = _get_voice_config()
    provider = v.get("provider", "edge-tts")
    voice_name = v.get("_voice_name", v["voice"])
    print(f"    voice: {voice_name}, {len(text)} chars, provider: {provider}")

    t0 = time.time()

    if provider == "elevenlabs":
        keys_str = os.environ.get("ELEVENLABS_API_KEYS", "")
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]

        if keys:
            for i, api_key in enumerate(keys):
                try:
                    _synth_elevenlabs(text, out_path, v, api_key)
                    print(f"    done in {time.time()-t0:.1f}s (elevenlabs key[{i}])")
                    return out_path
                except Exception as e:
                    print(f"    key[{i}] failed: {e}, trying next")
                    continue
            print(f"    all elevenlabs keys failed, falling back to edge-tts")
        else:
            print(f"    no elevenlabs keys set, falling back to edge-tts")

    _synth_edge(text, out_path, v)
    print(f"    done in {time.time()-t0:.1f}s (edge-tts)")
    return out_path
