import json
from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY, UPLOAD_DIR
from services.ai_service import extract_pdf_text, encode_image_base64, get_image_media_type


def solve_assignment(
    task_title: str,
    notes_content: str,
    context_attachments: list,
    assignment_file_path: Path,
    assignment_content_type: str,
    assignment_filename: str
) -> dict:
    """
    Analyze an assignment and generate solution approaches using notes as context.

    Args:
        task_title: The title of the task
        notes_content: User's notes for context
        context_attachments: List of study material attachments for context
        assignment_file_path: Path to the uploaded assignment file
        assignment_content_type: MIME type of the assignment file
        assignment_filename: Original filename of the assignment

    Returns a dict with questions and solution approaches.
    """
    if not OPENAI_API_KEY:
        return {
            "questions": [],
            "error": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        }

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build context from notes and attachments
    context_sections = []

    if notes_content and notes_content.strip():
        context_sections.append(f"=== STUDENT'S NOTES ===\n{notes_content}")

    # Process context attachments (study materials)
    for attachment in context_attachments:
        task_id = attachment.get("task_id")
        stored_filename = attachment.get("stored_filename")
        filename = attachment.get("filename", "unnamed")
        content_type = attachment.get("content_type", "")

        file_path = UPLOAD_DIR / str(task_id) / stored_filename

        if not file_path.exists():
            continue

        if content_type == "application/pdf":
            pdf_text = extract_pdf_text(file_path)
            if pdf_text and not pdf_text.startswith("["):
                context_sections.append(f"=== STUDY MATERIAL: {filename} ===\n{pdf_text[:15000]}")

    context_text = "\n\n".join(context_sections) if context_sections else "No additional study materials provided."

    # Extract assignment content
    assignment_content = ""
    assignment_images = []

    if assignment_content_type == "application/pdf":
        assignment_content = extract_pdf_text(assignment_file_path)
        print(f"[Assignment Service] Extracted {len(assignment_content)} chars from assignment PDF")
    elif assignment_content_type.startswith("image/"):
        try:
            base64_image = encode_image_base64(assignment_file_path)
            media_type = get_image_media_type(assignment_content_type)
            assignment_images.append({
                "filename": assignment_filename,
                "base64": base64_image,
                "media_type": media_type
            })
            print(f"[Assignment Service] Encoded assignment image for vision API")
        except Exception as e:
            print(f"[Assignment Service] Error encoding image: {str(e)}")
            return {"questions": [], "error": f"Failed to process image: {str(e)}"}

    # Generate solutions using appropriate method
    if assignment_images:
        return _solve_with_vision(client, task_title, context_text, assignment_images)
    else:
        return _solve_from_text(client, task_title, context_text, assignment_content)


