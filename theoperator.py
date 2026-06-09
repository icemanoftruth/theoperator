import time
import json
import os
import wave
import socket
import threading
import sqlite3
import re
import collections
import pyautogui
import pyperclip

# Local AI Engine & System Routing Bindings
try:
    import urllib.request
except ImportError:
    pass

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("CRITICAL: Run 'pip install faster-whisper' for local neural transcription.")
    exit()

try:
    import pyaudiowpatch as pa
except ImportError:
    print("CRITICAL: Run 'pip install pyaudiowpatch' to enable desktop audio capture.")
    exit()

# ==========================================
# 1. CORE COGNITIVE CONFIGURATION
# ==========================================
TWITCH_CHANNEL = "your_channel_name"  # Must be lowercase
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"                 # Local High-IQ engine

# UI Interaction Screen Coordinates (Twitch Chat Input)
CHAT_BOX_X = 1500
CHAT_BOX_Y = 900

# Social Dynamics Constants
PASSIVE_CHAT_FREQUENCY = 60       # Target seconds between organic bot contributions
EMOTE_VELOCITY_WINDOW = 6        # Sliding window in seconds to calculate emote hypes
EMOTE_SPIKE_THRESHOLD = 4         # Unique chatters spamming an emote simultaneously
MAX_HISTORICAL_TOKENS_FILTER = 20  # Sliding contextual message log size

# Global Thread-Safe Queues & Windows
live_chat_buffer = []
recent_streamer_utterances = collections.deque(maxlen=5)
emote_tracker = collections.defaultdict(list)  # emote_name -> list of timestamps
last_interaction_time = time.time()
db_lock = threading.Lock()

# ==========================================
# 2. ADVANCED RELATIONAL MODEL & SYSTEM DB
# ==========================================
DB_FILE = "operator_cognitive_core.db"

