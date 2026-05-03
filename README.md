# Lilu — Personal AI Assistant

Lilu is a powerful, terminal-based AI assistant designed to help you with a wide variety of tasks. Built with Python, Lilu supports multiple LLM providers (OpenAI, Groq), features a robust tool integration system, and offers optional capabilities like voice interaction and semantic memory.

## 🌟 Features

* **Dual LLM Support**: Uses OpenAI as the primary provider (for the best function calling) with a fallback to Groq for fast, free inference.
* **Extensive Tool Integration**:
  * 🌐 **Web Search**: Integrated with DuckDuckGo for real-time information retrieval.
  * 💻 **Python Execution**: Run Python code safely.
  * 📂 **File Operations**: Read, write, and manage local files.
  * 📅 **Google Calendar**: View and manage calendar events.
  * 📝 **Notion API**: Interact with your Notion databases.
  * ⚙️ **System Info**: Check local system resources and status.
* **Voice Capabilities (Optional)**: Support for Edge TTS (Text-to-Speech) and Whisper (Speech-to-Text).
* **Rich Terminal UI**: Beautiful, markdown-rendered terminal outputs using the `rich` library.

## 📋 Prerequisites

* Python 3.10+
* An API Key from [OpenAI](https://platform.openai.com/account/api-keys) OR [Groq](https://console.groq.com/keys).

## 🚀 Installation

1. **Navigate to the project directory:**
   Ensure you are in the root directory of the project (e.g., `Jarvis`).

2. **Create and activate a virtual environment (Recommended):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install Core Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install Optional Dependencies (If needed):**
   Open `requirements.txt` to see uncommented packages for Voice, Web UI, Memory (ChromaDB), and API integrations, and install them based on the features you want to enable.

## ⚙️ Configuration

1. **Set up your environment variables:**
   Copy the provided `.env.example` file to create a new `.env` file:
   ```powershell
   cp .env.example .env
   ```

2. **Add your API Keys:**
   Open the `.env` file and replace the placeholder values with your actual API keys. 
   
   *Note: If you are only using Groq, you can leave `OPENAI_API_KEY` blank and just fill in `GROQ_API_KEY`.*

   ```env
   OPENAI_API_KEY=sk-your-real-openai-key
   GROQ_API_KEY=gsk_your-real-groq-key
   ```

3. **Configure Optional Integrations:**
   In the same `.env` file, you can enable/disable voice, memory, and configure Google/Notion credentials if you wish to use those tools.

## 💻 Usage

To start Lilu, simply run the `main.py` file using your virtual environment's Python executable:

```powershell
python main.py
```
*(If your virtual environment is not activated, use `.\.venv\Scripts\python.exe main.py`)*

Once started, you will see a "System Online" banner. You can type your requests directly into the terminal and chat with Lilu. Type `exit` or `quit` to stop the application.

## 📁 Project Structure

* `main.py`: The main entry point for the terminal assistant.
* `config.py`: Configuration loader and validator.
* `core/`: Core orchestrator and LLM communication logic.
* `tools/`: Extensible tools that Lilu can use (Search, Files, Notion, Calendar, etc.).
* `memory/`: Storage directory for conversation history and user profiles.
* `voice/`: Optional Text-to-Speech and Speech-to-Text handlers.
