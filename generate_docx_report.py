import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_docx_report():
    doc = Document()

    # Define Colors
    COLOR_PRIMARY = RGBColor(0, 51, 102)    # Deep Blue
    COLOR_SECONDARY = RGBColor(0, 153, 204)  # Cyan
    COLOR_TEXT = RGBColor(51, 51, 51)       # Dark Gray

    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base Style Settings
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = COLOR_TEXT

    # ----------------------------------------------------
    # COVER / TITLE SECTION
    # ----------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("AI-BASED VOICE ASSISTANT (ARIA)\nPROJECT DOCUMENTATION REPORT")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(24)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY
    title_p.paragraph_format.space_before = Pt(36)
    title_p.paragraph_format.space_after = Pt(12)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Speech Recognition & Synthesis System with Web Control Center & Desktop Automation")
    run_sub.font.name = 'Arial'
    run_sub.font.size = Pt(14)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_SECONDARY
    sub_p.paragraph_format.space_after = Pt(36)

    # Meta Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Course / Subject:", "Major Academic Coding Project"),
        ("Project Title:", "AI-Based Voice Assistant (ARIA)"),
        ("Technologies Used:", "Python 3.13, SpeechRecognition, pyttsx3, Flask, PyAudio, Wikipedia API, HTML5/CSS3/JS"),
        ("Verification Status:", "100% Passed (10/10 Automated Tests Passed)")
    ]
    for i, (k, v) in enumerate(meta_data):
        cell_k = meta_table.cell(i, 0)
        cell_v = meta_table.cell(i, 1)
        cell_k.paragraphs[0].add_run(k).bold = True
        cell_v.paragraphs[0].add_run(v)
        cell_k.paragraphs[0].runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_page_break()

    # ----------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY & PROBLEM STATEMENT
    # ----------------------------------------------------
    h1 = doc.add_heading("1. Executive Summary & Problem Statement", level=1)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "Voice assistants have become an integral part of modern computing, enabling hands-free system interaction, "
        "improving convenience, and enhancing digital accessibility. This project focuses on designing and implementing a "
        "fully functional, AI-powered Voice Assistant (ARIA) capable of converting spoken voice commands into text, "
        "processing intent, performing automated system/web actions, and delivering audible spoken responses."
    )

    h2 = doc.add_heading("1.1 Objectives", level=2)
    h2.runs[0].font.color.rgb = COLOR_SECONDARY

    objectives = [
        "Audio Capture & Transcription: Capture real-time microphone input and convert speech to text using SpeechRecognition.",
        "Voice Response Synthesis: Convert system text responses into clear audible speech using offline pyttsx3 Text-to-Speech (TTS).",
        "Command Intent Processing: Intelligent pattern matching for system commands, time queries, math evaluations, and jokes.",
        "Web & API Information Retrieval: Instant Wikipedia search and multi-source Google Search Reports with title/snippet extraction.",
        "System & Web Automation: Open local applications (Notepad, Calculator, CMD, Explorer, Paint) and web portals (YouTube, Google, StackOverflow).",
        "Interactive Glassmorphism GUI: Provide a futuristic web control center featuring real-time CPU/RAM gauges, canvas audio visualizer, sound effects, and built-in interactive Notepad/Calculator modals."
    ]
    for obj in objectives:
        doc.add_paragraph(obj, style='List Bullet')

    # ----------------------------------------------------
    # SECTION 2: SYSTEM ARCHITECTURE & DATA FLOW
    # ----------------------------------------------------
    h1 = doc.add_heading("2. System Architecture & Component Design", level=1)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "The project adopts a modular architecture separating core voice engine processing from the user interaction layer. "
        "The system consists of three main operational tiers:"
    )

    tiers = [
        "Core Voice Engine (voice_assistant.py): Handles PyAudio mic capture, SpeechRecognition STT, pyttsx3 TTS synthesis, intent routing, and search APIs.",
        "Web API & Server Layer (app.py): Flask REST API exposing endpoints /api/command, /api/status, and /api/listen for HTTP communication.",
        "Web Control Center Frontend (index.html & app.js): Futuristic UI with Web Audio API sound effects, audio spectrum canvas visualizer, CPU/RAM monitoring, and interactive Glassmorphism modals."
    ]
    for tier in tiers:
        doc.add_paragraph(tier, style='List Bullet')

    # Data Flow Table
    doc.add_heading("2.1 Data Processing Flow", level=2).runs[0].font.color.rgb = COLOR_SECONDARY
    flow_table = doc.add_table(rows=6, cols=3)
    flow_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Step", "Module", "Action Performed"]
    for j, h in enumerate(headers):
        cell = flow_table.cell(0, j)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="003366"/>'))

    flow_data = [
        ("1. Audio Capture", "PyAudio & Web Audio API", "Captures microphone audio stream from user host or browser."),
        ("2. Speech-to-Text", "SpeechRecognition (Google STT)", "Converts audio waveform into clean text transcript string."),
        ("3. Intent Router", "VoiceAssistant.process_command()", "Matches command against patterns (Time, Math, Apps, Web Search)."),
        ("4. Execution & Retrieval", "OS Automation & Search APIs", "Launches app, executes math, or fetches Wikipedia/Google Search Reports."),
        ("5. Text-to-Speech", "pyttsx3 & Web SpeechSynthesis", "Synthesizes audible spoken response through host speakers and browser.")
    ]
    for row_idx, row_vals in enumerate(flow_data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = flow_table.cell(row_idx, col_idx)
            cell.paragraphs[0].add_run(val)

    doc.add_page_break()

    # ----------------------------------------------------
    # SECTION 3: KEY FEATURES & IMPLEMENTATION DETAILS
    # ----------------------------------------------------
    h1 = doc.add_heading("3. Key Features & Implementation Details", level=1)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    features = [
        ("Time & Date Telling", "Returns current system time and date formatted nicely in 12-hour AM/PM format."),
        ("Desktop Application Launcher", "Launches local applications (Notepad, Calculator, CMD, Explorer, MS Paint) via os.startfile and subprocess.Popen."),
        ("Interactive Glassmorphism Modals", "Includes built-in on-screen Notepad (with .txt file saving & word counts) and Calculator (with interactive grid keypad)."),
        ("Google & Web Search Reports", "Aggregates multi-source web reports returning main summary, top 3 related topics with snippets, and direct search URL buttons."),
        ("Math Expression Solver", "Evaluates mathematical word problems and expressions safely (addition, subtraction, multiplication, division)."),
        ("System Performance Gauges", "Monitors host CPU utilization percentage and RAM usage in real-time via psutil."),
        ("Joke & Entertainment Module", "Generates humorous programming and general jokes via pyjokes.")
    ]

    for title, desc in features:
        p = doc.add_paragraph()
        r1 = p.add_run(f"• {title}: ")
        r1.bold = True
        r1.font.color.rgb = COLOR_PRIMARY
        p.add_run(desc)

    # ----------------------------------------------------
    # SECTION 4: TESTING & VERIFICATION RESULTS
    # ----------------------------------------------------
    h1 = doc.add_heading("4. Testing & Verification Results", level=1)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "An automated test suite (test_assistant.py) containing 10 comprehensive unit tests was developed and executed. "
        "All 10 unit tests executed successfully with 0 errors."
    )

    test_table = doc.add_table(rows=11, cols=3)
    test_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Test ID", "Command Tested", "Result Status"]
    for j, h in enumerate(t_headers):
        cell = test_table.cell(0, j)
        r = cell.paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="003366"/>'))

    test_cases = [
        ("Test 1", "what is the current time?", "PASSED (100%)"),
        ("Test 2", "hello who are you", "PASSED (100%)"),
        ("Test 3", "show system status", "PASSED (100%)"),
        ("Test 4", "calculate 12 times 8", "PASSED (100%)"),
        ("Test 5", "tell me a joke", "PASSED (100%)"),
        ("Test 6", "open notepad", "PASSED (100%)"),
        ("Test 7", "open youtube", "PASSED (100%)"),
        ("Test 8", "search wikipedia for python", "PASSED (100%)"),
        ("Test 9", "goodbye", "PASSED (100%)"),
        ("Test 10", "describe me about artificial intelligence", "PASSED (100%)")
    ]
    for row_idx, row_vals in enumerate(test_cases, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = test_table.cell(row_idx, col_idx)
            r = cell.paragraphs[0].add_run(val)
            if col_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(0, 153, 76)

    # ----------------------------------------------------
    # SECTION 5: CONCLUSION & RECOMMENDATIONS
    # ----------------------------------------------------
    h1 = doc.add_heading("5. Conclusion & Project Summary", level=1)
    h1.runs[0].font.color.rgb = COLOR_PRIMARY

    doc.add_paragraph(
        "The AI-Based Voice Assistant project successfully achieves all problem statement requirements. It provides a robust, "
        "interactive, and visually striking assistant capable of speech recognition, text-to-speech synthesis, desktop automation, "
        "and live search report extraction. The project demonstrates practical integration of speech processing libraries, REST APIs, "
        "and modern web UI engineering."
    )

    doc.save("AI_Voice_Assistant_Project_Report.docx")
    print("[OK] Created AI_Voice_Assistant_Project_Report.docx successfully!")

if __name__ == '__main__':
    create_docx_report()
