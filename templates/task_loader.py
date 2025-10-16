"""Task template loader and generator."""
import json
import os
import random
import hashlib
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from string import Template

from config.config import config


class TaskLoader:
    """Load and generate tasks from templates."""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or config.TASK_TEMPLATES_DIR
        self.templates = self._load_templates()
    
    def _load_templates(self) -> List[Dict[str, Any]]:
        """Load all task templates from directory."""
        templates = []
        
        if not os.path.exists(self.templates_dir):
            print(f"Warning: Templates directory {self.templates_dir} not found")
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.templates_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        template = json.load(f)
                        templates.append(template)
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID."""
        for template in self.templates:
            if template["id"] == template_id:
                return template
        return None
    
    def get_random_template(self) -> Dict[str, Any]:
        """Get a random template."""
        return random.choice(self.templates)
    
    def generate_seed(self, email: str, round_num: int = 1) -> str:
        """Generate seed for parameterization."""
        now = datetime.utcnow()
        # Seed expires hourly
        seed_str = f"{email}-{now.strftime('%Y-%m-%d-%H')}-{round_num}"
        return hashlib.md5(seed_str.encode()).hexdigest()[:8]
    
    def generate_task(
        self,
        template: Dict[str, Any],
        email: str,
        round_num: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a task from a template.
        
        Args:
            template: Task template
            email: Student email
            round_num: Round number (1 or 2)
        
        Returns:
            Task data with brief, checks, and attachments
        """
        seed = self.generate_seed(email, round_num)
        
        if round_num == 1:
            brief = self._substitute(template["brief"], seed)
            checks = [self._substitute(check, seed) for check in template.get("checks", [])]
            attachments = self._generate_attachments(
                template.get("attachments", []),
                seed
            )
        else:
            # Round 2: pick a random variant
            round2_options = template.get("round2", [])
            if not round2_options:
                raise ValueError(f"No round2 options in template {template['id']}")
            
            variant = random.choice(round2_options)
            brief = self._substitute(variant["brief"], seed)
            checks = [self._substitute(check, seed) for check in variant.get("checks", [])]
            attachments = self._generate_attachments(
                variant.get("attachments", []),
                seed
            )
        
        return {
            "brief": brief,
            "checks": checks,
            "attachments": attachments
        }
    
    def _substitute(self, text: str, seed: str) -> str:
        """Substitute ${seed} and ${result} in text."""
        # For now, just replace ${seed}
        # ${result} would require actual computation based on generated data
        text = text.replace("${seed}", seed)
        
        # Simple result calculation (placeholder)
        result_value = sum(ord(c) for c in seed) % 1000
        text = text.replace("${result}", str(result_value))
        
        return text
    
    def _generate_attachments(
        self,
        attachment_templates: List[Dict[str, str]],
        seed: str
    ) -> List[Dict[str, str]]:
        """Generate attachments with seed-based data."""
        attachments = []
        
        for att_template in attachment_templates:
            name = att_template["name"]
            url_template = att_template["url"]
            
            # If it's a data URI template
            if "${seed}" in url_template:
                # Generate sample data based on file type
                if name.endswith(".csv"):
                    data = self._generate_csv_data(seed)
                elif name.endswith(".json"):
                    data = self._generate_json_data(seed)
                elif name.endswith(".md"):
                    data = self._generate_markdown_data(seed)
                elif name.endswith(".png"):
                    data = self._generate_png_data(seed)
                else:
                    data = f"Sample data for {name}"
                
                # Encode as base64
                encoded = base64.b64encode(data.encode("utf-8")).decode("utf-8")
                
                # Determine MIME type
                if name.endswith(".csv"):
                    mime = "text/csv"
                elif name.endswith(".json"):
                    mime = "application/json"
                elif name.endswith(".md"):
                    mime = "text/markdown"
                elif name.endswith(".png"):
                    mime = "image/png"
                else:
                    mime = "text/plain"
                
                url = f"data:{mime};base64,{encoded}"
            else:
                url = url_template
            
            attachments.append({
                "name": name,
                "url": url
            })
        
        return attachments
    
    def _generate_csv_data(self, seed: str) -> str:
        """Generate sample CSV data."""
        random.seed(seed)
        
        products = ["Widget", "Gadget", "Tool", "Device", "Item"]
        regions = ["North", "South", "East", "West"]
        
        csv_lines = ["product,region,sales"]
        for _ in range(random.randint(5, 10)):
            product = random.choice(products)
            region = random.choice(regions)
            sales = random.uniform(100, 1000)
            csv_lines.append(f"{product},{region},{sales:.2f}")
        
        return "\n".join(csv_lines)
    
    def _generate_json_data(self, seed: str) -> str:
        """Generate sample JSON data."""
        random.seed(seed)
        
        data = {
            "USD": 1.0,
            "EUR": round(random.uniform(0.85, 0.95), 4),
            "GBP": round(random.uniform(0.75, 0.85), 4),
            "JPY": round(random.uniform(110, 150), 2),
        }
        
        return json.dumps(data, indent=2)
    
    def _generate_markdown_data(self, seed: str) -> str:
        """Generate sample Markdown data."""
        return f"""# Sample Document

This is a sample markdown document with seed: {seed}

## Features

- Feature 1
- Feature 2
- Feature 3

## Code Example

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This is a test document.
"""
    
    def _generate_png_data(self, seed: str) -> str:
        """Generate placeholder PNG data."""
        # For actual PNG, you'd need PIL/Pillow
        # This is a minimal valid PNG (1x1 transparent)
        png_hex = "89504e470d0a1a0a0000000d494844520000000100000001080600000001f15c4890000000a49444154789c6260000000020001e10bc000000000049454e44ae426082"
        return bytes.fromhex(png_hex).decode("latin-1")


# Singleton instance
task_loader = TaskLoader()
