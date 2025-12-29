import json
import requests
from urllib.parse import urlparse
from config import PERPLEXITY_API_KEY


def verify_url(url: str, timeout: int = 5) -> bool:
    """Check if a URL is accessible."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        return response.status_code < 400
    except:
        try:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
            return response.status_code < 400
        except:
            return False


def get_source_from_url(url: str) -> str:
    """Extract a friendly source name from URL."""
    try:
        domain = urlparse(url).netloc.replace("www.", "").lower()

        source_map = {
            "youtube.com": "YouTube",
            "wikipedia.org": "Wikipedia",
            "edx.org": "edX",
            "brilliant.org": "Brilliant",
            "mit.edu": "MIT",
            "stanford.edu": "Stanford",
            "harvard.edu": "Harvard",
            "geeksforgeeks.org": "GeeksforGeeks",
            "w3schools.com": "W3Schools",
            "mathworld.wolfram.com": "Wolfram MathWorld",
            "britannica.com": "Britannica",
            "scholarpedia.org": "Scholarpedia",
            "nature.com": "Nature",
            "sciencedirect.com": "ScienceDirect",
            "pubmed.ncbi.nlm.nih.gov": "PubMed",
            "arxiv.org": "arXiv",
            "jstor.org": "JSTOR",
            "khanacademy.org": "Khan Academy",
            "coursera.org": "Coursera",
        }

        for key, value in source_map.items():
            if key in domain:
                return value

        # Default: capitalize first part of domain
        return domain.split(".")[0].title()
    except:
        return "Web"


def find_resources_with_perplexity(notes_content: str, pdf_content: str) -> list[dict]:
    """
    Use Perplexity API to find relevant educational resources.
    Perplexity has built-in web search and provides real, live sources.
    """
    if not PERPLEXITY_API_KEY:
        print("[Resource Service] No Perplexity API key")
        return []

    # Must have actual content
    if not notes_content.strip() and not pdf_content.strip():
        print("[Resource Service] No content to analyze")
        return []

    # Build content summary - prioritize PDF content since it's the main study material
    content_to_analyze = ""

    # Add PDF content FIRST since it's the primary source
    if pdf_content and pdf_content.strip():
        content_to_analyze += f"=== MAIN STUDY MATERIAL FROM UPLOADED PDFs ===\n{pdf_content}\n\n"
        print(f"[Resource Service] Added PDF content: {len(pdf_content)} chars")

    # Add notes as supplementary
    if notes_content and notes_content.strip():
        content_to_analyze += f"=== STUDENT'S ADDITIONAL NOTES ===\n{notes_content}\n\n"
        print(f"[Resource Service] Added notes content: {len(notes_content)} chars")

    print(f"[Resource Service] Total content to analyze: {len(content_to_analyze)} chars")

    # Log the actual content being sent (first 1000 chars)
    print(f"[Resource Service] === CONTENT BEING SENT TO PERPLEXITY ===")
    print(f"{content_to_analyze[:1000]}")
    print(f"[Resource Service] === END PREVIEW ===")

    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": """You are an expert educational resource finder. Your job is to CAREFULLY READ the student's uploaded PDF documents and notes, then find online resources that help them learn those EXACT topics.

CRITICAL INSTRUCTIONS:
1. THOROUGHLY READ the PDF content provided - this is the student's main study material
2. IDENTIFY the specific topics, concepts, theories, terms, and subjects mentioned in the PDFs
3. Search the web for 10 HIGH-QUALITY resources that DIRECTLY relate to the PDF content
4. Resources must be REAL, CURRENTLY WORKING URLs
5. Each resource should help explain concepts FROM THE PDF

RESPOND WITH ONLY A JSON ARRAY - no other text:
[
  {
    "title": "Exact title of the article/resource",
    "url": "https://real-working-url.com/specific-page",
    "description": "2-3 sentences explaining how this helps with SPECIFIC topics from the student's PDF",
    "source": "Website name"
  }
]"""
                },
                {
                    "role": "user",
                    "content": f"""I need help finding resources for my studies. Here is the content from my uploaded PDFs and notes - please READ THIS CAREFULLY and find resources that help me understand these specific topics:

{content_to_analyze[:15000]}

Based on the ACTUAL CONTENT above (especially the PDF material), search the web and find 10 educational resources that will help me understand these specific topics better. Return ONLY a JSON array with real, working URLs."""
                }
            ],
            "temperature": 0.2,
            "max_tokens": 3000
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print(f"[Resource Service] Perplexity API error: {response.status_code}")
            print(f"[Resource Service] Response: {response.text}")
            return []

        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        print(f"[Resource Service] Perplexity response: {content[:500]}...")

        # Parse JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Find JSON array
        content = content.strip()
        if not content.startswith("["):
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                content = content[start:end]

        resources = json.loads(content)

        if isinstance(resources, list):
            print(f"[Resource Service] Perplexity found {len(resources)} resources")
            return resources

        return []

    except json.JSONDecodeError as e:
        print(f"[Resource Service] JSON parse error: {str(e)}")
        return []
    except Exception as e:
        print(f"[Resource Service] Perplexity error: {str(e)}")
        return []


def find_resources(
    task_title: str = "",  # Kept for API compatibility but not used
    notes_content: str = "",
    pdf_content: str = "",
    num_resources: int = 5
) -> list[dict]:
    """
    Find relevant educational resources using Perplexity API.
    Resources are based ONLY on notes and PDF content.
    Generates 10 resources, verifies URLs, returns top 5.
    """
    _ = task_title  # Unused - resources based only on notes/PDF content
    print(f"[Resource Service] ===== FINDING RESOURCES WITH PERPLEXITY =====")
    print(f"[Resource Service] Notes: {len(notes_content)} chars")
    print(f"[Resource Service] PDF content: {len(pdf_content)} chars")

    # Log actual content preview for debugging
    if notes_content.strip():
        print(f"[Resource Service] Notes preview: {notes_content[:300]}...")
    if pdf_content.strip():
        print(f"[Resource Service] PDF content preview: {pdf_content[:500]}...")

    # Must have actual content
    if not notes_content.strip() and not pdf_content.strip():
        print("[Resource Service] No content provided - both notes and PDF content are empty")
        return []

    # Get resources from Perplexity (asks for 10)
    all_resources = find_resources_with_perplexity(notes_content, pdf_content)

    if not all_resources:
        print("[Resource Service] Perplexity returned no resources")
        return []

    # Verify URLs and collect valid resources
    verified_resources = []

    for resource in all_resources:
        if len(verified_resources) >= num_resources:
            break

        url = resource.get("url", "")
        title = resource.get("title", "")

        if not url or not title:
            continue

        # Clean up URL
        url = url.strip()
        if not url.startswith("http"):
            url = "https://" + url

        print(f"[Resource Service] Verifying: {title}")
        print(f"[Resource Service]   URL: {url}")

        # Verify URL is live
        if verify_url(url):
            source = resource.get("source") or get_source_from_url(url)

            verified_resources.append({
                "title": title,
                "url": url,
                "description": resource.get("description", "Educational resource related to your study materials"),
                "source": source
            })
            print(f"[Resource Service]   ✓ Verified and added")
        else:
            print(f"[Resource Service]   ✗ URL not accessible, skipping")

    print(f"[Resource Service] Returning {len(verified_resources)} verified resources (top 5 of 10)")
    return verified_resources
