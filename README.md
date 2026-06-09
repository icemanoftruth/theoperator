### ⚠️ IMPORTANT: TERMS OF USE AND LIABILITY DISCLAIMER

**USER RESPONSIBILITY:**
The Operator is a tool designed for educational purposes and personal stream enhancement. By using this software, you acknowledge that automating interaction on streaming platforms (such as Twitch) can violate the platform’s Terms of Service (ToS) regarding "Botting" or "Automation." 

**RISK MITIGATION:**
1. **ACCOUNT SAFETY:** You assume 100% responsibility for your Twitch account. We strongly recommend testing this software using a dedicated bot account, a test channel, or an account you are prepared to lose. Do not use this tool on your primary channel until you have thoroughly vetted its behavior in an isolated environment.
2. **MODERATION:** This software utilizes local AI models to generate text. While we have implemented "Internal Monologue" and "Safety Filters," AI models can hallucinate or generate inappropriate content. You are responsible for ensuring the output aligns with your stream's community guidelines.
3. **NO WARRANTIES:** This software is provided "as-is," without any warranty of any kind, express or implied. The developers (you) assume no liability for any loss of account access, channel bans, or other damages resulting from the use of this software.

**ETHICAL GUIDELINES:**
The Operator is intended to function as a co-pilot, not a deceptive entity. We recommend disclosing to your audience that you are experimenting with AI-driven community tools to maintain full transparency and trust with your viewers.

Step 1: Download the AI Brain

Download Ollama https://ollama.com/

Make sure the Ollama application is running in your system tray.

Open your command prompt or terminal and paste this command:

Bash
ollama run llama3:8b

Let it download (it should take a fraction of the time). Once it says "success" and gives you a >>> prompt, type /bye and hit Enter to exit the chat interface. The model is now cached on your PC.

Step 2: Update the Python Script

Open your Python script (e.g., theoperator.py) in your text editor and change this specific line at the top of the file:

Set Your Channel:
Find TWITCH_CHANNEL = "your_channel_name_here" and type your exact Twitch username in all lowercase (e.g., "icemanoftruth").

Step 3: Install Python Dependencies

Open a fresh command prompt and run this command to install the specific libraries the script needs for transcription, audio loopback, and keyboard/mouse control:

Bash
pip install faster-whisper pyaudiowpatch pyautogui pyperclip

Step 4: Calibrate the Chat Box Coordinates

The bot needs to know exactly where your Twitch "Send Message" box is on your screen so it can physically click it.

Open your Twitch channel chat in your browser and leave it visible on your screen.

Open a command prompt and run the Python interpreter by typing python and hitting Enter.

Paste these three lines:

Python
import pyautogui, time
time.sleep(4)
print(pyautogui.position())

Immediately hover your mouse cursor directly over the Twitch chat text box and leave it there for 4 seconds.

The console will print your coordinates (e.g., Point(x=1450, y=920)).

Open your operator.py script and update the coordinates to match:

Python
CHAT_BOX_X = 1450
CHAT_BOX_Y = 920

Step 5: Run The Operator

Make sure your Twitch chat window is visible on the screen where you mapped the coordinates.
Run the bot from your terminal or open command prompt as administrator:

Bash
python theoperator.py
