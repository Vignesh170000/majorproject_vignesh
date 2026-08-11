import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_pptx_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette (Dark Theme / Cyberpunk Cyan)
    BG_DARK = RGBColor(10, 15, 30)
    ACCENT_CYAN = RGBColor(0, 242, 254)
    ACCENT_PURPLE = RGBColor(127, 0, 255)
    TEXT_LIGHT = RGBColor(240, 246, 252)
    TEXT_MUTED = RGBColor(139, 148, 158)

    blank_layout = prs.slide_layouts[6]

    def add_dark_slide(title_text=""):
        slide = prs.slides.add_slide(blank_layout)
        
        # Dark Background shape
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()

        if title_text:
            title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.9))
            tf = title_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title_text
            p.font.name = 'Arial'
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN

        return slide

    # ----------------------------------------------------
    # SLIDE 1: Title Slide
    # ----------------------------------------------------
    slide1 = add_dark_slide()
    tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "AI-BASED VOICE ASSISTANT (ARIA)"
    p1.font.name = 'Arial'
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_CYAN
    p1.alignment = PP_ALIGN.CENTER

    p2 = tf1.add_paragraph()
    p2.text = "Speech Recognition, Text-to-Speech Synthesis & Web Control Center"
    p2.font.name = 'Arial'
    p2.font.size = Pt(20)
    p2.font.color.rgb = TEXT_LIGHT
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf1.add_paragraph()
    p3.text = "\nMajor Academic Project Presentation  |  Python 3.13 • SpeechRecognition • pyttsx3 • Flask"
    p3.font.name = 'Arial'
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED
    p3.alignment = PP_ALIGN.CENTER

    # ----------------------------------------------------
    # SLIDE 2: Problem Statement & Objectives
    # ----------------------------------------------------
    slide2 = add_dark_slide("Problem Statement & Objectives")
    tb2 = slide2.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    items2 = [
        ("Problem Statement", "Voice assistants enable users to perform tasks via spoken voice commands, boosting productivity and accessibility. This project builds a complete smart voice assistant simulating real-world AI capabilities."),
        ("Key Objectives", "1. Capture real-time microphone audio and convert speech to text.\n2. Intelligently match and process voice command intent.\n3. Execute automated system actions (open apps, calculate math, check status).\n4. Deliver clear audible voice responses using offline TTS engine.\n5. Provide a high-aesthetic interactive web control center.")
    ]
    for heading, text in items2:
        p_head = tf2.add_paragraph()
        p_head.text = heading
        p_head.font.size = Pt(20)
        p_head.font.bold = True
        p_head.font.color.rgb = ACCENT_PURPLE

        p_desc = tf2.add_paragraph()
        p_desc.text = text
        p_desc.font.size = Pt(15)
        p_desc.font.color.rgb = TEXT_LIGHT
        p_desc.space_after = Pt(16)

    # ----------------------------------------------------
    # SLIDE 3: System Architecture & Tech Stack
    # ----------------------------------------------------
    slide3 = add_dark_slide("System Architecture & Technology Stack")
    tb3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    tech_stack = [
        ("Python 3.13", "Core programming language for assistant engine, intent routing, and backend services."),
        ("SpeechRecognition & PyAudio", "Handles real-time microphone stream capture and Google Speech-to-Text transcription."),
        ("pyttsx3 Voice Engine", "Offline text-to-speech synthesis engine providing natural audio feedback."),
        ("Flask REST Framework", "Serves Web Control Center at http://localhost:5000 with REST API endpoints."),
        ("HTML5, CSS3, JavaScript", "Futuristic Glassmorphic Dark UI, Web Audio API sound synth, and interactive modals.")
    ]
    for tech, desc in tech_stack:
        p = tf3.add_paragraph()
        r1 = p.add_run()
        r1.text = f"- {tech}: "
        r1.font.bold = True
        r1.font.size = Pt(17)
        r1.font.color.rgb = ACCENT_CYAN

        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(15)
        r2.font.color.rgb = TEXT_LIGHT
        p.space_after = Pt(10)

    # ----------------------------------------------------
    # SLIDE 4: Voice Processing Pipeline
    # ----------------------------------------------------
    slide4 = add_dark_slide("Speech Recognition & Response Pipeline")
    tb4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    steps = [
        ("Step 1: Audio Input Capture", "Microphone stream captured via PyAudio (31 channels supported) or Browser Web Audio API."),
        ("Step 2: Speech-to-Text (STT)", "Audio processed by SpeechRecognition engine converting vocal waveform into text transcript."),
        ("Step 3: Intent Routing", "Pattern matching routes text to specific module (Time, Math, App Launcher, Web Search)."),
        ("Step 4: Action Execution", "Launches local app, computes math, queries Wikipedia, or fetches Google Search Reports."),
        ("Step 5: Spoken Audio Response", "Response spoken out loud orally via pyttsx3 host speakers and Web Speech Synthesis.")
    ]
    for step_title, step_desc in steps:
        p = tf4.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{step_title} -> "
        r1.font.bold = True
        r1.font.size = Pt(16)
        r1.font.color.rgb = ACCENT_CYAN

        r2 = p.add_run()
        r2.text = step_desc
        r2.font.size = Pt(14)
        r2.font.color.rgb = TEXT_LIGHT
        p.space_after = Pt(8)

    # ----------------------------------------------------
    # SLIDE 5: Core Assistant Features
    # ----------------------------------------------------
    slide5 = add_dark_slide("Core Functional Features")
    tb5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    features5 = [
        "[TIME] Time & Date Engine: Tells current time and date in formatted 12-hour AM/PM format.",
        "[APPS] System App Launcher: Launches Notepad, Calculator, Command Prompt, MS Paint, and Explorer.",
        "[MATH] Math Solver: Solves complex mathematical word problems and algebraic expressions.",
        "[SEARCH] Search Reports: Extracts Wikipedia summaries and multi-topic Google Search Reports.",
        "[STATS] System Stats: Live monitoring of host CPU load percentage and RAM utilization.",
        "[JOKES] Entertainment: Generates humorous programming and general jokes via pyjokes."
    ]
    for feat in features5:
        p = tf5.add_paragraph()
        p.text = feat
        p.font.size = Pt(17)
        p.font.color.rgb = TEXT_LIGHT
        p.space_after = Pt(12)

    # ----------------------------------------------------
    # SLIDE 6: Ultra-Interactive Web Dashboard
    # ----------------------------------------------------
    slide6 = add_dark_slide("Ultra-Interactive Web Control Center UI")
    tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    ui_feats = [
        ("Glassmorphic Dark Mode", "Futuristic neon layout with self-contained SVG graphics and smooth animations."),
        ("Canvas Audio Visualizer", "Dynamic audio spectrum visualizer animating live voice waveforms."),
        ("Top Hero Result Banner", "Prominent display card rendering instant AI text answers and web links right below input."),
        ("Web Audio Synthesizer", "Generates acoustic feedback beeps and success chimes using Web Audio API oscillator tones."),
        ("Real-time Gauges", "Dynamic animated progress gauges for host CPU load and RAM usage.")
    ]
    for u1, u2 in ui_feats:
        p = tf6.add_paragraph()
        r1 = p.add_run()
        r1.text = f"- {u1}: "
        r1.font.bold = True
        r1.font.size = Pt(17)
        r1.font.color.rgb = ACCENT_CYAN

        r2 = p.add_run()
        r2.text = u2
        r2.font.size = Pt(15)
        r2.font.color.rgb = TEXT_LIGHT
        p.space_after = Pt(10)

    # ----------------------------------------------------
    # SLIDE 7: Built-in Interactive Modals
    # ----------------------------------------------------
    slide7 = add_dark_slide("Built-in Interactive Modals (Notepad & Calculator)")
    tb7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    modal_items = [
        ("Interactive Glassmorphism Notepad Modal (#notepad-modal)", "- Opens instantly on screen when user clicks or speaks 'Open Notepad'.\n- Real-time character & word counters.\n- Includes Save File button (downloads notes directly as notes.txt).\n- Includes Copy to Clipboard and Clear actions."),
        ("Interactive Glassmorphism Calculator Modal (#calculator-modal)", "- Responsive grid keypad with 0-9, operators (+, -, *, /), =, C, Backspace.\n- Real-time equation solver displaying inputs and results on screen.")
    ]
    for m_title, m_desc in modal_items:
        p1 = tf7.add_paragraph()
        p1.text = m_title
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_PURPLE

        p2 = tf7.add_paragraph()
        p2.text = m_desc
        p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_LIGHT
        p2.space_after = Pt(14)

    # ----------------------------------------------------
    # SLIDE 8: Testing & Verification
    # ----------------------------------------------------
    slide8 = add_dark_slide("Testing & Verification Results (10/10 Passed)")
    tb8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    p_t = tf8.add_paragraph()
    p_t.text = "Automated Unit Test Suite Execution (test_assistant.py):"
    p_t.font.size = Pt(18)
    p_t.font.bold = True
    p_t.font.color.rgb = ACCENT_CYAN
    p_t.space_after = Pt(10)

    tests_list = [
        "[PASS] Test 1: Time Command ('what is the current time?') -> PASSED",
        "[PASS] Test 2: Greeting Identity ('hello who are you') -> PASSED",
        "[PASS] Test 3: System Status ('show system status') -> PASSED",
        "[PASS] Test 4: Math Solver ('calculate 12 times 8') -> PASSED",
        "[PASS] Test 5: Joke Module ('tell me a joke') -> PASSED",
        "[PASS] Test 6: App Launcher ('open notepad') -> PASSED",
        "[PASS] Test 7: Web Launcher ('open youtube') -> PASSED",
        "[PASS] Test 8: Wikipedia Search ('search wikipedia for python') -> PASSED",
        "[PASS] Test 9: Goodbye Exit ('goodbye') -> PASSED",
        "[PASS] Test 10: Google Search Report ('describe me about artificial intelligence') -> PASSED"
    ]
    for t_item in tests_list:
        p = tf8.add_paragraph()
        p.text = t_item
        p.font.size = Pt(14)
        p.font.color.rgb = TEXT_LIGHT
        p.space_after = Pt(4)

    # ----------------------------------------------------
    # SLIDE 9: Future Scope & Conclusion
    # ----------------------------------------------------
    slide9 = add_dark_slide("Future Scope & Conclusion")
    tb9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.2))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    future_items = [
        ("Future Scope Enhancements", "1. Integration with Large Language Models (LLMs) for conversational context.\n2. Smart Home IoT Automation (controlling smart lights & devices).\n3. Multi-language voice translation & voice cloning."),
        ("Conclusion", "The AI Voice Assistant (ARIA) project successfully meets all problem statement goals. It demonstrates robust speech recognition, offline text-to-speech synthesis, desktop application launcher capabilities, and a state-of-the-art web interface.")
    ]
    for f_title, f_desc in future_items:
        p1 = tf9.add_paragraph()
        p1.text = f_title
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_PURPLE

        p2 = tf9.add_paragraph()
        p2.text = f_desc
        p2.font.size = Pt(15)
        p2.font.color.rgb = TEXT_LIGHT
        p2.space_after = Pt(16)

    # ----------------------------------------------------
    # SLIDE 10: Thank You
    # ----------------------------------------------------
    slide10 = add_dark_slide()
    tb10 = slide10.shapes.add_textbox(Inches(1.0), Inches(2.5), Inches(11.333), Inches(3.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p_end1 = tf10.paragraphs[0]
    p_end1.text = "THANK YOU!"
    p_end1.font.name = 'Arial'
    p_end1.font.size = Pt(48)
    p_end1.font.bold = True
    p_end1.font.color.rgb = ACCENT_CYAN
    p_end1.alignment = PP_ALIGN.CENTER

    p_end2 = tf10.add_paragraph()
    p_end2.text = "Questions & Answers (Q&A)"
    p_end2.font.name = 'Arial'
    p_end2.font.size = Pt(24)
    p_end2.font.color.rgb = TEXT_LIGHT
    p_end2.alignment = PP_ALIGN.CENTER

    prs.save("AI_Voice_Assistant_Presentation.pptx")
    print("[OK] Created AI_Voice_Assistant_Presentation.pptx successfully!")

if __name__ == '__main__':
    create_pptx_presentation()
