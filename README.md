# agentmakestudio

AgentMake AI Studio - Web UI built for working with [AgentMake AI](https://github.com/eliranwong/agentmake)

![Image](https://github.com/user-attachments/assets/3e8dbe05-855d-4c0a-a581-bc262443b452)

# Install

> pip install --upgrade agentmakestudio

To support Vertex AI:

> pip install --upgrade "agentmakestudio[genai]"

# Export Path

To export Path for running AgentMake and AgentMake Studio, assuming you install `agentmakestudio` in a virtual environment `ai`, e.g.:

```
cd
python3 -m venv ai
source ai/bin/activate
pip install --upgrade "agentmake[studio,genai]"
echo export "PATH=$PATH:$(pwd)/ai/bin" >> ~/.bashrc
```

# Configurations

To configure AgentMake AI backends, like API keys, run:

> ai -ec

# Run

> agentmakestudio

Open `http://localhost:32123` in a web browser.

# Run with Custom Port

For example, use port 33333

> agentmakestudio --port 33333

Open `http://localhost:33333` in a web browser.

# Auto Run

Below is an example bash script that runs `agentmakestudio` automatically:

https://github.com/eliranwong/agentmakestudio/blob/main/README.md

You may place the content script in, e.g. `~/.bashrc`

# Usage

Enter your prompt and get a response.

Use the menu items to specify [agentic components](https://github.com/eliranwong/agentmake#introducing-agentic-components) optionally.

The following shortcuts are supported for specifying agent, tool, system, instruction in a single turn. These shortcuts work only if there is no agent being selected in the menu and you declar a shortcut at the beginning of your prompt:

* agent - `@@` followed by an agent name, e.g. `@@reasoning`

* tool - `@` followed by a tool name, e.g. `@magic`

* system - `++` followed by a system name, e.g. `++auto`

* instruction - `+` followed by an instruction name, e.g. `+think`

# Read more

https://github.com/eliranwong/agentmake