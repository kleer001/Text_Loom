# ***Text Loom:*** :thread: :pencil:
# **The unlimited power to procedurally create your text!**

## :speech_balloon: What? 
Text Loom is a new way to work with LLMs. Batch processing!  
Text Loom is a fun little workspace to create networks to manage queries and build on them in a way that is stable and  **reliable**. All from the comfort of your terminal!


# :bulb: Why?

<details>
  <summary>Enhance LLM Capabilities & Streamline Workflow</summary>

- Develop a solution that enables (local and remote) LLMs to generate long and complex multistep outputs effectively, such as detailed learning programs or comprehensive critiques or flesh out novel length ideas.

- Eliminate the need for manual copy-pasting in workflows to improve efficiency and maintain the quality of generated content while trying new things.

</details>

<details>
  <summary>Create a Custom Solution</summary>

- Leverage insights from experts like Jonathan Mast to design a tailored programming solution that integrates the strengths of LLMs and utilizes innovative tools like [Gradio](https://www.gradio.app/) and inspiration from [Automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

</details>

<details>
  <summary>Contribute to the Community</summary>

- Actively participate in the local LLM evolution among programmers and users who share a passion for generating text and exploring the capabilities of LLMs and enhancing the ease of the chat workflow.

</details>

## :rocket: Start (automagically)

<code>curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash ; cd cuesubplot </code>
 

## :sparkles: Start (manual) 
* Make sure you have **git** installed (and **python3**, at least 3.8)
* **Copy** the repo  
<code>git clone https://github.com/kleer001/Text_Loom ; cd Text_Loom </code>
* **Create** a local venv
* <code> python3 -m venv venv </code>
* **Activate** it
* <code> source venv/bin/activate </code>
* **Install** the dependencies  
<code> pip install textual </code>
* **Run** the program  
<code> python3 src/TUI/tui_skeleon.py</code>



## :package: Currently supported LLMS platforms 
*in  src/core/settings.cfg*  

| LLM Platform | URL                                    | Endpoint                                     |
|--------------|----------------------------------------|----------------------------------------------|
| Ollama       | localhost:11434                        | /api/generate                                |
| LM Studio    | localhost:1234                         | /v1/chat/completions                         |
| GPT4All      | localhost:4891                         | /v1/completions                              |
| LocalAI      | localhost:8080                         | /v1/chat/completions                         |
| llama.cpp    | localhost:8080                         | /completion                                  |
| oobabooga    | localhost:5000                         | /v1/chat/completions                         |
| ChatGPT      | https://api.openai.com                 | /v1/chat/completions                         |
| Perplexity   | https://api.perplexity.ai             | /v1/chat/completions                         |
| Claude       | https://api.anthropic.com              | /v1/messages                                 |
| Gemini       | https://generativelanguage.googleapis.com | /v1/models/gemini-1.5-pro:generateContent   |

* Please suggest more free local LLMs if you like. And feel free to change your local settings.cfg to fit your own purposes. The structure should be self-evident from the examples in it.  


## :walking: GUI WALK THROUGH 
### :eyes: MAIN WINDOW 