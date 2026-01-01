import base64
import json
from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY, UPLOAD_DIR

# Try to import PyPDF2 for PDF text extraction
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def extract_pdf_text(file_path: Path) -> str:
    """Extract text content from a PDF file."""
    if not PDF_SUPPORT:
        return "[PDF text extraction not available - please install PyPDF2]"

    try:
        reader = PdfReader(str(file_path))
        text_parts = []

        # Extract text from each page
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                text_parts.append(f"--- Page {i + 1} ---\n{text.strip()}")

        if text_parts:
            full_text = "\n\n".join(text_parts)
            # Log the extraction for debugging
            print(f"[AI Service] Extracted {len(full_text)} characters from PDF with {len(reader.pages)} pages")
            return full_text
        else:
            return "[No extractable text found in PDF - the PDF may contain only images or scanned content]"

    except Exception as e:
        print(f"[AI Service] Error reading PDF: {str(e)}")
        return f"[Error reading PDF: {str(e)}]"


def encode_image_base64(file_path: Path) -> str:
    """Encode an image file to base64."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_media_type(content_type: str) -> str:
    """Get the media type for OpenAI vision API."""
    type_map = {
        "image/png": "image/png",
        "image/jpeg": "image/jpeg",
        "image/jpg": "image/jpeg",
        "image/gif": "image/gif",
        "image/webp": "image/webp"
    }
    return type_map.get(content_type, "image/jpeg")


def generate_task_summary(
    task_title: str,
    notes_content: str,
    attachments: list = None
) -> dict:
    """
    Generate a detailed AI summary of task notes and attachments.

    Args:
        task_title: The title of the task
        notes_content: Text notes for the task
        attachments: List of attachment dicts with keys:
                    task_id, stored_filename, filename, content_type

    Returns a dict with detailed summary sections.
    """
    if not OPENAI_API_KEY:
        return {
            "summary": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            "key_points": [],
            "concepts": [],
            "action_items": [],
            "study_tips": [],
            "error": True
        }

    attachments = attachments or []
    has_notes = notes_content and notes_content.strip()
    has_attachments = len(attachments) > 0

    if not has_notes and not has_attachments:
        return {
            "summary": "No notes or attachments available to summarize. Add some content first!",
            "key_points": [],
            "concepts": [],
            "action_items": [],
            "study_tips": [],
            "error": False
        }

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Process attachments
    pdf_contents = []
    image_contents = []

    print(f"[AI Service] Processing {len(attachments)} attachments...")

    for attachment in attachments:
        task_id = attachment.get("task_id")
        stored_filename = attachment.get("stored_filename")
        filename = attachment.get("filename", "unnamed")
        content_type = attachment.get("content_type", "")

        file_path = UPLOAD_DIR / str(task_id) / stored_filename

        print(f"[AI Service] Processing: {filename} (type: {content_type})")

        if not file_path.exists():
            print(f"[AI Service] File not found: {file_path}")
            continue

        if content_type == "application/pdf":
            # Extract text from PDF
            pdf_text = extract_pdf_text(file_path)
            pdf_contents.append({
                "filename": filename,
                "content": pdf_text
            })
            print(f"[AI Service] PDF '{filename}' extracted: {len(pdf_text)} chars")

        elif content_type.startswith("image/"):
            # Prepare image for vision API
            try:
                base64_image = encode_image_base64(file_path)
                media_type = get_image_media_type(content_type)
                image_contents.append({
                    "filename": filename,
                    "base64": base64_image,
                    "media_type": media_type
                })
                print(f"[AI Service] Image '{filename}' encoded for vision API")
            except Exception as e:
                print(f"[AI Service] Error encoding image: {str(e)}")

    # Build comprehensive content for the AI
    content_sections = []

    if has_notes:
        content_sections.append(f"=== USER'S NOTES ===\n{notes_content}")

    if pdf_contents:
        for pdf in pdf_contents:
            content_sections.append(
                f"=== PDF DOCUMENT: {pdf['filename']} ===\n{pdf['content']}"
            )

    combined_text = "\n\n" + "\n\n".join(content_sections) if content_sections else ""

    print(f"[AI Service] Total content length: {len(combined_text)} characters")

    # Use GPT-4o-mini for vision if we have images, otherwise GPT-4o-mini for better quality
    if image_contents:
        return _generate_with_vision(client, task_title, combined_text, image_contents)
    else:
        return _generate_detailed_summary(client, task_title, combined_text)


def _generate_detailed_summary(client: OpenAI, task_title: str, content: str) -> dict:
    """Generate a detailed, comprehensive summary for studying."""

    # Truncate content if too long (GPT-4o-mini has ~128k context but we want to be safe)
    max_content_length = 100000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "\n\n[Content truncated due to length...]"

    prompt = f"""You are an expert academic assistant helping a student understand and complete their assignment.

TASK/ASSIGNMENT: {task_title}

CONTENT TO ANALYZE:
{content}

Based on ALL the content provided (notes and PDF documents), create a comprehensive study guide. Read through the ENTIRE content carefully and extract the most important information.

