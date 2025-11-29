## Overview
The Text Redaction Tool features a professional interface with black, white, and green color scheme for optimal readability and user experience.

## Interface Components

### 1. Input Section
**Location**: Top card panel
**Function**: Text input and configuration

#### Elements:
- **Text Area**: Large input field for pasting sensitive text
- **Redaction Mode Selector**: Toggle between two modes:
  - **Mask Entities**: Replaces sensitive data with `[ENTITY_TYPE]` placeholders
  - **Remove Entities**: Completely deletes sensitive data
- **Process Button**: Initiates analysis and redaction

### 2. Results Section
**Location**: Bottom card panel (appears after processing)
**Function**: Displays analysis results and redacted output

#### Components:

##### Statistics Panel
- **Total Entities**: Count of all detected sensitive items
- Visual summary of detection results

##### Detected Entities Table
Displays all identified sensitive information in a structured format:

| Column | Description |
|--------|-------------|
| Entity Type | Type of sensitive data (color-coded) |
| Extracted Text | Original sensitive content |
| Position | Character position in original text |

**Color Coding**:
- 🟢 **PERSON**: Names and personal identifiers
- 🔵 **LOCATION**: Geographic locations
- 🟣 **ORGANIZATION**: Companies and institutions
- 🟡 **DATE**: Calendar dates
- 🟠 **TIME**: Time values
- 🟢 **EMAIL**: Email addresses
- 🔵 **PHONE_NUMBER**: Telephone numbers
- 🟤 **IP_ADDRESS**: Network addresses
- 🟣 **CREDIT_CARD**: Payment card numbers
- 🟡 **URL**: Web addresses

##### Redacted Output Panel
- **Display**: Clean, redacted version of input text
- **Copy Function**: One-click copying to clipboard
- **Format Preservation**: Maintains original text structure

## Step-by-Step Usage

### Step 1: Input Preparation
1. Navigate to the application in your web browser
2. Locate the large text area labeled "Input Text"
3. Paste or type text containing sensitive information

**Example Input**:

### Step 2: Configuration
1. **Choose Redaction Mode**:
   - Select "Mask Entities" to see placeholder tags
   - Select "Remove Entities" for complete deletion

2. **Process Text**:
   - Click the "Analyze & Redact Text" button
   - Wait for processing (typically 1-3 seconds)

### Step 3: Review Results
1. **Check Statistics**: Verify entity count matches expectations
2. **Examine Detected Entities**: Review the table for accuracy
3. **View Redacted Output**: See the final safe-to-share text

### Step 4: Output Handling
1. **Copy Redacted Text**: Use the "Copy Redacted Text" button
2. **Verify Security**: Ensure all sensitive data is properly handled
3. **Use Safely**: Share the redacted text as needed

## Best Practices

### Input Preparation
- Use plain text format for optimal detection
- Include context around sensitive data for better AI recognition
- Avoid overly structured data (tables, lists)

### Mode Selection
- **Use Mask Mode** when you need to understand what was redacted
- **Use Remove Mode** for maximum privacy and clean output

### Verification
- Always review detected entities before sharing
- Check for false positives/negatives in the results table
- Verify redacted output meets your security requirements

## Troubleshooting

### Common Issues

**Low Detection Rate**:
- Ensure text has proper context around sensitive data
- Check that entities match supported patterns
- Verify spaCy model is properly installed

**False Positives**:
- Review validation rules in model documentation
- Consider text preprocessing for cleaner input

**Performance Issues**:
- Limit input text to reasonable lengths (<10,000 characters)
- Ensure adequate system resources for NLP processing
