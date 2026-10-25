from client import RealtimeVoiceCrossTalkSuppressorClient
import math, sys
sys.stdout.reconfigure(encoding='utf-8')

def main():
    suppressor = RealtimeVoiceCrossTalkSuppressorClient()
    print("=== REALTIME VOICE CROSS-TALK SUPPRESSOR ===")
    
    # Scenario 1: Acoustic Echo (Mic input is identical to speaker output with 15-sample room delay)
    speaker_audio = [int(15000.0 * math.sin(i * 0.15)) for i in range(480)]
    echo_mic_audio = [0] * 15 + speaker_audio[:465]
    res_echo = suppressor.evaluate_barge_in(echo_mic_audio, speaker_audio)
    print()
    print(f"1. Acoustic Echo: Corr={res_echo['cross_correlation_index']} | State={res_echo['conversational_state']}")
    print(f"   Action: {res_echo['recommended_agent_action']}")

    # Scenario 2: User Barge-in (User speaks while agent is speaking at different frequency)
    user_interruption = [int(22000.0 * math.sin(i * 0.45)) for i in range(480)]
    res_bargein = suppressor.evaluate_barge_in(user_interruption, speaker_audio)
    print()
    print(f"2. User Interruption: Corr={res_bargein['cross_correlation_index']} | State={res_bargein['conversational_state']}")
    print(f"   Action: {res_bargein['recommended_agent_action']}")

if __name__ == "__main__":
    main()
