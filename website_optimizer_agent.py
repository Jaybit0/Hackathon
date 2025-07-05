#!/usr/bin/env python3
"""
Website Optimizer Agent

This script reads the contents of company_website.html and a target (ideal) snippet, then uses the LLM to propose changes to the HTML (title, meta description, main content) to make the Google/LLM-generated snippet as close as possible to the target. Outputs the new HTML and a summary of changes.
"""

import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai_client_with_mcp import OpenAIClientWithMCP


def extract_website_content(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else ""
    meta_desc = ""
    for tag in soup.find_all("meta"):
        if tag.get("name", "").lower() == "description":
            meta_desc = tag.get("content", "").strip()
    first_paragraph = soup.find("p").get_text().strip() if soup.find("p") else ""
    return {
        "title": title,
        "meta_desc": meta_desc,
        "first_paragraph": first_paragraph,
        "html": html
    }


def website_optimization_prompt(current_html, target_snippet):
    return f"""
You are an expert in SEO and web content optimization. Your task is to update a company's website HTML so that Google or an LLM will generate a snippet as close as possible to the provided target snippet.

Here is the current website HTML:
---
{current_html}
---

Here is the target snippet we want Google/LLM to generate:
{target_snippet}

Please propose specific changes to the website's HTML (title, meta description, and main content) to maximize the chance that Google/LLM will use the target snippet. Output the new HTML (with your changes applied) and briefly explain your changes.
"""


def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        return
    html_path = "company_website.html"
    target_snippet_path = "target_snippet.txt"
    if not os.path.exists(html_path):
        print(f"❌ {html_path} not found!")
        return
    if not os.path.exists(target_snippet_path):
        print(f"❌ {target_snippet_path} not found!")
        return
    with open(target_snippet_path, "r", encoding="utf-8") as f:
        target_snippet = f.read().strip()
    with open(html_path, "r", encoding="utf-8") as f:
        current_html = f.read()
    prompt = website_optimization_prompt(current_html, target_snippet)
    print("\n📝 LLM Prompt:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    client = OpenAIClientWithMCP()
    try:
        response = client.chat_completion([
            {"role": "user", "content": prompt}
        ], model="gpt-4o", temperature=0.3)
        llm_answer = response['choices'][0]['message']['content']
        print("\n🤖 LLM Proposed Changes:")
        print("=" * 50)
        print(llm_answer)
        print("=" * 50)
        # Optionally, parse and apply changes to HTML here
    except Exception as e:
        print(f"❌ LLM call failed: {e}")

if __name__ == "__main__":
    main() 