def _solve_from_text(client: OpenAI, task_title: str, context: str, assignment_text: str) -> dict:
    """Generate solutions from text-based assignment."""

    # Truncate if needed
    max_context = 50000
    max_assignment = 30000

    if len(context) > max_context:
        context = context[:max_context] + "\n\n[Context truncated...]"
    if len(assignment_text) > max_assignment:
        assignment_text = assignment_text[:max_assignment] + "\n\n[Assignment truncated...]"

    prompt = f"""You are an expert tutor helping a student solve their homework assignment. The student has provided study notes and materials for context.

TASK/SUBJECT: {task_title}

=== STUDY CONTEXT (Notes and Materials) ===
{context}

=== ASSIGNMENT TO SOLVE ===
{assignment_text}

Your job is to:
1. Identify each question/problem in the assignment
2. For each question, provide a detailed approach to solving it using the study materials as reference
3. Do NOT give direct answers - instead guide the student through the solution process

Provide your response in the following JSON format:
{{
    "questions": [
        {{
            "question_number": "1" or "1a" or "Question 1",
            "question_text": "The actual question text (summarize if very long)",
            "approach": "A detailed explanation of how to approach this problem, referencing relevant concepts from the study materials",
            "key_concepts": ["Concept 1 from notes", "Concept 2 needed", "Formula or theorem to use"],
            "solution_steps": [
                "Step 1: First, identify...",
                "Step 2: Apply the concept of...",
                "Step 3: Calculate/analyze...",
                "Step 4: Verify your answer by..."
            ],
            "tips": "Helpful tips or common mistakes to avoid"
        }}
    ]
}}

IMPORTANT INSTRUCTIONS:
1. Identify ALL questions in the assignment
2. Reference specific concepts from the study materials when applicable
3. Provide step-by-step guidance, not direct answers
4. If a concept isn't in the notes, still explain it but note that additional study may be needed
5. Be thorough - the goal is to help the student learn while completing their assignment
6. For math problems, show the approach and formulas without calculating final numerical answers
7. For essay questions, provide an outline and key points to cover"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic tutor. Your goal is to guide students to solutions rather than giving direct answers. Reference their study materials when possible and help them understand the concepts needed to solve each problem."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        response_content = response.choices[0].message.content
        print(f"[Assignment Service] Response received: {len(response_content)} chars")
        return _parse_solution_response(response_content)

    except Exception as e:
        print(f"[Assignment Service] Error: {str(e)}")
        return {"questions": [], "error": f"Failed to generate solutions: {str(e)}"}


def _solve_with_vision(client: OpenAI, task_title: str, context: str, assignment_images: list) -> dict:
    """Generate solutions from image-based assignment using vision."""

    # Truncate context if needed
    max_context = 50000
    if len(context) > max_context:
        context = context[:max_context] + "\n\n[Context truncated...]"

    message_content = []

    text_prompt = f"""You are an expert tutor helping a student solve their homework assignment. The student has provided study notes and materials for context.

TASK/SUBJECT: {task_title}

=== STUDY CONTEXT (Notes and Materials) ===
{context}

=== ASSIGNMENT ===
I'm providing an image of the assignment. Please analyze it carefully and identify all questions/problems.

Your job is to:
1. Identify each question/problem in the assignment image
2. For each question, provide a detailed approach to solving it using the study materials as reference
3. Do NOT give direct answers - instead guide the student through the solution process

Provide your response in the following JSON format:
{{
    "questions": [
        {{
            "question_number": "1" or "1a" or "Question 1",
            "question_text": "The actual question text as shown in the image",
            "approach": "A detailed explanation of how to approach this problem, referencing relevant concepts from the study materials",
            "key_concepts": ["Concept 1 from notes", "Concept 2 needed", "Formula or theorem to use"],
            "solution_steps": [
                "Step 1: First, identify...",
                "Step 2: Apply the concept of...",
                "Step 3: Calculate/analyze...",
                "Step 4: Verify your answer by..."
            ],
            "tips": "Helpful tips or common mistakes to avoid"
        }}
    ]
}}

IMPORTANT: Read the assignment image carefully and identify ALL questions. Reference concepts from the study materials when applicable."""

    message_content.append({"type": "text", "text": text_prompt})

    # Add assignment images
    for img in assignment_images:
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img['media_type']};base64,{img['base64']}",
                "detail": "high"
            }
        })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert academic tutor who helps students understand and solve their assignments. You guide them through the problem-solving process without giving direct answers."
                },
                {"role": "user", "content": message_content}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        response_content = response.choices[0].message.content
        return _parse_solution_response(response_content)

    except Exception as e:
        return {"questions": [], "error": f"Failed to generate solutions: {str(e)}"}


def _parse_solution_response(content: str) -> dict:
    """Parse JSON response from OpenAI."""
    try:
        # Extract JSON from potential markdown wrapping
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]

        result = json.loads(content.strip())
        return {
            "questions": result.get("questions", []),
            "error": None
        }
    except json.JSONDecodeError as e:
        print(f"[Assignment Service] JSON parse error: {str(e)}")
        print(f"[Assignment Service] Raw content: {content[:500]}...")
        return {
            "questions": [],
            "error": "Failed to parse AI response. Please try again."
        }
