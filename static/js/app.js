/* ==========================================================================
   ARIA AI Voice Assistant - Ultra Interactive JavaScript Engine
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Selectors
    const orbContainer = document.getElementById('orb-container');
    const glowingOrb = document.getElementById('glowing-orb');
    const btnMicToggle = document.getElementById('btn-mic-toggle');
    const commandInput = document.getElementById('command-input');
    const btnSend = document.getElementById('btn-send');
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    const logStream = document.getElementById('log-stream');
    const liveClock = document.getElementById('live-clock');
    const micStatusLabel = document.getElementById('mic-status-label');
    const sysStatusLabel = document.getElementById('sys-status-label');
    const responseCategory = document.getElementById('response-category');
    const responseTextContent = document.getElementById('response-text-content');
    const cpuVal = document.getElementById('cpu-val');
    const cpuBar = document.getElementById('cpu-bar');
    const ramVal = document.getElementById('ram-val');
    const ramBar = document.getElementById('ram-bar');
    const canvas = document.getElementById('audio-waveform');
    const ctx = canvas.getContext('2d');

    // States
    let isListening = false;
    let isSpeaking = false;
    let recognition = null;
    let wavePhase = 0;

    // --------------------------------------------------
    // 1. Audio Synthesizer Sound Effects (Web Audio API)
    // --------------------------------------------------
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function playAudioTone(freq, type, duration) {
        try {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {
            // Audio context muted or restricted
        }
    }

    function playBeepStart() {
        playAudioTone(587.33, 'sine', 0.15); // D5
        setTimeout(() => playAudioTone(880, 'sine', 0.2), 100); // A5
    }

    function playChimeSuccess() {
        playAudioTone(523.25, 'sine', 0.12); // C5
        setTimeout(() => playAudioTone(659.25, 'sine', 0.15), 90); // E5
        setTimeout(() => playAudioTone(783.99, 'sine', 0.25), 180); // G5
    }

    // --------------------------------------------------
    // 2. Web Speech Recognition Setup
    // --------------------------------------------------
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            setListeningState(true);
            playBeepStart();
            updateStatus('Listening... Speak now into your microphone', 'listening');
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (interimTranscript) {
                commandInput.value = interimTranscript;
            }

            if (finalTranscript) {
                commandInput.value = finalTranscript;
                appendLog('user', `🗣️ You said: "${finalTranscript}"`);
                processCommand(finalTranscript);
            }
        };

        recognition.onerror = (event) => {
            console.warn('Speech Recognition Error:', event.error);
            setListeningState(false);
            if (event.error === 'no-speech') {
                updateStatus('No speech detected. Click mic to speak again.', 'ready');
            } else if (event.error === 'not-allowed') {
                updateStatus('Microphone permission denied. Using keyboard input mode.', 'ready');
                micStatusLabel.textContent = 'Mic Restricted';
            } else {
                updateStatus(`Notice: ${event.error}. You can type commands directly!`, 'ready');
            }
        };

        recognition.onend = () => {
            setListeningState(false);
        };
    } else {
        micStatusLabel.textContent = 'Mic N/A (Browser)';
        console.warn('Web Speech API not supported in this browser environment.');
    }

    // --------------------------------------------------
    // 3. Audio Waveform Spectrum Animation
    // --------------------------------------------------
    function drawWaveform() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.lineWidth = 2.5;

        const amplitude = isListening ? 24 : (isSpeaking ? 18 : 5);
        const frequency = isListening ? 0.035 : 0.02;
        const speed = isListening ? 0.16 : (isSpeaking ? 0.1 : 0.04);

        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        if (isListening) {
            gradient.addColorStop(0, '#f5576c');
            gradient.addColorStop(0.5, '#ef4444');
            gradient.addColorStop(1, '#00f2fe');
        } else if (isSpeaking) {
            gradient.addColorStop(0, '#00f2fe');
            gradient.addColorStop(0.5, '#7f00ff');
            gradient.addColorStop(1, '#10b981');
        } else {
            gradient.addColorStop(0, 'rgba(0, 242, 254, 0.3)');
            gradient.addColorStop(1, 'rgba(127, 0, 255, 0.3)');
        }

        ctx.strokeStyle = gradient;

        for (let x = 0; x < canvas.width; x++) {
            const y = canvas.height / 2 + Math.sin(x * frequency + wavePhase) * amplitude * Math.sin((x / canvas.width) * Math.PI);
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();

        wavePhase += speed;
        requestAnimationFrame(drawWaveform);
    }
    drawWaveform();

    // --------------------------------------------------
    // 4. UI Helper Functions
    // --------------------------------------------------
    function setListeningState(listening) {
        isListening = listening;
        if (listening) {
            orbContainer.classList.add('listening');
            btnMicToggle.classList.add('listening');
        } else {
            orbContainer.classList.remove('listening');
            btnMicToggle.classList.remove('listening');
        }
    }

    function updateStatus(text, mode) {
        statusText.textContent = text;
        if (mode === 'listening') {
            statusDot.className = 'status-dot listening';
        } else {
            statusDot.className = 'status-dot';
        }
    }

    function appendLog(type, message) {
        const item = document.createElement('div');
        item.className = `log-item ${type}`;

        const tag = document.createElement('span');
        tag.className = 'log-tag';
        const now = new Date();
        tag.textContent = `${type.toUpperCase()} • ${now.toLocaleTimeString()}`;

        const content = document.createElement('span');
        content.textContent = message;

        item.appendChild(tag);
        item.appendChild(content);

        logStream.appendChild(item);
        logStream.scrollTop = logStream.scrollHeight;

        if (type === 'user' || type === 'assistant') {
            try { saveActiveMessage(type, message); } catch(e) {}
        }
    }

    function displayResponseCard(category, responseText, details = null) {
        if (responseCategory) responseCategory.textContent = category.replace(/_/g, ' ').toUpperCase();
        
        let htmlContent = `<div style="font-size:1.02rem; line-height:1.5;">${responseText}</div>`;

        if (details && details.related_results && details.related_results.length > 0) {
            htmlContent += `<div style="margin-top:14px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.12);">
                <div style="font-size:0.78rem; font-weight:700; color:var(--accent-cyan); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">📰 Related Google & Web Search Topics:</div>
                <div style="display:flex; flex-direction:column; gap:8px;">`;
            
            details.related_results.forEach(item => {
                htmlContent += `<div style="background:rgba(255,255,255,0.04); padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.08);">
                    <strong style="color:var(--accent-blue); font-size:0.88rem;">🔹 ${item.title}:</strong>
                    <span style="font-size:0.84rem; color:var(--text-secondary); display:block; margin-top:2px;">${item.snippet}...</span>
                </div>`;
            });
            
            htmlContent += `</div></div>`;
        }

        if (details && details.url) {
            htmlContent += `<br><a href="${details.url}" target="_blank" style="display:inline-flex; align-items:center; gap:8px; background:linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); color:#fff; padding:10px 18px; border-radius:30px; text-decoration:none; font-weight:700; font-size:0.88rem; margin-top:10px; box-shadow:0 4px 15px rgba(0,242,254,0.4);" class="search-url-btn">🌐 View Full Google Search Results Page</a>`;
        }
        
        // Update Right Panel Card
        if (responseTextContent) responseTextContent.innerHTML = htmlContent;

        // Update Top Hero Result Banner (Right below input box)
        const heroCategory = document.getElementById('hero-category');
        const heroResponseText = document.getElementById('hero-response-text');
        const heroCard = document.getElementById('hero-response-box');

        if (heroCategory) heroCategory.textContent = category.replace(/_/g, ' ').toUpperCase();
        if (heroResponseText) heroResponseText.innerHTML = htmlContent;
        if (heroCard) {
            heroCard.style.borderColor = 'var(--accent-cyan)';
            heroCard.style.boxShadow = '0 0 25px rgba(0, 242, 254, 0.4)';
            setTimeout(() => {
                heroCard.style.borderColor = 'var(--accent-purple)';
                heroCard.style.boxShadow = 'none';
            }, 600);
        }

        // Visual flash effect on right panel card
        const card = document.getElementById('latest-response-box');
        if (card) {
            card.style.borderColor = 'var(--accent-cyan)';
            setTimeout(() => {
                card.style.borderColor = 'var(--accent-purple)';
            }, 500);
        }
    }

    function speakResponse(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            const voices = window.speechSynthesis.getVoices();
            if (voices.length > 0) {
                // Select a natural English voice if available
                const preferredVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Zira') || v.name.includes('Samantha')));
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }
            }

            utterance.onstart = () => {
                isSpeaking = true;
                updateStatus('ARIA is speaking response out loud...', 'speaking');
            };

            utterance.onend = () => {
                isSpeaking = false;
                updateStatus('Ready for next command', 'ready');
            };

            utterance.onerror = (e) => {
                console.warn('Browser Speech Error:', e);
                isSpeaking = false;
                updateStatus('Ready for next command', 'ready');
            };

            window.speechSynthesis.speak(utterance);
        }
    }

    // Load voices on init
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            window.speechSynthesis.getVoices();
        };
    }

    // Notepad Modal Elements & Handlers
    function openNotepadModal(initialText = '') {
        const modal = document.getElementById('notepad-modal');
        const textarea = document.getElementById('notepad-textarea');
        if (modal) {
            modal.style.display = 'flex';
            modal.style.visibility = 'visible';
            modal.style.opacity = '1';
            if (initialText && textarea) {
                textarea.value += (textarea.value ? '\n\n' : '') + initialText;
            }
            if (textarea) {
                textarea.focus();
                updateNotepadCount();
            }
        }
    }

    function closeNotepadModal() {
        const modal = document.getElementById('notepad-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    function updateNotepadCount() {
        const textarea = document.getElementById('notepad-textarea');
        const countSpan = document.getElementById('notepad-char-count');
        if (textarea && countSpan) {
            const val = textarea.value;
            const chars = val.length;
            const words = val.trim() ? val.trim().split(/\s+/).length : 0;
            countSpan.textContent = `${chars} characters | ${words} words`;
        }
    }

    document.addEventListener('click', (e) => {
        if (e.target && e.target.id === 'btn-notepad-close') closeNotepadModal();
        if (e.target && e.target.id === 'btn-notepad-clear') {
            const textarea = document.getElementById('notepad-textarea');
            if (textarea) {
                textarea.value = '';
                updateNotepadCount();
            }
        }
        if (e.target && e.target.id === 'btn-notepad-copy') {
            const textarea = document.getElementById('notepad-textarea');
            if (textarea && textarea.value) {
                navigator.clipboard.writeText(textarea.value);
                alert('Notes copied to clipboard!');
            }
        }
        if (e.target && e.target.id === 'btn-notepad-save') {
            const textarea = document.getElementById('notepad-textarea');
            if (textarea) {
                const text = textarea.value || 'Empty note';
                const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'notes.txt';
                a.click();
            }
        }
    });

    const textareaElem = document.getElementById('notepad-textarea');
    if (textareaElem) textareaElem.addEventListener('input', updateNotepadCount);

    // Calculator Modal Elements & Handlers
    function openCalculatorModal() {
        const modal = document.getElementById('calculator-modal');
        const calcScreen = document.getElementById('calc-screen');
        if (modal) {
            modal.style.display = 'flex';
            modal.style.visibility = 'visible';
            modal.style.opacity = '1';
            if (calcScreen) calcScreen.value = '0';
        }
    }

    function closeCalculatorModal() {
        const modal = document.getElementById('calculator-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    document.addEventListener('click', (e) => {
        if (e.target && e.target.id === 'btn-calc-close') closeCalculatorModal();
        if (e.target && e.target.classList.contains('calc-btn')) {
            const btn = e.target;
            const calcScreen = document.getElementById('calc-screen');
            const val = btn.getAttribute('data-val');
            if (!window.calcExpression) window.calcExpression = '';

            if (val === 'C') {
                window.calcExpression = '';
                if (calcScreen) calcScreen.value = '0';
            } else if (val === 'BACK') {
                window.calcExpression = window.calcExpression.slice(0, -1);
                if (calcScreen) calcScreen.value = window.calcExpression || '0';
            } else if (val === '=') {
                try {
                    const res = Function(`'use strict'; return (${window.calcExpression})`)();
                    if (calcScreen) calcScreen.value = res;
                    window.calcExpression = String(res);
                } catch(err) {
                    if (calcScreen) calcScreen.value = 'Error';
                    window.calcExpression = '';
                }
            } else {
                if (calcScreen && calcScreen.value === '0' && !isNaN(val)) {
                    window.calcExpression = val;
                } else {
                    window.calcExpression += val;
                }
                if (calcScreen) calcScreen.value = window.calcExpression;
            }
        }
    });

    // --------------------------------------------------
    // 5. Client-Side Engine Fallback (For Live Public GitHub Pages Deployment)
    // --------------------------------------------------
    async function processCommandClientSide(cmdText) {
        const cmd = cmdText.trim().toLowerCase();
        let responseText = '';
        let actionCategory = 'response';
        let details = null;

        // 1. Greeting & Identity
        if (/hello|hi|hey|who are you|what is your name/.test(cmd)) {
            responseText = "Hello! I am ARIA, your AI Voice Assistant. How can I assist you today?";
            actionCategory = "greeting";
        }
        // 2. Math Calculations
        else if (/calculate|plus|minus|times|divided by|\d+\s*[\+\-\*\/x]\s*\d+/.test(cmd)) {
            actionCategory = "math";
            try {
                let expr = cmd.replace(/can you|calculate|what is|how much is/gi, '').replace(/plus/gi, '+').replace(/minus/gi, '-').replace(/times|x/gi, '*').replace(/divided by/gi, '/').trim();
                let cleanExpr = expr.replace(/[^0-9\+\-\*\/\.\(\)\s]/g, '');
                if (cleanExpr) {
                    let result = Function(`'use strict'; return (${cleanExpr})`)();
                    responseText = `The result of ${expr} is ${result}.`;
                } else {
                    responseText = "I could not evaluate that mathematical expression.";
                }
            } catch(e) {
                responseText = "Sorry, I encountered an error while calculating that expression.";
            }
        }
        // 3. Time & Date
        else if (/time|date|clock|day/.test(cmd)) {
            actionCategory = "time";
            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const dateStr = now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
            responseText = `Current time is ${timeStr} on ${dateStr}.`;
        }
        // 4. Notepad Application
        else if (cmd.includes('notepad')) {
            actionCategory = "open_app";
            openNotepadModal();
            responseText = "Opening ARIA Interactive Notepad editor on screen.";
        }
        // 5. Calculator Application
        else if (cmd.includes('calculator') || cmd.includes('calc')) {
            actionCategory = "open_app";
            openCalculatorModal();
            responseText = "Opening ARIA Interactive Calculator tool on screen.";
        }
        // 6. YouTube Web App
        else if (cmd.includes('youtube')) {
            actionCategory = "open_app";
            try { window.open('https://www.youtube.com', '_blank'); } catch(e) {}
            responseText = "Opening YouTube in a new browser tab.";
            details = { url: "https://www.youtube.com" };
        }
        // 7. Google Web App
        else if (cmd.includes('google') && !cmd.includes('search')) {
            actionCategory = "open_app";
            try { window.open('https://www.google.com', '_blank'); } catch(e) {}
            responseText = "Opening Google in a new browser tab.";
            details = { url: "https://www.google.com" };
        }
        // 8. GitHub Web App
        else if (cmd.includes('github')) {
            actionCategory = "open_app";
            try { window.open('https://github.com', '_blank'); } catch(e) {}
            responseText = "Opening GitHub in a new browser tab.";
            details = { url: "https://github.com" };
        }
        // 9. Jokes
        else if (cmd.includes('joke')) {
            actionCategory = "joke";
            const jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "There are 10 types of people in the world: those who understand binary, and those who don't.",
                "Why did the JavaScript developer wear glasses? Because he didn't C#!",
                "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
                "Software developers are converted machines: they turn coffee into code!"
            ];
            responseText = jokes[Math.floor(Math.random() * jokes.length)];
        }
        // 10. System Stats
        else if (/system status|cpu|ram|memory|stats/.test(cmd)) {
            actionCategory = "system_stats";
            responseText = "System Monitoring: Browser Client Engine active. Memory & Web Speech API operational.";
        }
        // 11. Search & Information Queries (Wikipedia Search API Report)
        else {
            actionCategory = "google_search_report";
            let cleanQuery = cmd.replace(/can you|tell me|describe me|describe|explain|search result|search report|search google for|search web for|search for|google|wikipedia/gi, '').trim();
            if (!cleanQuery) cleanQuery = cmd;

            const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(cleanQuery)}`;
            const relatedTopics = [];

            try {
                const apiReqUrl = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(cleanQuery)}&format=json&origin=*`;
                const wikiRes = await fetch(apiReqUrl);
                
                if (wikiRes.ok) {
                    const wikiData = await wikiRes.json();
                    const searchResults = (wikiData.query && wikiData.query.search) ? wikiData.query.search : [];
                    
                    if (searchResults.length > 0) {
                        const topMatch = searchResults[0];
                        const cleanSnippet = topMatch.snippet.replace(/<[^>]*>?/gm, '');
                        responseText = `According to Wikipedia (${topMatch.title}): ${cleanSnippet}...`;

                        for (let i = 0; i < Math.min(3, searchResults.length); i++) {
                            const item = searchResults[i];
                            relatedTopics.push({
                                title: item.title,
                                snippet: item.snippet.replace(/<[^>]*>?/gm, '')
                            });
                        }
                    } else {
                        responseText = `Information retrieved for '${cleanQuery}'. Click the search link below to view complete Google search results.`;
                    }
                } else {
                    responseText = `Search results compiled for '${cleanQuery}'. Click the link below to view full search results on Google.`;
                }
            } catch(e) {
                responseText = `Search results retrieved for '${cleanQuery}'. Click below to open full Google search page.`;
            }

            details = {
                query: cleanQuery,
                url: searchUrl,
                related_results: relatedTopics.length > 0 ? relatedTopics : [
                    { title: `Explore '${cleanQuery}' on Google`, snippet: `View live web search results, articles, and media for ${cleanQuery}.` }
                ]
            };
        }

        // Render response card, append to activity log, and speak response out loud
        playChimeSuccess();
        displayResponseCard(actionCategory, responseText, details);
        appendLog('assistant', `🤖 ${responseText}`);
        speakResponse(responseText);
    }

    // --------------------------------------------------
    // 6. Command Execution API Handler
    // --------------------------------------------------
    async function processCommand(cmdText) {
        if (!cmdText.trim()) return;

        updateStatus('Processing command...', 'ready');

        const cmdLower = cmdText.toLowerCase();

        // Client-Side Interactive Application Launcher
        if (cmdLower.includes('notepad')) {
            openNotepadModal();
        } else if (cmdLower.includes('calculator') || cmdLower.includes('calc')) {
            openCalculatorModal();
        } else if (cmdLower.includes('youtube')) {
            try { window.open('https://www.youtube.com', '_blank'); } catch(e) {}
        } else if (cmdLower.includes('open google')) {
            try { window.open('https://www.google.com', '_blank'); } catch(e) {}
        } else if (cmdLower.includes('github')) {
            try { window.open('https://github.com', '_blank'); } catch(e) {}
        }

        // Check if running on GitHub Pages or static host
        if (window.location.hostname.includes('github.io')) {
            await processCommandClientSide(cmdText);
            return;
        }

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: cmdText, speak: true })
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json();
            if (data.status === 'success') {
                playChimeSuccess();
                displayResponseCard(data.action || 'response', data.response, data.details);
                appendLog('assistant', `🤖 ${data.response}`);
                speakResponse(data.response);
            } else {
                displayResponseCard('Error', data.response || 'Could not process command.');
                appendLog('assistant', `⚠️ ${data.response}`);
                updateStatus('Ready for command', 'ready');
            }
        } catch (err) {
            console.warn('Backend server API unavailable. Falling back to Client-Side Web Engine...', err);
            await processCommandClientSide(cmdText);
        }
    }

    // Server-Side Microphone Listener Fallback
    async function triggerServerMicListen() {
        setListeningState(true);
        playBeepStart();
        updateStatus('Listening via host microphone...', 'listening');

        try {
            const res = await fetch('/api/listen', { method: 'POST' });
            const data = await res.json();
            setListeningState(false);

            if (data.status === 'success') {
                playChimeSuccess();
                commandInput.value = data.command;
                appendLog('user', `🗣️ Server Mic Heard: "${data.command}"`);
                displayResponseCard(data.action || 'response', data.response, data.details);
                appendLog('assistant', `🤖 ${data.response}`);
                speakResponse(data.response);
            } else {
                updateStatus(data.message || 'No speech recognized', 'ready');
            }
        } catch (e) {
            setListeningState(false);
            updateStatus('Ready for command', 'ready');
        }
    }

    // --------------------------------------------------
    // 6. System Gauges & Clock Polling
    // --------------------------------------------------
    async function updateSystemDashboard() {
        // Clock
        const now = new Date();
        liveClock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            if (data.system_stats) {
                // Parse CPU and RAM percentages
                const cpuMatch = data.system_stats.match(/CPU Usage is ([\d\.]+)%/);
                const ramMatch = data.system_stats.match(/RAM Usage is ([\d\.]+)%/);

                if (cpuMatch) {
                    const cpuPercent = parseFloat(cpuMatch[1]);
                    cpuVal.textContent = `${cpuPercent}%`;
                    cpuBar.style.width = `${cpuPercent}%`;
                }
                if (ramMatch) {
                    const ramPercent = parseFloat(ramMatch[1]);
                    ramVal.textContent = `${ramPercent}%`;
                    ramBar.style.width = `${ramPercent}%`;
                }
            }
            if (data.mic_available) {
                micStatusLabel.textContent = 'Mic Ready';
            }
        } catch (e) {
            // Simulated random gauge values if backend polling fails
            const simCpu = Math.floor(12 + Math.random() * 18);
            const simRam = Math.floor(45 + Math.random() * 5);
            cpuVal.textContent = `${simCpu}%`;
            cpuBar.style.width = `${simCpu}%`;
            ramVal.textContent = `${simRam}%`;
            ramBar.style.width = `${simRam}%`;
        }
    }

    // --------------------------------------------------
    // 7. Event Listeners
    // --------------------------------------------------
    btnMicToggle.addEventListener('click', async () => {
        if (isListening) {
            if (recognition) {
                try { recognition.stop(); } catch(e) {}
            }
            setListeningState(false);
            updateStatus('Listening stopped. Click mic to speak again.', 'ready');
        } else {
            const isStaticHost = window.location.hostname.includes('github.io');

            // 1. Request microphone permissions explicitly
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                try {
                    await navigator.mediaDevices.getUserMedia({ audio: true });
                } catch (err) {
                    console.warn("Browser microphone access restricted:", err);
                    if (!isStaticHost) {
                        triggerServerMicListen();
                        return;
                    } else {
                        updateStatus('⚠️ Please allow microphone access in your browser address bar to speak.', 'ready');
                        alert('Microphone Access Notice:\nPlease allow microphone permissions in your browser address bar (click lock/tune icon near URL) to speak to ARIA.');
                        return;
                    }
                }
            }

            // 2. Start Web Speech Recognition Engine
            if (recognition) {
                try {
                    setListeningState(true);
                    playBeepStart();
                    updateStatus('🎙️ Listening... Speak your command now into your microphone!', 'listening');
                    recognition.start();
                } catch (e) {
                    console.warn("Recognition start notice:", e);
                    setListeningState(true);
                    updateStatus('🎙️ Listening for speech...', 'listening');
                }
            } else if (!isStaticHost) {
                triggerServerMicListen();
            } else {
                updateStatus('⚠️ Web Speech Recognition not supported by browser. Type your command below.', 'ready');
            }
        }
    });

    orbContainer.addEventListener('click', () => {
        btnMicToggle.click();
    });

    btnSend.addEventListener('click', () => {
        const text = commandInput.value.trim();
        if (text) {
            appendLog('user', `💬 Typed: "${text}"`);
            processCommand(text);
            commandInput.value = '';
        }
    });

    commandInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            btnSend.click();
        }
    });

    // Shortcut Chip Click Handlers
    document.querySelectorAll('.chip-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            commandInput.value = cmd;
            appendLog('user', `⚡ Clicked Shortcut: "${cmd}"`);
            processCommand(cmd);
            commandInput.value = '';
        });
    });

    // --------------------------------------------------
    // 8. User Authentication Manager (GitHub, Apple ID, Google, Email)
    // --------------------------------------------------
    let currentUser = JSON.parse(localStorage.getItem('aria_logged_user')) || {
        id: 'guest_user',
        name: 'Guest User',
        email: 'guest@aria.ai',
        provider: 'Guest'
    };

    const btnUserAuth = document.getElementById('btn-user-auth');
    const userDisplayName = document.getElementById('user-display-name');
    const authModal = document.getElementById('auth-modal');
    const btnAuthClose = document.getElementById('btn-auth-close');
    const btnLoginGithub = document.getElementById('btn-login-github');
    const btnLoginApple = document.getElementById('btn-login-apple');
    const btnLoginGoogle = document.getElementById('btn-login-google');
    const btnAuthSubmit = document.getElementById('btn-auth-submit');
    const btnAuthGuest = document.getElementById('btn-auth-guest');
    const authEmail = document.getElementById('auth-email');
    const authPassword = document.getElementById('auth-password');

    function updateAuthUserUI() {
        if (userDisplayName) {
            userDisplayName.textContent = currentUser.name || 'Sign In';
        }
        if (btnUserAuth) {
            if (currentUser.provider !== 'Guest') {
                btnUserAuth.style.background = 'rgba(16, 185, 129, 0.18)';
                btnUserAuth.style.borderColor = 'var(--success)';
            } else {
                btnUserAuth.style.background = 'rgba(0, 242, 254, 0.12)';
                btnUserAuth.style.borderColor = 'rgba(0, 242, 254, 0.3)';
            }
        }
    }
    updateAuthUserUI();

    function saveUserSession(user) {
        currentUser = user;
        localStorage.setItem('aria_logged_user', JSON.stringify(user));
        updateAuthUserUI();
        if (authModal) authModal.style.display = 'none';
        appendLog('system', `👤 Logged in as ${user.name} (${user.provider})`);
        
        // Sync user profile to persistent cloud/SQLite database
        try {
            fetch('/api/db/user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(user)
            }).catch(err => {});
        } catch(e) {}

        loadHistoryFromStorage();
    }

    if (btnUserAuth) {
        btnUserAuth.addEventListener('click', () => {
            if (currentUser.provider !== 'Guest') {
                if (confirm(`Logged in as ${currentUser.name} (${currentUser.email}). Log out?`)) {
                    saveUserSession({ id: 'guest_user', name: 'Guest User', email: 'guest@aria.ai', provider: 'Guest' });
                }
            } else if (authModal) {
                authModal.style.display = 'flex';
            }
        });
    }

    const chipBtnAuth = document.getElementById('chip-btn-auth');
    const chipBtnHistory = document.getElementById('chip-btn-history');

    if (chipBtnAuth) {
        chipBtnAuth.addEventListener('click', () => {
            if (authModal) authModal.style.display = 'flex';
        });
    }

    if (chipBtnHistory) {
        chipBtnHistory.addEventListener('click', () => {
            renderHistoryList();
            if (historyDrawer) historyDrawer.style.display = 'flex';
        });
    }

    if (btnAuthClose) btnAuthClose.addEventListener('click', () => { authModal.style.display = 'none'; });

    if (btnLoginGithub) {
        btnLoginGithub.addEventListener('click', () => {
            saveUserSession({
                id: 'github_' + Date.now(),
                name: 'GitHub Developer',
                email: 'user@github.com',
                provider: 'GitHub'
            });
        });
    }

    if (btnLoginApple) {
        btnLoginApple.addEventListener('click', () => {
            saveUserSession({
                id: 'apple_' + Date.now(),
                name: 'Apple User',
                email: 'user@icloud.com',
                provider: 'Apple ID'
            });
        });
    }

    if (btnLoginGoogle) {
        btnLoginGoogle.addEventListener('click', () => {
            saveUserSession({
                id: 'google_' + Date.now(),
                name: 'Google User',
                email: 'user@gmail.com',
                provider: 'Google'
            });
        });
    }

    if (btnAuthSubmit) {
        btnAuthSubmit.addEventListener('click', () => {
            const email = authEmail ? authEmail.value.trim() : '';
            if (email) {
                const nameStr = email.split('@')[0];
                saveUserSession({
                    id: 'email_' + Date.now(),
                    name: nameStr.charAt(0).toUpperCase() + nameStr.slice(1),
                    email: email,
                    provider: 'Email'
                });
            } else {
                alert('Please enter a valid email address.');
            }
        });
    }

    if (btnAuthGuest) {
        btnAuthGuest.addEventListener('click', () => {
            saveUserSession({
                id: 'guest_user',
                name: 'Guest User',
                email: 'guest@aria.ai',
                provider: 'Guest'
            });
        });
    }

    // --------------------------------------------------
    // 9. Persistent Chat History & Session Storage Manager
    // --------------------------------------------------
    let currentSessionId = 'session_' + Date.now();
    let savedSessions = JSON.parse(localStorage.getItem('aria_saved_sessions')) || [];

    const btnToggleHistory = document.getElementById('btn-toggle-history');
    const historyDrawer = document.getElementById('history-drawer');
    const btnHistoryClose = document.getElementById('btn-history-close');
    const btnNewChat = document.getElementById('btn-new-chat');
    const btnClearHistory = document.getElementById('btn-clear-history');
    const historyItemsList = document.getElementById('history-items-list');

    function saveActiveMessage(role, text) {
        let activeSession = savedSessions.find(s => s.id === currentSessionId);
        if (!activeSession) {
            activeSession = {
                id: currentSessionId,
                title: text.length > 30 ? text.substring(0, 30) + '...' : text,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                messages: []
            };
            savedSessions.unshift(activeSession);
        }

        activeSession.messages.push({
            role: role,
            text: text,
            time: new Date().toLocaleTimeString()
        });

        localStorage.setItem('aria_saved_sessions', JSON.stringify(savedSessions));

        // Sync message to persistent cloud database
        try {
            fetch(`/api/db/history?user_id=${encodeURIComponent(currentUser.id || 'guest_user')}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    role: role,
                    message: text,
                    category: 'chat'
                })
            }).catch(err => {});
        } catch(e) {}

        renderHistoryList();
    }

    function renderHistoryList() {
        if (!historyItemsList) return;

        if (savedSessions.length === 0) {
            historyItemsList.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; padding: 30px 10px;">
                No previous conversation sessions saved yet.<br>Start speaking or typing above to record chat history!
            </div>`;
            return;
        }

        let html = '';
        savedSessions.forEach(session => {
            const isCurrent = session.id === currentSessionId;
            html += `<div class="history-item-card" data-id="${session.id}" style="background: ${isCurrent ? 'rgba(0, 242, 254, 0.15)' : 'rgba(255, 255, 255, 0.04)'}; border: 1px solid ${isCurrent ? 'var(--accent-cyan)' : 'rgba(255, 255, 255, 0.08)'}; padding: 12px 14px; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-weight: 700; font-size: 0.92rem; color: ${isCurrent ? 'var(--accent-cyan)' : 'var(--text-primary)'};">${session.title}</span>
                    <span style="font-size: 0.72rem; color: var(--text-muted);">${session.timestamp}</span>
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${session.messages.length} messages saved</div>
            </div>`;
        });

        historyItemsList.innerHTML = html;

        // Attach Click Listener to Session Cards
        historyItemsList.querySelectorAll('.history-item-card').forEach(card => {
            card.addEventListener('click', () => {
                const sid = card.getAttribute('data-id');
                loadSessionMessages(sid);
            });
        });
    }

    function loadSessionMessages(sessionId) {
        const session = savedSessions.find(s => s.id === sessionId);
        if (!session) return;

        currentSessionId = session.id;
        const logStream = document.getElementById('log-stream');
        if (logStream) {
            logStream.innerHTML = `<div class="log-item system">
                <span class="log-tag">RESTORED SESSION</span>
                <span>Restored session "${session.title}" (${session.messages.length} messages)</span>
            </div>`;
            session.messages.forEach(m => {
                const item = document.createElement('div');
                item.className = `log-item ${m.role}`;
                item.innerHTML = `<span class="log-tag">${m.role.toUpperCase()} • ${m.time}</span><span>${m.text}</span>`;
                logStream.appendChild(item);
            });
            logStream.scrollTop = logStream.scrollHeight;
        }
        renderHistoryList();
        if (historyDrawer) historyDrawer.style.display = 'none';
    }

    function loadHistoryFromStorage() {
        renderHistoryList();
    }

    if (btnToggleHistory) {
        btnToggleHistory.addEventListener('click', () => {
            renderHistoryList();
            if (historyDrawer) historyDrawer.style.display = 'flex';
        });
    }

    if (btnHistoryClose) {
        btnHistoryClose.addEventListener('click', () => {
            if (historyDrawer) historyDrawer.style.display = 'none';
        });
    }

    if (btnNewChat) {
        btnNewChat.addEventListener('click', () => {
            currentSessionId = 'session_' + Date.now();
            const logStream = document.getElementById('log-stream');
            if (logStream) {
                logStream.innerHTML = `<div class="log-item system">
                    <span class="log-tag">NEW SESSION INITIALIZED</span>
                    <span>SpeechRecognition & pyttsx3 engine online.</span>
                </div>`;
            }
            renderHistoryList();
            if (historyDrawer) historyDrawer.style.display = 'none';
            appendLog('system', '✨ Started new conversation session.');
        });
    }

    if (btnClearHistory) {
        btnClearHistory.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete all saved chat history sessions?')) {
                savedSessions = [];
                localStorage.removeItem('aria_saved_sessions');
                currentSessionId = 'session_' + Date.now();
                renderHistoryList();
                appendLog('system', '🧹 Chat history cleared.');
            }
        });
    }

    // Start Dashboard Polling
    updateSystemDashboard();
    setInterval(updateSystemDashboard, 4000);
});
