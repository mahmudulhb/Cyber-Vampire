from flask import Flask, render_template_string, request
import spacy
import re

app = Flask(__name__)

# Load large English NLP model
nlp = spacy.load("en_core_web_lg")

# Entity placeholders - REMOVED CARDINAL
ENTITY_MAP = {
    "PERSON": "[PERSON]",
    "GPE": "[LOCATION]", 
    "LOC": "[LOCATION]",
    "ORG": "[ORGANIZATION]",
    "DATE": "[DATE]",
    "TIME": "[TIME]",
    "MONEY": "[MONEY]",
    "PERCENT": "[PERCENT]",
    "EMAIL": "[EMAIL]",
    "IP_ADDRESS": "[IP_ADDRESS]",
    "PHONE_NUMBER": "[PHONE_NUMBER]",
    "CREDIT_CARD": "[CREDIT_CARD]",
    "URL": "[URL]",
    "SSN": "[SSN]"
}

# FIXED regex patterns - much more comprehensive
REGEX_PATTERNS = [
    # Phone numbers FIRST (priority)
    ("PHONE_NUMBER", r'\+?44\s?\d{1,4}\s?\d{3,4}\s?\d{3,4}'),
    ("PHONE_NUMBER", r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
    ("PHONE_NUMBER", r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}'),
    
    # Credit cards - FIXED patterns
    ("CREDIT_CARD", r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'),  # Standard 16-digit
    ("CREDIT_CARD", r'\b\d{4}[- ]?\d{6}[- ]?\d{5}\b'),  # Amex 15-digit
    ("CREDIT_CARD", r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{3}\b'),  # 15-digit variant
    ("CREDIT_CARD", r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{2,4}\b'),  # Flexible
    
    # Other patterns
    ("EMAIL", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    ("URL", r'https?://[^\s<>"]+|\bwww\.[^\s<>"]+'),
    ("IP_ADDRESS", r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'),
    ("DATE", r'\b(?:0?[1-9]|[12][0-9]|3[01])[/-](?:0?[1-9]|1[0-2])[/-](?:\d{4}|\d{2})\b'),
    ("TIME", r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9]\b'),
]

# HTML TEMPLATE AS STRING
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Text Redaction Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            border-bottom: 2px solid #ecf0f1;
        }

        .header h1 {
            font-size: 2.8rem;
            margin-bottom: 10px;
            color: #2c3e50;
            font-weight: 300;
        }

        .header p {
            font-size: 1.2rem;
            color: #7f8c8d;
        }

        .card {
            background: #ffffff;
            border-radius: 8px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border: 1px solid #ecf0f1;
        }

        .card h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.6rem;
            font-weight: 500;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            color: #2c3e50;
        }

        textarea {
            width: 100%;
            min-height: 200px;
            padding: 20px;
            border: 1px solid #dcdfe6;
            border-radius: 6px;
            font-size: 15px;
            resize: vertical;
            font-family: monospace;
            background: #fafbfc;
        }

        textarea:focus {
            outline: none;
            border-color: #27ae60;
            background: #ffffff;
        }

        .mode-selector {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }

        .mode-option {
            flex: 1;
        }

        .mode-option input[type="radio"] {
            display: none;
        }

        .mode-option label {
            display: block;
            padding: 18px 20px;
            text-align: center;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            color: #6c757d;
        }

        .mode-option input[type="radio"]:checked + label {
            background: #27ae60;
            color: #ffffff;
            border-color: #27ae60;
        }

        .btn {
            background: #27ae60;
            color: #ffffff;
            border: none;
            padding: 18px 30px;
            font-size: 16px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-weight: 500;
        }

        .btn:hover {
            background: #219653;
        }

        .result-box {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 25px;
            min-height: 120px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: monospace;
            font-size: 14px;
            line-height: 1.6;
        }

        .entities-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }

        .entity-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            overflow: hidden;
        }

        .entity-table th,
        .entity-table td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }

        .entity-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.85rem;
        }

        .entity-type {
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            display: inline-block;
            text-align: center;
            min-width: 100px;
        }

        .entity-person { background: #d5f4e6; color: #166534; }
        .entity-location { background: #dbeafe; color: #1e40af; }
        .entity-organization { background: #f3e8ff; color: #7e22ce; }
        .entity-date { background: #fef3c7; color: #92400e; }
        .entity-time { background: #fce7f3; color: #be185d; }
        .entity-email { background: #dcfce7; color: #166534; }
        .entity-phone { background: #e0e7ff; color: #3730a3; }
        .entity-ip { background: #f1f5f9; color: #475569; }
        .entity-url { background: #ffedd5; color: #9a3412; }
        .entity-credit_card { background: #fef9c3; color: #854d0e; }
        .entity-number { background: #e0f2fe; color: #0c4a6e; }

        .stats {
            display: flex;
            justify-content: space-around;
            background: #f8f9fa;
            padding: 25px;
            border-radius: 6px;
            margin-bottom: 25px;
            border: 1px solid #e9ecef;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 2.2rem;
            font-weight: 300;
            color: #27ae60;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.85rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .copy-btn {
            background: #2c3e50;
            margin-top: 15px;
            width: auto;
            padding: 12px 24px;
        }

        .copy-btn:hover {
            background: #34495e;
        }

        .validation-note {
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #1565c0;
            font-size: 0.9rem;
        }

        .section-divider {
            height: 1px;
            background: #ecf0f1;
            margin: 30px 0;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .card {
                padding: 25px 20px;
            }
            
            .entities-container {
                grid-template-columns: 1fr;
            }
            
            .mode-selector {
                flex-direction: column;
            }
            
            .entity-table {
                font-size: 0.8rem;
            }
            
            .stats {
                padding: 20px 15px;
            }
            
            .stat-number {
                font-size: 1.8rem;
            }
        }
    </style>
</head>
<body>
        <form method="POST">
            <div class="card">
                <h2>Input Text</h2>
                <div class="form-group">
                    <label for="input_text">Enter text containing sensitive information</label>
                    <textarea id="input_text" name="input_text" placeholder="Paste your text here for analysis and redaction...">{{ input_text }}</textarea>
                </div>
                
                <div class="form-group">
                    <label>Redaction Mode</label>
                    <div class="mode-selector">
                        <div class="mode-option">
                            <input type="radio" id="mask" name="mode" value="mask" {% if mode == 'mask' %}checked{% endif %}>
                            <label for="mask">Mask</label>
                        </div>
                        <div class="mode-option">
                            <input type="radio" id="redact" name="mode" value="redact" {% if mode == 'redact' %}checked{% endif %}>
                            <label for="redact">Redact</label>
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn">submit</button>
            </div>
        </form>

        {% if redacted_text %}
        <div class="card">

            <div class="entities-container">
                <div>
                    <h3>Detected Entities</h3>
                    {% if entities %}
                    <table class="entity-table">
                        <thead>
                            <tr>
                                <th>Entity Type</th>
                                <th>Extracted Text</th>
                                <th>Position</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for entity in entities %}
                            <tr>
                                <td>
                                    <span class="entity-type entity-{{ entity.label|lower }}">
                                        {{ entity.label }}
                                    </span>
                                </td>
                                <td><code>{{ entity.text }}</code></td>
                                <td>{{ entity.start }}-{{ entity.end }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% else %}
                    <p>No entities detected with current strict filters.</p>
                    {% endif %}
                </div>

                <div>
                    <h3>Redacted Output</h3>
                    <div class="result-box">{{ redacted_text }}</div>
                    
                    {% if redacted_text %}
                    <div style="display: flex; justify-content: flex-end; margin-top: 20px;">
                        <button onclick="copyToClipboard()" class="btn copy-btn">Copy Redacted Text</button>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <script>
        function copyToClipboard() {
            const resultText = document.querySelector('.result-box').textContent;
            navigator.clipboard.writeText(resultText).then(() => {
                const btn = document.querySelector('.copy-btn');
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                btn.style.background = '#27ae60';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '#2c3e50';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                alert('Failed to copy text to clipboard. Please try again.');
            });
        }

        // Add loading state to button
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.querySelector('form');
            const submitBtn = form.querySelector('button[type="submit"]');
            
            form.addEventListener('submit', function() {
                submitBtn.textContent = 'Processing...';
                submitBtn.disabled = true;
            });
        });
    </script>
</body>
</html>
'''

def extract_all_entities(text):
    """Extract entities using both regex and spaCy"""
    all_entities = []
    
    # Extract ALL regex entities first without overlap check
    temp_entities = []
    for label, pattern in REGEX_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            temp_entities.append({
                "label": label,
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "type": "regex"
            })
    
    # Sort by start position and remove overlaps (keep longer matches)
    temp_entities.sort(key=lambda x: x["start"])
    i = 0
    while i < len(temp_entities):
        current = temp_entities[i]
        all_entities.append(current)
        
        # Skip overlapping entities
        j = i + 1
        while j < len(temp_entities) and temp_entities[j]["start"] < current["end"]:
            j += 1
        i = j
    
    # Extract spaCy entities - IGNORE CARDINAL
    doc = nlp(text)
    for ent in doc.ents:
        # Skip CARDINAL entities
        if ent.label_ == "CARDINAL":
            continue
            
        # Check for overlap with existing entities
        overlap = False
        for existing_ent in all_entities:
            if (ent.start_char < existing_ent["end"] and 
                ent.end_char > existing_ent["start"]):
                overlap = True
                break
        
        if not overlap and ent.label_ in ENTITY_MAP:
            if is_valid_spacy_entity(ent.text, ent.label_):
                all_entities.append({
                    "label": ent.label_,
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "type": "spacy"
                })
    
    # Final sort
    all_entities.sort(key=lambda x: x["start"])
    return all_entities

def is_valid_spacy_entity(text, label):
    """Simple validation for spaCy entities"""
    if label == "PERSON":
        if len(text) < 2 or len(text) > 50:
            return False
        if any(char.isdigit() for char in text):
            return False
        if text.lower() in ["city", "location", "ip"]:
            return False
    
    elif label == "GPE":
        if len(text) < 2 or len(text) > 30:
            return False
        if text.lower() in ["city", "location"]:
            return False
    
    return True

def redact_text(text, entities, mode="mask"):
    """Redact text based on detected entities"""
    if not entities:
        return text
    
    # Sort entities by start position in reverse order for replacement
    entities_sorted = sorted(entities, key=lambda x: x["start"], reverse=True)
    
    result_text = text
    for entity in entities_sorted:
        start = entity["start"]
        end = entity["end"]
        label = entity["label"]
        
        replacement = ENTITY_MAP.get(label, f"[{label}]") if mode == "mask" else ""
        result_text = result_text[:start] + replacement + result_text[end:]
    
    return result_text

@app.route("/", methods=["GET", "POST"])
def index():
    redacted_text = ""
    entities = []
    input_text = ""
    mode = "mask"
    
    if request.method == "POST":
        input_text = request.form.get("input_text", "")
        mode = request.form.get("mode", "mask")
        
        if input_text.strip():
            # Extract entities
            entities = extract_all_entities(input_text)
            # Redact text
            redacted_text = redact_text(input_text, entities, mode)
    
    return render_template_string(HTML_TEMPLATE, 
                         redacted_text=redacted_text, 
                         entities=entities,
                         input_text=input_text,
                         mode=mode)

if __name__ == "__main__":
    app.run(debug=True)