import gradio as gr
import scipy.io.wavfile as wav
import tempfile
import os
from agent.stt import transcribe_audio
from agent.intent import classify_intent
from agent.tools import execute_intent
from agent.memory import SessionMemory

memory = SessionMemory()
PENDING = {}
OUTPUT_DIR = "output"

def get_output_files():
    if not os.path.exists(OUTPUT_DIR):
        return []
    files = os.listdir(OUTPUT_DIR)
    return [os.path.join(OUTPUT_DIR, f) for f in files if os.path.isfile(os.path.join(OUTPUT_DIR, f))]

def view_selected_file(filepath):
    if not filepath:
        return "", gr.update(value=None, visible=False)
    try:
        with open(filepath, "r") as f:
            content = f.read()
        return content, gr.update(value=filepath, visible=True)
    except:
        return "Could not read file.", gr.update(value=None, visible=False)

def refresh_files():
    return gr.update(choices=get_output_files())

def process_audio(audio_input, confirmed=False):
    global PENDING

    try:
        if confirmed:
            if not PENDING:
                return ("", "", "", "Nothing to confirm. Please record audio first.", gr.update(visible=True), memory.get_log_display(), gr.update(choices=get_output_files()), "Ready.")
            intent_data = PENDING["intent_data"]
            transcription = PENDING["transcription"]
            PENDING.clear()

            results = execute_intent(intent_data, memory.history)
            memory.add_turn(transcription, intent_data, results)
            output_text = format_results(results)

            return (
                transcription,
                ", ".join(intent_data.get("intents", [])),
                intent_data.get("explanation", ""),
                output_text,
                gr.update(visible=True),
                memory.get_log_display(),
                gr.update(choices=get_output_files()),
                "Done. Files updated."
            )

        if audio_input is None:
            return ("", "", "", "Please record or upload audio first.", gr.update(visible=True), memory.get_log_display(), gr.update(choices=get_output_files()), "Waiting for input.")

        if isinstance(audio_input, tuple):
            sr, data = audio_input
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav.write(tmp.name, sr, data)
            audio_path = tmp.name
        else:
            audio_path = audio_input

        transcription = transcribe_audio(audio_path)

        intent_data = classify_intent(transcription)
        intents = intent_data.get("intents", [])
        intents_str = ", ".join(intents)
        explanation = intent_data.get("explanation", "")

        file_intents = {"create_file", "write_code"}
        needs_confirm = any(i in file_intents for i in intents)

        if needs_confirm:
            PENDING["intent_data"] = intent_data
            PENDING["transcription"] = transcription
            return (
                transcription,
                intents_str,
                explanation,
                "File operation detected. Click Confirm & Execute to proceed.",
                gr.update(visible=True),
                memory.get_log_display(),
                gr.update(choices=get_output_files()),
                "Waiting for confirmation."
            )

        results = execute_intent(intent_data, memory.history)
        memory.add_turn(transcription, intent_data, results)
        output_text = format_results(results)

        return (
            transcription,
            intents_str,
            explanation,
            output_text,
            gr.update(visible=True),
            memory.get_log_display(),
            gr.update(choices=get_output_files()),
            "Done."
        )

    except Exception as e:
        return (
            "",
            "",
            "",
            f"Error: {str(e)}",
            gr.update(visible=True),
            memory.get_log_display(),
            gr.update(choices=get_output_files()),
            f"Error: {str(e)}"
        )

def format_results(results):
    output_text = ""
    for r in results:
        output_text += f"**{r['intent']}** — {r.get('message', '')}\n\n"
        if "code" in r:
            code_preview = r["code"][:500] + "\n..." if len(r["code"]) > 500 else r["code"]
            output_text += f"```\n{code_preview}\n```\n\n"
        if "summary" in r:
            output_text += f"{r['summary']}\n\n"
        if "reply" in r:
            output_text += f"{r['reply']}\n\n"
    return output_text.strip()

