import sys, json
from client import RealtimeVoiceCrossTalkSuppressorClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    suppressor = RealtimeVoiceCrossTalkSuppressorClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-realtime-voice-cross-talk-suppressor-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    mic = req.get("mic_samples", [0] * 320)
    ref = req.get("ref_samples", [0] * 320)
    res = suppressor.evaluate_barge_in(mic, ref)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