Provide your response in the following JSON format:
{{
    "summary": "A detailed 4-6 sentence summary that explains what this assignment/topic is about, the main themes, and what the student needs to understand. Be specific and reference actual content from the documents.",

    "key_points": [
        "Detailed key point 1 - explain the concept fully",
        "Detailed key point 2 - include specific facts, dates, or figures if mentioned",
        "Detailed key point 3 - explain relationships between concepts",
        "Detailed key point 4 - highlight any important definitions or terms",
        "Detailed key point 5 - note any critical arguments or theories"
    ],

    "concepts": [
        "Important concept or term 1 with brief explanation",
        "Important concept or term 2 with brief explanation",
        "Important concept or term 3 with brief explanation"
    ],

    "action_items": [
        "Specific action the student should take to complete this assignment",
        "Another specific task or step",
        "Things to research or review further"
    ],

    "study_tips": [
        "Specific study recommendation based on the content",
        "How to approach understanding this material",
        "What to focus on for success"
    ]
}}

IMPORTANT INSTRUCTIONS:
1. Actually READ and ANALYZE the full content - don't just describe what files are attached
2. Extract SPECIFIC information, facts, concepts, and arguments from the documents
3. Be DETAILED and THOROUGH - this summary should help the student study
4. Include actual content from the PDFs - quotes, statistics, key arguments, etc.
5. If there are multiple documents, synthesize information across all of them
6. Make the key_points comprehensive enough that a student could study from them
7. for the key points and concepts section make sure that you make it very detailed and make sure that you properly teach the user about all the topics in all the documents so they can apply it to any questions they get"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for better comprehension
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic tutor who creates detailed, helpful study guides. You thoroughly read all provided content and extract the most important information to help students succeed in their assignments. Always provide specific, actionable insights based on the actual content."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused, accurate responses
            max_tokens=2000  # Allow longer responses for detailed summaries
        )

        response_content = response.choices[0].message.content
        print(f"[AI Service] Response received: {len(response_content)} chars")
        return _parse_detailed_response(response_content)

    except Exception as e:
        print(f"[AI Service] Error generating summary: {str(e)}")
        return {
            "summary": f"Failed to generate summary: {str(e)}",
            "key_points": [],
            "concepts": [],
            "action_items": [],
            "study_tips": [],
            "error": True
        }


def _generate_with_vision(
    client: OpenAI,
    task_title: str,
    text_content: str,
    image_contents: list
) -> dict:
    """Generate detailed summary using vision model to analyze images."""

    # Build message content with images
    message_content = []

    # Add text prompt
    text_prompt = f"""You are an expert academic assistant helping a student understand and complete their assignment.

TASK/ASSIGNMENT: {task_title}

TEXT CONTENT TO ANALYZE:
{text_content}

I'm also providing {len(image_contents)} image(s) attached to this task. Please analyze the images thoroughly - they may contain diagrams, charts, text, equations, or other important information.

Based on ALL the content (text notes, PDFs, and images), create a comprehensive study guide. Read through EVERYTHING carefully and extract the most important information.

Provide your response in the following JSON format:
{{
    "summary": "A detailed 4-6 sentence summary that explains what this assignment/topic is about, the main themes, and what the student needs to understand. Be specific and reference actual content from the documents and images.",

    "key_points": [
        "Detailed key point 1 - explain the concept fully",
        "Detailed key point 2 - include specific facts, dates, or figures if mentioned",
        "Detailed key point 3 - explain relationships between concepts",
        "Detailed key point 4 - highlight any important definitions or terms",
        "Detailed key point 5 - note any critical arguments or theories"
    ],

    "concepts": [
        "Important concept or term 1 with brief explanation",
        "Important concept or term 2 with brief explanation",
        "Important concept or term 3 with brief explanation"
    ],

    "action_items": [
        "Specific action the student should take to complete this assignment",
        "Another specific task or step",
        "Things to research or review further"
    ],

    "study_tips": [
        "Specific study recommendation based on the content",
        "How to approach understanding this material",
        "What to focus on for success"
    ]
}}

IMPORTANT: Actually analyze the images and extract specific information from them. Describe what you see and how it relates to the assignment."""

    message_content.append({
        "type": "text",
        "text": text_prompt
    })

    # Add images
    for img in image_contents:
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img['media_type']};base64,{img['base64']}",
                "detail": "high"  # Use high detail for better analysis
            }
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Vision-capable model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic tutor who creates detailed, helpful study guides. You thoroughly analyze all provided content including images, diagrams, and documents. Always provide specific, actionable insights based on the actual content."
                },
                {"role": "user", "content": message_content}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        response_content = response.choices[0].message.content
        return _parse_detailed_response(response_content)

    except Exception as e:
        return {
            "summary": f"Failed to generate summary: {str(e)}",
            "key_points": [],
            "concepts": [],
            "action_items": [],
            "study_tips": [],
            "error": True
        }


def _parse_detailed_response(content: str) -> dict:
    """Parse JSON response from OpenAI."""
    try:
        # Try to extract JSON from the response
        # Sometimes the model wraps it in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]

        result = json.loads(content.strip())
        return {
            "summary": result.get("summary", ""),
            "key_points": result.get("key_points", []),
            "concepts": result.get("concepts", []),
            "action_items": result.get("action_items", []),
            "study_tips": result.get("study_tips", []),
            "error": False
        }
    except json.JSONDecodeError as e:
        print(f"[AI Service] JSON parse error: {str(e)}")
        print(f"[AI Service] Raw content: {content[:500]}...")
        # If JSON parsing fails, try to return something useful
        return {
            "summary": content,
            "key_points": [],
            "concepts": [],
            "action_items": [],
            "study_tips": [],
            "error": False
        }
