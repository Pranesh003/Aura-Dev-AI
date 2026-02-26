# Aura-Dev-AI 🚀

Aura-Dev-AI is a powerful, multi-agent AI development framework designed to automate and enhance the software development lifecycle. Built with **CrewAI** and powered by **Google Gemini**, it orchestrates a team of specialized AI agents to handle everything from architectural design to code generation and auditing.

## 🌟 Key Features

- **Multi-Agent Orchestration**: Specialized agents for Architecting, Coding, Auditing, and more.
- **Resilient LLM Engine**: Advanced model rotation and retry logic to ensure high availability and performance.
- **Vision Integration**: Capabilities to analyze UI designs and sketches for front-end generation.
- **Automated Workflows**: Streamlined processes for project initialization, development, and verification.
- **Modern UI**: Intuitive front-end built with Vite and React.

## 🏗️ Project Structure

```text
visionlink/
├── agents.py           # Definition of specialized AI agents
├── tasks.py            # Task definitions for agents
├── crew_flow.py        # CrewAI orchestration logic
├── direct_flow.py      # Main execution flow and direct processing
├── resilient_engine.py # Hardened LLM interaction layer
├── tools.py            # Custom tools for agents
├── app.py              # Streamlit dashboard/interface
├── backend/            # FastAPI backend services
└── frontend/           # Vite + React frontend application
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js & npm (for frontend)
- Google Gemini API Key(s)

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
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the Backend**:

   ```bash
   python app.py
   ```

5. **Run the Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🤖 Agents & Roles

- **System Architect**: Designs robust software architectures.
- **Senior Developer**: Writes high-quality, production-ready code.
- **Security Auditor**: Ensures code follows security best practices.
- **UX Specialist**: Focuses on user interface and experience.
- **Sustainability Auditor**: Evaluates software for energy efficiency and inclusivity.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by [Pranesh003](https://github.com/Pranesh003)
