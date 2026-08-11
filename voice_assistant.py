import os
import sys
import datetime
import webbrowser
import subprocess
import re
import urllib.parse
import urllib.request
import json
import ssl
import math

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Disable SSL verification issues for Wikipedia and Web API queries
ssl._create_default_https_context = ssl._create_unverified_context

try:
    import requests
    requests.packages.urllib3.disable_warnings()
    _orig_req = requests.Session.request
    requests.Session.request = lambda self, method, url, **kwargs: _orig_req(self, method, url, **dict(kwargs, verify=False))
except Exception:
    pass

# Optional dependencies with safe imports
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import wikipedia
    wikipedia.set_user_agent("ARIAVoiceAssistant/1.0 (student@example.com)")
    WIKIPEDIA_AVAILABLE = True
except Exception:
    WIKIPEDIA_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import pyjokes
    PYJOKES_AVAILABLE = True
except ImportError:
    PYJOKES_AVAILABLE = False


class VoiceAssistant:
    """
    AI-Based Voice Assistant Engine
    Handles Speech Recognition (STT), Text-to-Speech (TTS), Intent Processing,
    and Execution of System/Web Actions.
    """

    def __init__(self, name="Aria", rate=175, volume=1.0):
        self.name = name
        self.rate = rate
        self.volume = volume
        self.tts_engine = None
        self.recognizer = None
        self.microphone_available = False

        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        """Initialize the text-to-speech engine using pyttsx3."""
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.rate)
                self.tts_engine.setProperty('volume', self.volume)
                
                # Select a pleasant voice if available (e.g. female/male)
                voices = self.tts_engine.getProperty('voices')
                if len(voices) > 1:
                    # Choose second voice if available (often female on Windows SAPI5)
                    self.tts_engine.setProperty('voice', voices[1].id)
                elif len(voices) > 0:
                    self.tts_engine.setProperty('voice', voices[0].id)
            except Exception as e:
                print(f"[TTS Warning] Could not initialize pyttsx3: {e}")
                self.tts_engine = None

    def _init_stt(self):
        """Initialize the SpeechRecognition recognizer and check microphone presence."""
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True

            try:
                mics = sr.Microphone.list_microphone_names()
                if len(mics) > 0:
                    self.microphone_available = True
                else:
                    self.microphone_available = False
            except Exception:
                self.microphone_available = False

    def speak(self, text):
        """Convert text response into spoken audio and print to console."""
        print(f"🤖 {self.name}: {text}")
        if PYTTSX3_AVAILABLE:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                voices = engine.getProperty('voices')
                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS Notice] {e}")
        return text

    def listen(self, timeout=5, phrase_time_limit=8):
        """
        Listen to audio from the microphone and return transcribed text.
        Falls back gracefully if microphone is unavailable.
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("[STT Error] SpeechRecognition library is not installed.")
            return None

        if not self.microphone_available:
            print("[STT Info] Microphone not detected or inaccessible. Using text input mode.")
            return None

        try:
            with sr.Microphone() as source:
                print("\n🎙️ Listening... (Speak now)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("⚡ Recognizing speech...")
            command = self.recognizer.recognize_google(audio)
            print(f"🗣️ You said: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out. No speech detected.")
            return None
        except sr.UnknownValueError:
            print("🤔 Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"📡 Could not request results from Google Speech Recognition service; {e}")
            return None
        except Exception as e:
            print(f"[STT Error] {e}")
            return None

    def get_time(self):
        """Get current formatted time and date."""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %B %d, %Y")
        return f"The current time is {time_str} on {date_str}."

    def search_wikipedia(self, query):
        """Search Wikipedia and return a short summary."""
        try:
            import wikipedia
        except ImportError:
            return "Wikipedia library is not installed."
        
        try:
            # Clean search query
            clean_query = re.sub(r'search|wikipedia|for|who is|what is|tell me about', '', query, flags=re.IGNORECASE).strip()
            if not clean_query:
                clean_query = query.strip()
            
            print(f"🔍 Searching Wikipedia for: '{clean_query}'...")
            summary = wikipedia.summary(clean_query, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:3]
            return f"Your query was too broad. Did you mean: {', '.join(options)}?"
        except wikipedia.exceptions.PageError:
            return f"Sorry, I could not find any Wikipedia page matching '{query}'."
        except Exception as e:
            return f"Failed to retrieve Wikipedia info: {str(e)}"

    def open_application(self, command):
        """Open local system applications or web apps based on command."""
        cmd_lower = command.lower()

        # Web applications / Websites
        if "youtube" in cmd_lower:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube in your browser."
        elif "google" in cmd_lower and "search" not in cmd_lower:
            webbrowser.open("https://www.google.com")
            return "Opening Google in your browser."
        elif "github" in cmd_lower:
            webbrowser.open("https://github.com")
            return "Opening GitHub in your browser."
        elif "stackoverflow" in cmd_lower or "stack overflow" in cmd_lower:
            webbrowser.open("https://stackoverflow.com")
            return "Opening Stack Overflow."
        elif "maps" in cmd_lower or "google maps" in cmd_lower:
            webbrowser.open("https://maps.google.com")
            return "Opening Google Maps."
        
        # Local Desktop Applications (Windows compatibility)
        if "notepad" in cmd_lower:
            if sys.platform.startswith("win"):
                try:
                    os.startfile("notepad.exe")
                except Exception:
                    subprocess.Popen("notepad.exe", shell=True)
            else:
                subprocess.Popen(["gedit"])
            return "Opening Notepad application."

        elif "calculator" in cmd_lower or "calc" in cmd_lower:
            if sys.platform.startswith("win"):
                try:
                    os.startfile("calc.exe")
                except Exception:
                    subprocess.Popen("calc.exe", shell=True)
            else:
                subprocess.Popen(["gnome-calculator"])
            return "Opening Calculator application."

        elif "command prompt" in cmd_lower or "cmd" in cmd_lower or "terminal" in cmd_lower:
            if sys.platform.startswith("win"):
                subprocess.Popen("start cmd.exe", shell=True)
            else:
                subprocess.Popen(["x-terminal-emulator"])
            return "Opening Terminal Command Prompt."

        elif "paint" in cmd_lower or "mspaint" in cmd_lower:
            if sys.platform.startswith("win"):
                try:
                    os.startfile("mspaint.exe")
                except Exception:
                    subprocess.Popen("mspaint.exe", shell=True)
            return "Opening MS Paint application."

        elif "file explorer" in cmd_lower or "explorer" in cmd_lower:
            if sys.platform.startswith("win"):
                subprocess.Popen("explorer.exe", shell=True)
            return "Opening File Explorer."

        return None

    def search_web(self, query):
        """Search Google and APIs to extract and speak actual results."""
        clean_query = re.sub(
            r'can you|tell me|describe me|describe|explain|search result|search google for|search web for|search for|google',
            '', query, flags=re.IGNORECASE
        ).strip()
        if not clean_query:
            clean_query = query.strip()

        print(f"🔍 Searching Web & APIs for: '{clean_query}'...")
        encoded = urllib.parse.quote_plus(clean_query)

        # 1. Try Wikipedia direct summary
        try:
            import wikipedia
            wiki_summary = wikipedia.summary(clean_query, sentences=2)
            return f"According to Wikipedia: {wiki_summary}"
        except Exception:
            pass

        # 2. Try Wikipedia search for top match summary
        try:
            import wikipedia
            search_results = wikipedia.search(clean_query)
            if search_results:
                first_match = search_results[0]
                wiki_summary = wikipedia.summary(first_match, sentences=2)
                return f"Information regarding {first_match}: {wiki_summary}"
        except Exception:
            pass

        # 3. Try DuckDuckGo Instant Answer API
        try:
            ctx = ssl._create_unverified_context()
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                abstract = data.get('AbstractText', '').strip()
                if abstract:
                    return f"Here is what I found for {clean_query}: {abstract}"
        except Exception as e:
            print(f"[DDG Search Notice] {e}")

        # 4. Try Wikipedia API Snippet Search
        try:
            ctx = ssl._create_unverified_context()
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded}&format=json"
            req = urllib.request.Request(url, headers={'User-Agent': 'ARIAVoiceAssistant/1.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                results = res.get('query', {}).get('search', [])
                if results:
                    snippet = re.sub(r'<[^<]+?>', '', results[0]['snippet'])
                    title = results[0]['title']
                    if snippet:
                        return f"Search result for {title}: {snippet}."
        except Exception as e:
            print(f"[Wiki Snippet Notice] {e}")

        # 5. Informative Fallback
        return f"I searched for '{clean_query}'. Click the web link below to view full Google search results."

    def get_system_stats(self):
        """Get CPU usage, RAM utilization, and battery status."""
        if not PSUTIL_AVAILABLE:
            return "System monitoring library (psutil) is not installed."
        
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram_info = psutil.virtual_memory()
        ram_usage = ram_info.percent
        
        status = f"System Stats: CPU Usage is {cpu_usage}%, RAM Usage is {ram_usage}%."
        
        battery = getattr(psutil, "sensors_battery", lambda: None)()
        if battery:
            status += f" Battery is at {battery.percent}% ({'Plugged in' if battery.power_plugged else 'On battery'})."
            
        return status

    def get_joke(self):
        """Tell a programming joke."""
        if PYJOKES_AVAILABLE:
            try:
                return pyjokes.get_joke()
            except Exception:
                pass
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

    def calculate_math(self, expression):
        """Perform simple mathematical calculations."""
        clean_expr = re.sub(r'calculate|what is|compute|solve', '', expression, flags=re.IGNORECASE).strip()
        # Replace word operators with symbols
        clean_expr = clean_expr.replace('plus', '+').replace('minus', '-').replace('times', '*').replace('x', '*').replace('divided by', '/').replace('over', '/')
        
        # Only allow numbers, math operators, spaces, decimal points
        if not re.match(r'^[0-9\.\+\-\*\/\(\)\s]+$', clean_expr):
            return "Invalid math expression. Only standard arithmetic is supported."

        try:
            # Safe evaluation using Python math scope
            result = eval(clean_expr, {"__builtins__": None, "math": math})
            return f"The answer to {clean_expr} is {result}."
        except Exception:
            return f"Could not calculate the expression '{clean_expr}'."

    def get_google_search_report(self, query):
        """Fetch structured search report containing top snippets and related topics."""
        clean_q = re.sub(
            r'can you|tell me|describe me|describe|explain|search result|search report|search google for|search web for|search for|google',
            '', query, flags=re.IGNORECASE
        ).strip()
        if not clean_q:
            clean_q = query.strip()

        encoded_q = urllib.parse.quote_plus(clean_q)
        search_url = f"https://www.google.com/search?q={encoded_q}"

        report_items = []
        summary_response = self.search_web(query)

        # Fetch extra search topics via Wikipedia Search API
        try:
            ctx = ssl._create_unverified_context()
            api_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_q}&format=json"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'ARIAVoiceAssistant/1.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=4) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                search_results = res.get('query', {}).get('search', [])
                for item in search_results[:3]:
                    title = item.get('title', '')
                    snippet = re.sub(r'<[^<]+?>', '', item.get('snippet', ''))
                    if title and snippet:
                        report_items.append({"title": title, "snippet": snippet})
        except Exception as e:
            print(f"[Search Report Error] {e}")

        details = {
            "query": clean_q,
            "url": search_url,
            "related_results": report_items
        }

        return summary_response, "google_search_report", details

    def process_command(self, command):
        """
        Main logic router for matching voice/text commands to actions.
        Returns a tuple: (response_text, action_category, extra_details)
        """
        if not command or not command.strip():
            return "Please provide a valid command.", "error", None

        cmd = command.strip().lower()
        print(f"\n🧠 Processing Command: '{cmd}'")

        # 1. Greeting & Identity
        if any(re.search(r'\b' + re.escape(w) + r'\b', cmd) for w in ["hello", "hi", "hey", "who are you", "what is your name"]):
            response = f"Hello! I am {self.name}, your AI Voice Assistant. How can I assist you today?"
            return response, "greeting", None

        # 2. Math Calculation (Checked before time so 'times' is not misidentified as 'time')
        if any(w in cmd for w in ["calculate", "plus", "minus", "times", "divided by"]) or re.search(r'\d+\s*[\+\-\*\/x]\s*\d+', cmd):
            response = self.calculate_math(cmd)
            return response, "math", None

        # 3. Time & Date Command (Exact word matching)
        if any(re.search(r'\b' + re.escape(w) + r'\b', cmd) for w in ["time", "date", "clock", "current time"]) or "what day is it" in cmd:
            response = self.get_time()
            return response, "time", {"time": datetime.datetime.now().isoformat()}

        # 4. Describe / Search / Google Search Reports
        if any(w in cmd for w in ["describe", "explain", "search result", "search report", "tell me about", "who is", "what is a"]):
            return self.get_google_search_report(cmd)

        # 5. Wikipedia Explicit Search
        if "wikipedia" in cmd:
            return self.get_google_search_report(cmd)

        # 6. Open System / Web Applications
        if "open" in cmd or "launch" in cmd:
            app_response = self.open_application(cmd)
            if app_response:
                return app_response, "open_app", {"command": cmd}
            else:
                return self.get_google_search_report(cmd)

        # 7. General Web Search
        if "search" in cmd or "google" in cmd:
            return self.get_google_search_report(cmd)

        # 6. System Stats (CPU, RAM)
        if any(w in cmd for w in ["system status", "cpu", "ram", "memory", "battery", "system stats"]):
            response = self.get_system_stats()
            return response, "system_stats", None

        # 7. Joke Command
        if any(w in cmd for w in ["joke", "funny", "make me laugh"]):
            response = self.get_joke()
            return response, "joke", None

        # 8. Math Calculation
        if any(w in cmd for w in ["calculate", "plus", "minus", "times", "divided by"]) or re.search(r'\d+\s*[\+\-\*\/]\s*\d+', cmd):
            response = self.calculate_math(cmd)
            return response, "math", None

        # 9. Exit Command
        if any(w in cmd for w in ["exit", "stop", "quit", "bye", "goodbye"]):
            response = f"Goodbye! Have a great day. {self.name} signing off."
            return response, "exit", None

        # 10. Default Fallback Search
        response = self.search_web(cmd)
        return f"I wasn't sure how to handle that directly, so I searched Google: {response}", "web_search", None

    def run_cli_loop(self):
        """Run interactive CLI mode in terminal."""
        self.speak(f"Hello! I am {self.name}, your AI Voice Assistant.")
        print("=" * 60)
        print("💡 COMMAND EXAMPLES:")
        print("  • 'What is the time?'")
        print("  • 'Search Wikipedia for Artificial Intelligence'")
        print("  • 'Open Notepad' / 'Open YouTube' / 'Open Calculator'")
        print("  • 'What is 45 times 12?'")
        print("  • 'Tell me a joke' / 'Show system status'")
        print("  • 'Exit' to quit")
        print("=" * 60)

        while True:
            # Try voice input first, fallback to text if mic unavailable or empty
            user_input = None
            if self.microphone_available:
                print("\nOptions: Press [Enter] for Voice Input, or type command directly:")
                inp = input("⌨️ Input (or press Enter for Mic): ").strip()
                if inp:
                    user_input = inp
                else:
                    user_input = self.listen()
            else:
                user_input = input("\n⌨️ Enter command: ").strip()

            if not user_input:
                continue

            response, action_type, _ = self.process_command(user_input)
            self.speak(response)

            if action_type == "exit":
                break


if __name__ == "__main__":
    assistant = VoiceAssistant(name="Aria")
    assistant.run_cli_loop()
