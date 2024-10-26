# ***Text Loom:*** **The unlimited power to procedurally create your text!**


 # :thread: :pencil:


## :speech_balloon: What? 
Text Loom is a workspace to create generalized networks to manage lists and build on them in a way that is stable and  **reliable**. All from the comfort of your favorite local LLM API.


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



'''mermaid

stateDiagram-v2
    Normal: Normal Mode
    direction LR
    
    [*] --> Normal
    
    Normal --> CommandInput: press :
    Normal --> ParamMode: press p
    Normal --> HelpMode: press h
    
    state CommandInput {
        [*] --> Input
        Input --> MenuSelect: press tab
        MenuSelect --> Input: make selection
    }
    
    state ParamMode {
        [*] --> SelectParam
        SelectParam --> EditValue
        EditValue --> SelectParam: press enter
    }
    
    state HelpMode {
        [*] --> ContextHelp
        ContextHelp --> Manual: press m
    }
    
    CommandInput --> Normal: execute/esc
    ParamMode --> Normal: press esc
    HelpMode --> Normal: press q

    note right of Normal
        Status line shows current mode,
        selected node, available commands,
        and context help
    end note

'''