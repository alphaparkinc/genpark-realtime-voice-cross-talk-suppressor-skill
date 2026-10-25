import math, sys
sys.stdout.reconfigure(encoding='utf-8')

class RealtimeVoiceCrossTalkSuppressorClient:
    """
    Full-duplex voice conversational cross-talk and echo suppressor.
    Computes normalized cross-correlation (NCC) between microphone input and speaker playback
    to distinguish genuine user barge-in speech from acoustic echo.
    """
    def __init__(self, echo_correlation_threshold=0.65, min_bargein_energy_db=-32.0):
        self.echo_thresh = echo_correlation_threshold
        self.min_bargein_energy_db = min_bargein_energy_db

    def compute_energy_db(self, samples):
        if not samples:
            return -100.0
        rms = math.sqrt(sum(x * x for x in samples) / float(len(samples)))
        return 20.0 * math.log10(max(1e-5, rms / 32767.0))

    def compute_normalized_cross_correlation(self, mic_samples, ref_speaker_samples, max_lag=80):
        # Reference speaker playback and microphone input correlation
        n = min(len(mic_samples), len(ref_speaker_samples))
        if n == 0:
            return 0.0

        sum_mic_sq = sum(mic_samples[i] * mic_samples[i] for i in range(n))
        sum_ref_sq = sum(ref_speaker_samples[i] * ref_speaker_samples[i] for i in range(n))
        
        denom = math.sqrt(sum_mic_sq * sum_ref_sq)
        if denom == 0.0:
            return 0.0

        max_corr = 0.0
        for lag in range(0, min(max_lag, n // 2)):
            corr = sum(mic_samples[i] * ref_speaker_samples[i - lag] for i in range(lag, n))
            norm_corr = abs(corr) / denom
            if norm_corr > max_corr:
                max_corr = norm_corr

        return min(1.0, max_corr)

    def evaluate_barge_in(self, mic_frame, speaker_ref_frame):
        mic_db = self.compute_energy_db(mic_frame)
        ref_db = self.compute_energy_db(speaker_ref_frame)
        
        correlation = self.compute_normalized_cross_correlation(mic_frame, speaker_ref_frame)

        # Decision rules
        is_speaker_active = ref_db >= -45.0
        is_mic_active = mic_db >= self.min_bargein_energy_db

        if not is_speaker_active:
            # Agent is not speaking: any mic energy is pure user speech
            state = "USER_MONO_SPEECH" if is_mic_active else "IDLE_SILENCE"
            action = "TRANSMIT_TO_ASR" if is_mic_active else "GATE_MUTED"
        else:
            # Agent is speaking: evaluate cross-correlation
            if correlation >= self.echo_thresh:
                # High correlation: microphone picked up speaker acoustic echo
                state = "ACOUSTIC_SPEAKER_ECHO"
                action = "SUPPRESS_ECHO_KEEP_SPEAKING"
            elif is_mic_active and correlation < (self.echo_thresh - 0.20):
                # High mic energy with low correlation: User is interrupting!
                state = "GENUINE_USER_BARGE_IN"
                action = "IMMEDIATELY_HALT_AGENT_SPEECH"
            else:
                state = "DOUBLE_TALK_AMBIGUOUS"
                action = "ATTENUATE_GENTLY"

        return {
            "status": "success",
            "mic_energy_db": round(mic_db, 2),
            "speaker_reference_energy_db": round(ref_db, 2),
            "cross_correlation_index": round(correlation, 3),
            "conversational_state": state,
            "recommended_agent_action": action
        }