def reset_ui():
    global PENDING
    PENDING = {}
    return (
        None,
        "",
        "",
        "",
        "*Output will appear here after execution.*",
        gr.update(visible=True),
        memory.get_log_display(),
        gr.update(choices=get_output_files()),
        "Ready."
    )

# ---- Custom CSS ----
custom_css = """
body { font-family: 'Segoe UI', sans-serif; }
#title { text-align: center; font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; }
#subtitle { text-align: center; font-size: 1rem; color: gray; margin-bottom: 1.5rem; }
#run-btn { width: 100%; margin-top: 10px; border-radius: 8px; font-size: 1rem; }
#confirm-btn { width: 100%; margin-top: 6px; border-radius: 8px; }
#reset-btn { width: 100%; margin-top: 6px; border-radius: 8px; }
#status-bar { padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; background: #1e1e2e; color: #aaa; border: 1px solid #333; margin-bottom: 10px; }
"""

# ---- UI ----
with gr.Blocks(title="Voice AI Agent", css=custom_css) as demo:

    gr.Markdown("# Voice-Controlled AI Agent", elem_id="title")
    gr.Markdown("Speak or upload audio — the agent will transcribe, understand your intent, and act.", elem_id="subtitle")

    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="numpy",
                label="Audio Input"
            )
            run_btn = gr.Button("Run Agent", variant="primary", elem_id="run-btn")
            confirm_btn = gr.Button("Confirm & Execute", variant="secondary", elem_id="confirm-btn", visible=True)
            reset_btn = gr.Button("New Command (Clear)", variant="stop", elem_id="reset-btn")

        with gr.Column(scale=2):
            status_bar = gr.Textbox(
                value="Ready. Record or upload audio to begin.",
                label="Status",
                interactive=False,
                elem_id="status-bar",
                lines=1
            )
            gr.Markdown("### Pipeline Results")
            transcription_box = gr.Textbox(
                label="Transcription",
                interactive=False,
                placeholder="Your spoken text will appear here..."
            )
            intent_box = gr.Textbox(
                label="Detected Intent",
                interactive=False,
                placeholder="Detected intent will appear here..."
            )
            explanation_box = gr.Textbox(
                label="Explanation",
                interactive=False,
                placeholder="What the agent understood..."
            )
            output_box = gr.Markdown(value="*Output will appear here after execution.*")

    gr.Markdown("---")
    gr.Markdown("### Output Files")
    with gr.Row():
        with gr.Column(scale=1):
            file_dropdown = gr.Dropdown(
                choices=get_output_files(),
                label="Select a file to view",
                interactive=True
            )
            refresh_btn = gr.Button("Refresh Files")
        with gr.Column(scale=2):
            file_content_box = gr.Code(
                label="File Content",
                language=None,
                interactive=False,
                lines=12
            )
            download_file = gr.File(
                label="Download Selected File",
                visible=False,
                interactive=False
            )

    gr.Markdown("---")
    gr.Markdown("### Session History")
    history_box = gr.Markdown("*No history yet. Run a command to get started.*")

    run_btn.click(
        fn=lambda audio: process_audio(audio, confirmed=False),
        inputs=[audio_input],
        outputs=[transcription_box, intent_box, explanation_box, output_box, confirm_btn, history_box, file_dropdown, status_bar]
    )

    confirm_btn.click(
        fn=lambda: process_audio(None, confirmed=True),
        inputs=[],
        outputs=[transcription_box, intent_box, explanation_box, output_box, confirm_btn, history_box, file_dropdown, status_bar]
    )

    reset_btn.click(
        fn=reset_ui,
        inputs=[],
        outputs=[audio_input, transcription_box, intent_box, explanation_box, output_box, confirm_btn, history_box, file_dropdown, status_bar]
    )

    file_dropdown.change(
        fn=view_selected_file,
        inputs=[file_dropdown],
        outputs=[file_content_box, download_file]
    )

    refresh_btn.click(
        fn=refresh_files,
        inputs=[],
        outputs=[file_dropdown]
    )

if __name__ == "__main__":
    demo.launch()