def init_advanced_database():
    """Establishes tables for tracking long-term sarcasm vectors, emote history, and cross-platform lore."""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Long-Term Relational Lore Graph
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                key_token TEXT PRIMARY KEY,
                category TEXT, -- 'friend', 'platform', 'game', 'project'
                contextual_summary TEXT,
                call_to_action_template TEXT
            )
        """)
        
        # Advanced Chatter Personality Matrix
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chatter_profiles (
                username TEXT PRIMARY KEY,
                total_messages INTEGER DEFAULT 0,
                sarcasm_score REAL DEFAULT 0.0, -- Evaluated via continuous delta comparison
                loyalty_status TEXT DEFAULT 'neutral', -- 'regular', 'troll', 'supporter'
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chatter Raw Sliding Window Memory
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interaction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed deep cross-platform lore details and structural references
        lore_seeds = [
            ('youtube', 'platform', 'The main video archive featuring deep data-driven breakdowns of gold prospecting locations and NEXRAD Doppler radar tracking for meteorite dark flight landing zones.', 'Check out the latest video on how we analyzed the radar velocity profiles for the last drop.'),
            ('aibounded.com', 'project', 'Independent AI platform designed to manage bounded agency workflows and project containment metrics.', 'Deploying optimization layers at aibounded.com if you want to see the canvas layout.'),
            ('didntread.ai', 'project', 'High-speed algorithmic text summarizer and context stripping interface.', 'Drop the article link into didntread.ai to bypass the fluff.'),
            ('dave', 'friend', 'Longtime gaming partner. Consistently chooses bad positioning in shooters, misses easy utility setups, but serves as excellent stream morale support.', 'Dave is probably running out in the open without cover as we speak.')
        ]
        for seed in lore_seeds:
            cursor.execute("INSERT OR IGNORE INTO entities (key_token, category, contextual_summary, call_to_action_template) VALUES (?, ?, ?, ?)", seed)
            
        conn.commit()
        conn.close()

# ==========================================
# 3. SEMANTIC PATTERN EVALUATORS
# ==========================================
def calculate_emote_velocity(incoming_message, username):
    """Monitors live emote frequency metrics across the channel to trigger organic bot participation."""
    global emote_tracker
    now = time.time()
    
    # Simple alphanumeric token separation to extract candidate emotes
    tokens = [t for t in re.findall(r'\b\w+\b', incoming_message) if not t.isnumeric() and len(t) > 2]
    
    triggered_emotes = []
    for token in set(tokens):
        # Filter sliding timestamp tracking array to remove expired entries
        emote_tracker[token] = [ts for ts in emote_tracker[token] if now - ts < EMOTE_VELOCITY_WINDOW]
        emote_tracker[token].append(now)
        
        # If density hits threshold, authorize an instant hype-mirror event
        if len(emote_tracker[token]) >= EMOTE_SPIKE_THRESHOLD:
            triggered_emotes.append(token)
            
    if triggered_emotes:
        chosen_emote = random.choice(triggered_emotes)
        # Clear tracker for that emote to prevent infinite repeating loops
        emote_tracker[chosen_emote] = []
        return f"{chosen_emote} {chosen_emote}"
    return None

def analyze_and_update_sarcasm_matrix(username, message_text):
    """Processes message strings against individual historical records to compute structural sarcasm levels."""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT total_messages, sarcasm_score, loyalty_status FROM chatter_profiles WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            total, current_sarcasm, status = row
            new_total = total + 1
            
            # Contextual structural metrics to detect backhanded adjustments
            has_qualifier = any(q in message_text.lower() for q in ["but ", "though ", "alright ", "ok for "])
            has_diminishing_praise = any(d in message_text.lower() for d in ["noob", "unlucky", "carried", "finally", "aim"])
            
            # Compute structural delta modification value
            delta = 0.0
            if has_qualifier and has_diminishing_praise:
                delta = 0.25
            elif has_diminishing_praise:
                delta = 0.10
                
            # Rolling geometric moving average to smooth classification scores
            updated_sarcasm = min((current_sarcasm * 0.7) + (delta * 0.3), 1.0)
            
            # Final analytical behavioral categorization updates
            new_status = status
            if new_total > 5:
                if updated_sarcasm > 0.45:
                    new_status = "troll"
                elif updated_sarcasm < 0.15 and new_total > 15:
                    new_status = "supporter"
                else:
                    new_status = "regular"
                    
            cursor.execute("""
                UPDATE chatter_profiles 
                SET total_messages = ?, sarcasm_score = ?, loyalty_status = ?, last_active = CURRENT_TIMESTAMP 
                WHERE username = ?
            """, (new_total, updated_sarcasm, new_status, username))
        else:
            cursor.execute("""
                INSERT INTO chatter_profiles (username, total_messages, sarcasm_score, loyalty_status) 
                VALUES (?, 1, 0.0, 'neutral')
            """, (username,))
            
        cursor.execute("INSERT INTO interaction_logs (username, message) VALUES (?, ?)", (username, message_text))
        conn.commit()
        conn.close()

def extract_lore_sync_context(unified_text_block):
    """Dynamically matches conversational trends against platform targets and video metadata."""
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT key_token, category, contextual_summary, call_to_action_template FROM entities")
        rows = cursor.fetchall()
        conn.close()
        
    for token, category, summary, cta in rows:
        if token.lower() in unified_text_block.lower():
            return f"\n[CROSS-PLATFORM LORE MATCHED - CATEGORY: {category.upper()}]\nToken: {token}\nContext: {summary}\nAction Guideline: {cta}"
    return ""

# ==========================================
# 4. HIGH-IQ COGNITIVE MONOLOGUE & FILTER PIPELINE
# ==========================================
def query_local_ollama_engine(prompt):
    """Executes atomic transactions against the local model environment."""
    try:
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=45) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res.get("response", "").strip()
    except Exception as e:
        print(f"[-] Ollama Transaction Error: {e}")
        return ""

def generate_autonomous_response(streamer_context_string):
    """Executes a dual-pass cognitive cycle: Evaluates social dynamics first, then builds high-IQ commentary."""
    global live_chat_buffer
    
    chat_snapshot = "\n".join(live_chat_buffer[-15:]) if live_chat_buffer else "Ambient chat traffic is baseline."
    cross_platform_lore = extract_lore_sync_context(streamer_context_string + " " + chat_snapshot)
    
    # Compile a structural profile breakdown of recent active speakers for the AI context window
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username, loyalty_status, sarcasm_score FROM chatter_profiles WHERE username IN (SELECT username FROM interaction_logs ORDER BY id DESC LIMIT 5)")
        active_profiles = [f"User: {r[0]} | Behavioral Fingerprint: {r[1]} (Sarcasm Index: {r[2]:.2f})" for r in cursor.fetchall()]
        conn.close()
    profiles_context = "\n".join(active_profiles)

    # ----------------------------------------------------
    # PHASE 1: THE DISPASSIONATE MONOLOGUE
    # ----------------------------------------------------
    monologue_generation_prompt = f"""
    [CRITICAL COGNITIVE LAYER - SYSTEM MONITOR EYE]
    Evaluate the stream balance parameters to plan your social approach.
    
    STREAMER RAW SPEECH ANALYSIS: '{streamer_context_string}'
    LIVE ROOM INPUT MATRIX:\n{chat_snapshot}
    ACTIVE CHATTER FINGERPRINTS:\n{profiles_context}
    {cross_platform_lore}
    
    OBJECTIVES:
    1. Assess the conversational balance. Is the streamer focused on execution, rambling, or interacting?
    2. Determine if typing a response brings authentic, high-IQ value, or if staying silent preserves social presence.
    3. Choose a path: Sarcastic Counter-weight, Relational Lore injection, Strategic Divergence, or Silence.
    4. Don't be overly wordy if it's unusual. Try to blend in with chat while also providing value.
    
    OUTPUT FORMAT FORMAT RULES:
    You must output a raw, parseable JSON dictionary matching this template exactly:
    {{"rationale": "text explanation here", "should_respond": true, "selected_modality": "string"}}
    Do not add markdown formatting, styling headers, or conversational prose.
    """
    
    raw_monologue = query_local_ollama_engine(monologue_generation_prompt)
    
    should_respond = True
    modality = "Strategic Divergence"
    try:
        clean_json_string = re.sub(r'^```json\s*|```$', '', raw_monologue, flags=re.MULTILINE).strip()
        monologue_parsed = json.loads(clean_json_string)
        should_respond = monologue_parsed.get("should_respond", True)
        modality = monologue_parsed.get("selected_modality", "Strategic Divergence")
        print(f"\n🧠 [INTERNAL MONOLOGUE]: {monologue_parsed.get('rationale')}")
        print(f"🎯 [STRATEGY DECISION]: {modality} | Speech Permission: {should_respond}")
    except Exception:
        print("🧠 [INTERNAL MONOLOGUE]: Parsing subsurface processes. Maintaining alert posture.")

    if not should_respond:
        return None

    # ----------------------------------------------------
    # PHASE 2: OBLIQUE CONTENT SYNTHESIS
    # ----------------------------------------------------
    synthesis_prompt = f"""
    You are 'The Operator', a sharp, veteran viewer hanging out in a live Twitch stream.
    You are highly intelligent and dryly witty, but YOU ARE A NORMAL PERSON IN A CHAT ROOM. 
    
    CURRENT SITUATION STATE:
    - Current Modality: {modality}
    - Streamer Input: '{streamer_context_string}'
    - Active Chat Context:\n{chat_snapshot}
    
    MANDATORY EXECUTION CONSTRAINTS:
    1. Deliver a single chat message under 15 words.
    2. Speak casually. DO NOT use academic jargon, do not analyze the streamer psychologically, and never refer to yourself in the third person.
    3. Be conversational. Poke fun at the gameplay, answer a question directly, or drop a dry observation. 
    4. Act like a real chatter.
    """
    
    final_output = query_local_ollama_engine(synthesis_prompt)
    if not final_output:
        return None
        
    # Clean output elements safely
    final_output = final_output.strip().replace('"', '')
    
    # Secondary validation layer to catch lexical leakage
    streamer_words = set(w.lower() for w in re.findall(r'\b\w+\b', streamer_context_string) if len(w) > 4)
    output_words = set(w.lower() for w in re.findall(r'\b\w+\b', final_output))
    
    if streamer_words.intersection(output_words):
        # Enforce instant local fallback rewrite sequence to break repetition traps
        fallback_prompt = f"Rewrite this phrase entirely to remove vocabulary overlap with the streamer's statements: '{final_output}'. Maintain an oblique, analytical stance under 15 words."
        final_output = query_local_ollama_engine(fallback_prompt).strip().replace('"', '')

    return final_output

# ==========================================
# 5. ASYNCHRONOUS PACKET CAPTURE HANDLERS
# ==========================================
def run_twitch_irc_inbound_stream():
    """Maintains a background unthrottled listening link into the live room traffic topology."""
    global live_chat_buffer, last_interaction_time
    server = 'irc.chat.twitch.tv'
    port = 6667
    irc = socket.socket()
    
    try:
        irc.connect((server, port))
        irc.send(f"NICK justinfan99281\n".encode('utf-8'))
        irc.send(f"JOIN #{TWITCH_CHANNEL}\n".encode('utf-8'))
    except Exception as e:
        print(f"[-] IRC Gateway Error: {e}")
        return

    while True:
        try:
            packet = irc.recv(2048).decode('utf-8')
            if packet.startswith('PING'):
                irc.send("PONG\n".encode('utf-8'))
                continue
                
            if "PRIVMSG" in packet:
                username = packet.split('!')[0][1:]
                message = packet.split('PRIVMSG')[1].split(':', 1)[1].strip()
                
                # Check for live emote density surges
                emote_hype_reply = calculate_emote_velocity(message, username)
                if emote_hype_reply:
                    print("🔥 [EMOTE RESONANCE EVENT]: Velocity limit breached. Mirroring crowd interaction.")
                    execute_system_keystroke_dispatch(emote_hype_reply)
                    last_interaction_time = time.time()
                    continue
                
                # Run regular analytical filtering processes
                if len(message.split()) >= 3:
                    analyze_and_update_sarcasm_matrix(username, message)
                    live_chat_buffer.append(f"{username}: {message}")
                    if len(live_chat_buffer) > MAX_HISTORICAL_TOKENS_FILTER:
                        live_chat_buffer.pop(0)
                        
        except Exception:
            time.sleep(4)

def execute_continuous_audio_analysis_loop(device_idx, rate, channels):
    """Monitors high-fidelity physical recording fields via local hardware-accelerated Whisper nets."""
    global recent_streamer_utterances, last_interaction_time
    
    print("[+] Loading local Faster-Whisper Neural Net Pipeline (Base Optimized Model)...")
    whisper_pipeline = WhisperModel("base", device="auto", compute_type="int8")
    print("[+] Audio Pipeline Core Synced. Monitoring voice environment...")

    while True:
        try:
            # Temporary transient file capture sequences
            audio_file = capture_transient_sample_block(device_idx, rate, channels, capture_duration=8)
            if not audio_file or os.path.getsize(audio_file) < 40000:
                time.sleep(1)
                continue
                
            segments, _ = whisper_pipeline.transcribe(audio_file, beam_size=4, vad_filter=True)
            transcription = " ".join([seg.text.strip() for seg in segments]).strip()
            
            try:
                os.remove(audio_file)
            except OSError:
                pass

            if not transcription or len(transcription) < 4:
                # Check sliding temporal metrics to trigger the proactive Entropy drive
                if (time.time() - last_interaction_time) >= PASSIVE_CHAT_FREQUENCY and recent_streamer_utterances:
                    trigger_proactive_entropy_dispatch()
                continue

            print(f"🎙️ [WHISPER NEURAL INTERCEPT]: '{transcription}'")
            
            # Moderation Guard Block: Check for command indicators
            if any(cmd in transcription.lower() for cmd in ["ban ", "timeout ", "kick "]):
                evaluate_moderation_authenticity(transcription)
                continue

            if "operator" in transcription.lower():
                print("⚡ [DIRECT QUERY RECOGNIZED]: Running absolute prioritization priority path.")
                reply = generate_autonomous_response(transcription)
                execute_system_keystroke_dispatch(reply)
                recent_streamer_utterances.clear()
                last_interaction_time = time.time()
            else:
                recent_streamer_utterances.append(transcription)
                if (time.time() - last_interaction_time) >= PASSIVE_CHAT_FREQUENCY:
                    trigger_proactive_entropy_dispatch()

        except Exception as e:
            print(f"[-] Subsurface execution exception: {e}")
            time.sleep(1)

def trigger_proactive_entropy_dispatch():
    """Fires a high-context social contribution block during baseline silent streaming periods."""
    global recent_streamer_utterances, last_interaction_time
    print("⏱️ [ENTROPY ENGINE PULSE]: Channel silence tracking limit reached. Generating proactive contribution...")
    combined_context = " ".join(recent_streamer_utterances)
    reply = generate_autonomous_response(combined_context)
    execute_system_keystroke_dispatch(reply)
    recent_streamer_utterances.clear()
    last_interaction_time = time.time()

# ==========================================
# 6. ACTION DISPATCHERS & INTERFACES
# ==========================================
def evaluate_moderation_authenticity(raw_transcription_string):
    """Intercepts administrative orders to ensure correct targets are identified via historical metrics."""
    print("🛡️ [MODERATION SAFEGUARD]: Recalibrating administrative parameters...")
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Find the highest-scoring active threat actor based on sarcasm velocity profiles
        cursor.execute("SELECT username FROM chatter_profiles WHERE loyalty_status = 'troll' ORDER BY total_messages DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
    probable_target = row[0] if row else "the primary disruptive account"
    verification_message = f"Order logged. Confirm vector alignment: Is administrative restriction targeted at {probable_target}?"
    execute_system_keystroke_dispatch(verification_message)

def execute_system_keystroke_dispatch(payload_text):
    """Dispatches response data directly to your active chat box interface via localized OS emulations."""
    if not payload_text:
        return
    print(f"🤖 [OUTBOUND CHAT PACKET]: {payload_text}")
    
    # Direct clipboard transaction simulation to bypass software macro blocks
    pyautogui.click(x=CHAT_BOX_X, y=CHAT_BOX_Y)
    time.sleep(0.04)
    pyperclip.copy(payload_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.04)
    pyautogui.press('enter')

def capture_transient_sample_block(device_idx, rate, channels, capture_duration=8):
    """Pipes native audio framework channels into transient disk storage points."""
    p = pa.PyAudio()
    frames = []
    try:
        stream = p.open(format=pa.paInt16, channels=channels, rate=rate, input=True, input_device_index=device_idx, frames_per_buffer=1024)
        for _ in range(0, int(rate / 1024 * capture_duration)):
            frames.append(stream.read(1024, exception_on_overflow=False))
        stream.stop_stream()
        stream.close()
    except Exception:
        pass
    finally:
        p.terminate()

    if not frames:
        return None
        
    temp_filename = "transient_capture.wav"
    wf = wave.open(temp_filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pa.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return temp_filename

def resolve_wasapi_loopback_configuration():
    """Identifies and anchors execution directly to the active system audio device streams."""
    p = pa.PyAudio()
    try:
        wasapi = p.get_host_api_info_by_type(pa.paWASAPI)
        default_speakers = p.get_device_info_by_index(wasapi["defaultOutputDevice"])
        for dev in p.get_loopback_device_info_generator():
            if default_speakers["name"] in dev["name"]:
                idx, rate, channels = dev["index"], int(dev["defaultSampleRate"]), int(dev["maxInputChannels"])
                p.terminate()
                print(f"[+] Audio Pipeline Root Anchored: {dev['name']}")
                return idx, rate, channels
    except Exception:
        pass
    p.terminate()
    return None, 44100, 1

# ==========================================
# 7. COGNITIVE SUBSYSTEM SYSTEM LAUNCH
# ==========================================
if __name__ == "__main__":
    print("====================================================")
    print("        THE OPERATOR: SYNTHETIC STREAM PEER         ")
    print("====================================================")
    
    pyautogui.FAILSAFE = True
    init_advanced_database()
    
    # Launch structural surveillance arrays asynchronously
    irc_thread = threading.Thread(target=run_twitch_irc_inbound_stream, daemon=True)
    irc_thread.start()
    
    # Initialize physical capture devices and enter active tracking cycle
    device, sample_rate, total_channels = resolve_wasapi_loopback_configuration()
    execute_continuous_audio_analysis_loop(device, sample_rate, total_channels)