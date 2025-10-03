<!-- <p align="center">
  <img src="images/TL_logo.png" alt="Leaderloop GIF">
</p> -->

# <p style="text-align: center;">  ***Text Loom:***:pencil::thread:  <p>


## :tired_face: Why? 
I was fed up with copying and pasting between an LLM and a text editor when trying to work procedurally with a limited context window (this was early 2024).  
3D VFX has Houdini, images have Nuke, games have Unreal's Blueprint, music has Reaktor, sound has PureData. ***Why is there no node based editor for text?!***
> Well, actually there's Nodysseus (https://nodysseus.io/) and Nodes (https://nodes.io) , but they have different use cases.

## :speech_balloon: What? 
Text Loom is a fun workspace for creating networks that manage queries and build on them.  
All from the comfort of your terminal!

# :page_with_curl: How?

*Text flows from one node to the next.*  
The Text Loom philosophy, it's backend, is all about **text**.  
*Specifically* **lists of text.**  

## Nodes pass text to each other:  
* One node creates text: **([Text](https://github.com/kleer001/Text_Loom/wiki/Text-Node))**
* Some nodes read and write text files: **([FileIn](https://github.com/kleer001/Text_Loom/wiki/FileIn-Node), [FileOut](https://github.com/kleer001/Text_Loom/wiki/FileOut-Node))**
* Some nodes create lists: **([Section](https://github.com/kleer001/Text_Loom/wiki/Section-Node), [Split](https://github.com/kleer001/Text_Loom/wiki/Split-Node),  [MakeList](https://github.com/kleer001/Text_Loom/wiki/MakeList-Node))**
* One node combines lists: **([Merge](https://github.com/kleer001/Text_Loom/wiki/Merge-Node))**
* One node talks to an LLM: **([Query](https://github.com/kleer001/Text_Loom/wiki/Query-Node))**
* One node can contain other nodes and iterate over them in loops: **([Looper](https://github.com/kleer001/Text_Loom/wiki/Looper-Node))**
* And one node does nothing at all except pass the text along: **([Null](https://github.com/kleer001/Text_Loom/wiki/Null-Node))**



## :rocket: Start (automagically)

<code>curl -fsSL https://raw.githubusercontent.com/kleer001/Text_Loom/master/install.sh | bash ; cd Text_Loom </code>
 

## :sparkles: Start (manual) 
<details>
* Make sure you have **git** installed and **python3** (version 3.8 or higher)
* **Clone** the repository  
<code>git clone https://github.com/kleer001/Text_Loom ; cd Text_Loom</code>
* **Create** a local venv  
<code>python3 -m venv .venv</code>
* **Activate** it and set PYTHONPATH  
<code>source .venv/bin/activate ; export PYTHONPATH=\$PYTHONPATH:$(pwd)/src</code>
* **Install** in development mode  
<code>pip install -e .</code>
* **Run** the program  
<code>python3 src/TUI/tui_skeleton.py</code>

Note for Windows users:  
<code>Replace  **source .venv/bin/activate** with **.venv\Scripts\activate**  
and **export PYTHONPATH=\$PYTHONPATH:$(pwd)/src** with **set PYTHONPATH=%PYTHONPATH%;%cd%\src**</code>
</details>


## :package: Currently supported LLMS platforms 
<details>
  
**in  src/core/settings.cfg**

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
</details>

## :walking: GUI WALK THROUGH 
### :eyes: MAIN WINDOW 

<img src="images/mainwin3_trim.gif" alt="Demo of MakeList functionality GIF">


### Primary Workspace
Each Primary window can be navigated to with the keycommand **CTRL+(n/a/g)** 
- [**N**ode Network](#node-network) - Central workspace for creating and connecting nodes. Displays [node](https://github.com/kleer001/Text_Loom/wiki/Nodes,-nodes,-nodes) states, connections, and hierarchies using visual indicators.
- [P**a**rameters](#parameters) - Center Top panel showing properties of selected nodes.
- [**G**lobals](#globals) - Right Top panel. System-wide variables accessible across the network.

### Execution and Output
- **[Output Display](#output-display)** - Center bottom. Shows formatted results from node evaluations with clear item separation.
- **[Status Window](#status-window)** - Right bottom. Real-time system message monitoring, capturing stdout and stderr streams.
- **Help window** - Bottom. Shows the key commands available for the active window.
- **Mode Line** - Gutter. Show the active window, current filename, last window switched to, and keypressed.

---

# Please see the extensive [wiki](https://github.com/kleer001/Text_Loom/wiki) for more detailed information.

