"""LLM client for code generation."""
import os
from typing import Optional, Dict, Any
from config.config import config


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self):
        self.provider = config.LLM_API_PROVIDER
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
        
        if self.provider == "aipipe":
            # AIPipe uses OpenAI-compatible API
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=config.LLM_API_BASE_URL
            )
        elif self.provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate code using LLM."""
        try:
            if self.provider in ["aipipe", "openai"]:
                # AIPipe and OpenAI use the same API format
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4000
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    system=system_prompt or "",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    def generate_app(self, brief: str, checks: list, attachments: list = None) -> Dict[str, str]:
        """Generate a complete app based on brief and checks."""
        
        # Build the prompt
        system_prompt = """You are an expert web developer. Generate a complete, production-ready single-page web application.
        
Requirements:
- Use vanilla HTML, CSS, and JavaScript (no build tools)
- Include all necessary CDN links for libraries
- Make it responsive and professional
- Follow best practices
- Ensure all checks will pass
- Add proper error handling
- Write clean, commented code
- When attachments are provided as data URIs, embed them directly in the JavaScript code"""
        
        attachments_info = ""
        if attachments:
            attachments_info = "\n\nAttachments provided (embed these directly in your code):\n"
            for att in attachments:
                # Provide the full data URI for the LLM to use
                attachments_info += f"\n{att['name']}:\n{att['url']}\n"
        
        checks_info = "\n\nThe app must pass these checks:\n"
        for i, check in enumerate(checks, 1):
            checks_info += f"{i}. {check}\n"
        
        prompt = f"""Create a single-page web application with the following requirements:

BRIEF:
{brief}
{attachments_info}
{checks_info}

IMPORTANT: For any data files provided as data URIs above, embed them directly in your JavaScript code.
Do NOT try to fetch external files. Parse the base64 data URI and use it inline.

Example for CSV data URI:
const dataUri = "data:text/csv;base64,....";
const csvText = atob(dataUri.split(',')[1]);
// then parse csvText

Generate THREE files:
1. index.html (complete HTML file with embedded CSS and JavaScript)
2. README.md (professional documentation with setup, usage, and explanation)
3. LICENSE (MIT License)

Output format:
[FILE: index.html]
... content ...
[END FILE]

[FILE: README.md]
... content ...
[END FILE]

[FILE: LICENSE]
... content ...
[END FILE]
"""
        
        response = self.generate_code(prompt, system_prompt)
        
        # Parse the response into files
        files = self._parse_files(response)
        
        # Ensure we have the required files
        if "index.html" not in files:
            files["index.html"] = self._generate_fallback_html(brief)
        if "README.md" not in files:
            files["README.md"] = self._generate_fallback_readme(brief)
        if "LICENSE" not in files:
            files["LICENSE"] = self._generate_mit_license()
        
        return files
    
    def _parse_files(self, response: str) -> Dict[str, str]:
        """Parse files from LLM response."""
        files = {}
        current_file = None
        current_content = []
        
        for line in response.split("\n"):
            if line.startswith("[FILE:") and "]" in line:
                # Save previous file
                if current_file:
                    files[current_file] = "\n".join(current_content).strip()
                
                # Start new file
                current_file = line.split("[FILE:")[1].split("]")[0].strip()
                current_content = []
            elif line.startswith("[END FILE]"):
                if current_file:
                    files[current_file] = "\n".join(current_content).strip()
                    current_file = None
                    current_content = []
            elif current_file:
                current_content.append(line)
        
        # Save last file if not closed
        if current_file and current_content:
            files[current_file] = "\n".join(current_content).strip()
        
        return files
    
    def _generate_fallback_html(self, brief: str) -> str:
        """Generate a basic fallback HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Application</h1>
        <p>{brief}</p>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    def _generate_fallback_readme(self, brief: str) -> str:
        """Generate a basic fallback README."""
        return f"""# Application

## Overview
{brief}

## Setup
1. Clone this repository
2. Open `index.html` in a web browser

## Usage
Open the application in your web browser and follow the on-screen instructions.

## License
MIT License - see LICENSE file for details.
"""
    
    def _generate_mit_license(self) -> str:
        """Generate MIT License."""
        import datetime
        year = datetime.datetime.now().year
        return f"""MIT License

Copyright (c) {year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


# Singleton instance
llm_client = LLMClient()
