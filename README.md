# Voice-Controlled Local AI Agent

A fully functional voice-controlled AI agent that accepts spoken input and uploaded audio file, classifies user intent using a large language model, executes local system tasks, and displays the entire pipeline in a clean web-based UI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)
![Groq](https://img.shields.io/badge/LLM-Groq-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Supported Intents](#supported-intents)
- [Bonus Features](#bonus-features)
- [Hardware Notes](#hardware-notes)
- [Security](#security)
- [Demo](#demo)

---

## Overview

This project is a local AI agent that listens to your voice, understands what you want, and acts on it — creating files, writing code, summarizing text, or chatting — all from a single voice command. The entire pipeline from audio input to final output is visualized in real time inside a Gradio web interface.

---

## Architecture

```
Audio Input (Microphone or File Upload)
        |
        v
Speech-to-Text  -->  Groq Whisper Large V3
        |
        v
Intent Classification  -->  Groq LLaMA 3.3 70B
        |
        v
Tool Router
   |-- create_file()
   |-- write_code()
   |-- summarize_text()
   |-- general_chat()
        |
        v
Output saved to output/ folder
        |
        v
Gradio UI displays results
```

---

## Features

- Record audio via microphone or upload an existing `.wav` or `.mp3` file
- Speech-to-text transcription using Groq Whisper Large V3
- Intent classification using LLaMA 3.3 70B
- Supports file creation, code generation, text summarization, and general chat
- Human-in-the-loop confirmation before any file operation is executed
- Compound command support — multiple intents handled in a single voice command
- Session memory — chat history and action log persist across turns
- Output file viewer — browse and read generated files directly in the UI
- Download button for any generated file
- Status bar showing the current pipeline state
- Graceful error handling for all edge cases
- All generated files are safely restricted to the `output/` folder

---

## Tech Stack

| Component | Technology |
|---|---|
| UI Framework | Gradio |
| Speech-to-Text | Groq Whisper Large V3 |
| Intent Classification | Groq LLaMA 3.3 70B Versatile |
| Code Generation | Groq LLaMA 3.3 70B Versatile |
| Language | Python 3.10+ |
| Audio Processing | SciPy, NumPy, SoundDevice |
| Environment Management | python-dotenv |

---

## Project Structure

```
voice-ai-agent/
├── agent/
│   ├── __init__.py        # Marks agent as a Python module
│   ├── stt.py             # Speech-to-text via Groq Whisper
│   ├── intent.py          # Intent classification via LLaMA 3.3
│   ├── tools.py           # Tool execution: file, code, summarize, chat
│   └── memory.py          # Session memory and action log
├── output/                # All generated files are saved here
│   └── .gitkeep           # Keeps folder tracked by Git
├── .env                   # API key — not uploaded to GitHub
├── .gitignore             # Ignores .env, venv, __pycache__
├── app.py                 # Main Gradio UI and pipeline logic
├── requirements.txt       # All Python dependencies
└── README.md              # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher


### 1. Clone the Repository

```bash
git clone https://github.com/VASU52261/voice-ai-agent.git
cd voice-ai-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root of the project and add your Groq API key.




### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to:

```
http://127.0.0.1:7860
```

---

## Usage

Record audio using your microphone or upload a `.wav` / `.mp3` file, then click **Run Agent**. For file and code operations, a confirmation step will appear before anything is written to disk.

### Example Commands

| Voice Command | Expected Intent |
|---|---|
| "Write a Python file called calculator.py with add and subtract functions" | `write_code` |
| "Create a file called notes.txt" | `create_file` |
| "Summarize this text: AI is transforming industries around the world" | `summarize_text` |
| "Summarize this text and save it to summary.txt: Python is a popular language" | `summarize_text` + `write_code` |
| "What is machine learning?" | `general_chat` |

---

## Supported Intents

### `create_file`
Creates an empty file or a file with basic content in the `output/` folder.

**Example:** _"Create a file called notes.txt"_

### `write_code`
Generates code using LLaMA 3.3 and saves it to a file in the `output/` folder.

**Example:** _"Write a Python file called sort.py with a bubble sort function"_

### `summarize_text`
Summarizes the provided text and displays the result. Can also save the summary to a file if a filename is mentioned in the command.

**Example:** _"Summarize this text: Artificial intelligence is changing the world"_

### `general_chat`
Handles any general question or conversation that does not match the other intents.

**Example:** _"What is the difference between Python and JavaScript?"_

---

## Bonus Features

### Compound Commands
The agent supports multiple intents in a single voice command. For example, saying _"Summarize this text and save it to summary.txt"_ triggers both `summarize_text` and `write_code` in a single pipeline run.

### Human-in-the-Loop
Before executing any file operation such as `create_file` or `write_code`, the agent pauses and asks the user to confirm by clicking the **Confirm & Execute** button. This prevents accidental file creation.

### Session Memory
The agent maintains a persistent history of all actions and chat context within the session. This allows the LLM to refer back to previous messages for context-aware responses.

### Graceful Degradation
All errors are caught and displayed cleanly in the UI without crashing the application. If the intent cannot be parsed, the agent defaults to `general_chat` instead of failing.

---

## Hardware Notes

The assignment recommends using a local HuggingFace Whisper model for speech-to-text. However, running Whisper locally requires a CUDA-compatible GPU with sufficient VRAM (at least 4 GB for the base model, 10 GB+ for large-v3).

This machine does not have a dedicated GPU capable of running Whisper efficiently. Therefore, the Groq API was used to access `whisper-large-v3`, which provides:

- Sub-second transcription latency
- Higher accuracy than smaller local Whisper models
- Free tier access at no cost

This is a documented and accepted workaround per the assignment brief.

The LLM used for intent classification and code generation is `llama-3.3-70b-versatile`, also accessed via the Groq API. A local model via Ollama or LM Studio was considered, but Groq provides significantly faster inference with equivalent output quality.

---

## Security

All file creation and code writing operations are strictly restricted to the `output/` folder inside the repository. The tool execution code uses `os.path.basename()` to strip any directory traversal attempts, ensuring no files can be written outside the designated folder.

The `.env` file containing the API key is listed in `.gitignore` and is never uploaded to GitHub.

---

## Demo

- **Video Demo:** [Watch on YouTube](#) — _update this link after recording_
- **GitHub Repository:** [github.com/VASU52261/voice-ai-agent](https://github.com/VASU52261/voice-ai-agent)
