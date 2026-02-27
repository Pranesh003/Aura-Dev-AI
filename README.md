# Aura-Dev-AI 🚀

Aura-Dev-AI is a powerful, multi-agent AI development framework designed to automate and enhance the software development lifecycle. Built with **CrewAI** and powered by **Google Gemini** and **OpenAI**, it orchestrates a team of specialized AI agents to handle everything from architectural design to code generation and auditing.

## 🌟 Key Features

- **Multi-Agent Orchestration**: Specialized agents for Architecting, Coding, Auditing, and more.
- **Resilient LLM Engine**: Advanced model rotation and retry logic to ensure high availability and performance, supporting both Google Gemini and OpenAI models.
- **Vision Integration**: Capabilities to analyze UI designs and sketches for front-end generation.
- **Automated Workflows**: Streamlined processes for project initialization, development, and verification.
- **Modern UI**: Intuitive front-end built with Vite and React, alongside a Streamlit-based agentic workflow interface.
- **Sustainability Focus**: Includes a "Green AI" auditor to evaluate energy efficiency and carbon footprint.

## 🏗️ Project Structure

```text
aura-dev-ai/
├── agents.py           # Definition of specialized AI agents
├── tasks.py            # Task definitions for agents
├── crew_flow.py        # CrewAI orchestration logic
├── direct_flow.py      # Main execution flow and direct processing
├── resilient_engine.py # Hardened LLM interaction layer
├── tools.py            # Custom tools for agents
├── app.py              # Streamlit dashboard/interface for Agentic Workflow
├── backend/            # FastAPI backend services
│   └── main.py         # Backend entry point
├── frontend/           # Vite + React frontend application
└── requirements.txt    # Python dependencies
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js & npm (for frontend)
- Google Gemini API Key(s)
- OpenAI API Key (optional, for fallback/specific models)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Pranesh003/Aura-Dev-AI.git
   cd Aura-Dev-AI
   ```

2. **Set up Python environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory and add your API keys:

   ```env
   # Primary
   GOOGLE_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key

   # Optional: Additional keys for rotation/resilience
   GOOGLE_API_KEY_2=...
   GOOGLE_API_KEY_3=...
   ```

### 🚀 Running the Application

You can run Aura-Dev-AI in two modes:

#### Option 1: Streamlit Agentic Workflow

This mode provides a direct interface to the 7-Agent Core Dominion, allowing you to upload sketches and generate full projects.

```bash
streamlit run app.py
```

#### Option 2: Web Interface (FastAPI + React)

This mode provides a full IDE-like experience with a file explorer and editor.

1. **Start the Backend**:
   ```bash
   python backend/main.py
   ```
   The backend will run on `http://localhost:8000`.

2. **Start the Frontend**:
   Open a new terminal window:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`.

## 🤖 Agents & Roles

- **Lead Multimodal Vision Architect**: Converts abstract visual sketches into deep-reasoning engineering blueprints.
- **System Architect**: Designs robust software architectures.
- **Senior Autonomous Full-Stack Engineer**: Writes high-quality, production-ready, PEP8-compliant code.
- **Autonomous Debugging Engineer**: Detects and fixes syntax errors, missing imports, and logic bottlenecks.
- **Performance Optimization Specialist**: Identifies heavy dependencies and suggests lightweight alternatives.
- **Cognitive Load & DX Optimization Specialist**: Analyzes developer interaction patterns to simplify systems.
- **Green AI & Sustainable Software Auditor**: Evaluates software for compute efficiency and carbon risk.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by [Pranesh003](https://github.com/Pranesh003)
