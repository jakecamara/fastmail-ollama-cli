# Fastmail / Ollama Interactive CLI Tool

This Python project processes emails using the Fastmail API and summarizes or generates replies to them using a local Ollama API.

## Features
- [x] Fetch and list emails from your Fastmail inbox.
- [x] Clean email content by removing HTML and CSS to prepare it for processing.
- [x] Summarize emails using the Ollama API.
- [x] Generate polite and professional replies.
- [x] Fully interactive CLI for selecting and processing emails.

## Roadmap
- [ ] Automatically save Ollama-generated replies as drafts in your Fastmail account.
- [ ] Tag emails with labels based on Ollama's analysis.
- [ ] Automatically or manually move emails to folders.
- [ ] Delete emails directly from the CLI.
- [ ] Process multiple emails at once for summarization, replies, or folder assignment.
- [ ] Generate tasks from email content and export to external tools like Todoist or Trello.

## Requirements
- Python 3.7 or later
- Fastmail API credentials
- Access to an Ollama instance

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/jakeandco/fastmail-ollama-cli.git
cd fastmail-ollama-cli
```

### 2. Create a Virtual Environment
Create a virtual environment in the project directory:
```bash
python -m venv venv
```

Activate the virtual environment:

- Windows:
```bash
.\venv\Scripts\activate
```

- macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies
Install the required dependencies using pip:
```bash
pip install -r requirements.txt
```

### 4. Create a .env File
Create a .env file in the project directory to store sensitive credentials:
```bash
touch .env
```

Add the following variables to .env:
```
API_TOKEN=your_fastmail_api_token
ACCOUNT_ID=your_account_id
API_URL=https://api.fastmail.com/jmap/api/
OLLAMA_URL=http://ollama:11434/api/generate
```

## Usage
Run the script to start the interactive email processor:
```bash
python main.py
```

**Interactive CLI Features**
- Lists emails from your Fastmail inbox.
- Allows you to select an email to summarize or reply to.
- Generates replies or summaries using the Ollama API.

## Updating Dependencies
To update or add dependencies, install the package and update requirements.txt:
```bash
pip install <package_name>
pip freeze > requirements.txt
```

## Troubleshooting
- **Missing Module Error:** Ensure the virtual environment is activated and dependencies are installed.
- **API Errors:** Verify the credentials in your .env file and that the API endpoint exists on your Ollama server.

## License

This project is licensed under the MIT License.