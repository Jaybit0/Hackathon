#!/usr/bin/env python3
"""
Full Optimization Workflow

1. Prompt for a website URL and download the HTML to company_website.html.
2. Use the LLM to generate company_info.md from the HTML.
3. Prompt for a search query.
4. Run the snippet optimizer and, if successful, the website optimizer.
"""

import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai_client_with_mcp import OpenAIClientWithMCP
import subprocess
import html as html_lib


def download_website_html(url, out_path="company_website.html"):
    print(f"🌐 Downloading website HTML from: {url}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"✅ Saved HTML to {out_path}")


def extract_clean_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    # Remove all script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()
    parts = []
    # Title
    if soup.title:
        parts.append(f"Title: {soup.title.string.strip()}")
    # Meta description
    meta_desc = ""
    for tag in soup.find_all("meta"):
        if tag.get("name", "").lower() == "description":
            meta_desc = tag.get("content", "").strip()
    if meta_desc:
        parts.append(f"Meta description: {meta_desc}")
    # Headers
    for tag in soup.find_all(["h1", "h2", "h3"]):
        parts.append(f"{tag.name.upper()}: {tag.get_text(strip=True)}")
    # Paragraphs
    for tag in soup.find_all("p"):
        parts.append(f"P: {tag.get_text(strip=True)}")
    # List items
    for tag in soup.find_all("li"):
        parts.append(f"LI: {tag.get_text(strip=True)}")
    text = "\n".join(parts)
    text = html_lib.unescape(text)
    return text


def extract_company_info_with_llm(html_path, out_path="company_info.md"):
    print(f"🤖 Using LLM to extract company info from {html_path}...")
    relevant_text = extract_clean_text_from_html(html_path)
    prompt = f"""
You are an expert at analyzing company websites. Given the following extracted content, extract all relevant information about the company, its products, services, mission, awards, and contact details. Write a comprehensive, well-structured markdown file (company_info.md) that summarizes this information for use in AI-driven search and snippet optimization.

---
{relevant_text}
---

Output only the markdown file contents.
"""
    client = OpenAIClientWithMCP()
    response = client.chat_completion([
        {"role": "user", "content": prompt}
    ], model="gpt-4o", temperature=0.2)
    md = response['choices'][0]['message']['content']
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ Saved company info to {out_path}")


def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        return
    # 1. Prompt for website URL
    url = input("Enter the company website URL: ").strip()
    download_website_html(url)
    # 2. Use LLM to generate company_info.md
    extract_company_info_with_llm("company_website.html", "company_info.md")
    # 3. Prompt for search query
    query = input("Enter the search query to optimize for: ").strip()
    # 4. Run snippet optimizer (which will call website optimizer if successful)
    # Patch snippet_optimizer_agent.py to accept a query argument if needed
    print(f"\n🚀 Running snippet_optimizer_agent.py for query: {query}")
    subprocess.run(["python", "snippet_optimizer_agent.py", query])

if __name__ == "__main__":
    main() 