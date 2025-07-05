# Start
```bash
python -m uvicorn simple_search_server:app --host 0.0.0.0 --port 8000 --reload
```
Snippy

Given a website and a query, we optimize the site's content to increase its chances of being cited by an LLM answering that query.

We extract the site's snippet and inject it into the real search results via a custom MCP server. An LLM uses this server to choose a citation. If our site isn't cited, we modify its snippet using a feedback loop until it is. Once we find an effective snippet, we update the actual website to match it.


![image](https://github.com/user-attachments/assets/a6b94e34-1f43-451c-bf14-6ab85613292d)
