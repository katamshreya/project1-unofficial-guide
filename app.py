"""Gradio web interface for the Unofficial Guide RAG system.

Thin UI layer over generate.ask(): takes a question, shows the grounded answer
and the source files it was drawn from.

Run with:

    python app.py
"""

import gradio as gr

from generate import ask


def answer_question(question: str):
    """Adapter between the Gradio textboxes and generate.ask()."""
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(result["sources"]) if result["sources"] else "(none)"
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask about UT Austin CS professors and courses. Answers come only "
        "from student reviews and Reddit threads in the document set."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about Mike Scott's exams?",
    )
    btn = gr.Button("Ask", variant="primary")

    answer_out = gr.Textbox(label="Answer", lines=8)
    sources_out = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(answer_question, inputs=inp, outputs=[answer_out, sources_out])
    inp.submit(answer_question, inputs=inp, outputs=[answer_out, sources_out])


if __name__ == "__main__":
    demo.launch()
