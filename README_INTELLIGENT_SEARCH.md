# 🧠 Intelligent Search Tool

This tool allows the LLM to intelligently decide which websites to visit for deeper content extraction, creating a more sophisticated research system.

## 🎯 How It Works

The intelligent search tool performs a 4-step process:

### 1. 🔍 Initial Search
- Uses your MCP server to perform web search
- Gets multiple search results (titles, links, snippets)
- Includes test entries to verify functionality

### 2. 🧠 LLM Analysis & Site Selection
- LLM analyzes all search results
- Evaluates each site based on:
  - **Relevance** to the query
  - **Authority** and reputation
  - **Content Quality** based on snippets
  - **Uniqueness** of information
- Provides confidence scores (1-10) and reasoning
- Selects the most valuable sites to visit

### 3. 📄 Content Extraction
- Visits selected websites
- Extracts detailed content using web scraping
- Handles various website structures
- Respects robots.txt and rate limits

### 4. 📝 Optimized Summary
- LLM creates comprehensive summary from extracted content
- Synthesizes information from multiple sources
- Provides well-structured, detailed answers
- Cites sources appropriately

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# With conda
conda activate hackathon
pip install beautifulsoup4

# Or without conda
pip3 install beautifulsoup4
```

### 2. Start Your MCP Server

```bash
# Start the enhanced search server
./start_openai_mcp.sh
```

### 3. Run the Intelligent Search Tool

#### Option A: Interactive Mode (Recommended)

```bash
# With conda
conda activate hackathon
python interactive_intelligent_search.py

# Or without conda
python3 interactive_intelligent_search.py
```

#### Option B: Programmatic Usage

```python
from intelligent_search_tool import IntelligentSearchTool

# Initialize the tool
tool = IntelligentSearchTool()

# Perform intelligent search
results = tool.intelligent_search("What are the latest features of OpenAI's GPT-4?")

if results.get('success'):
    print("📝 OPTIMIZED SUMMARY:")
    print(results['summary'])
    
    print("\n📊 STATISTICS:")
    print(f"Initial results: {len(results['initial_results'])}")
    print(f"Sites selected by LLM: {len(results['selected_sites'])}")
    print(f"Content extracted: {len([c for c in results['extracted_content'] if c.get('extraction_success')])}")
```

## 📁 Files Overview

### Core Files

- **`intelligent_search_tool.py`** - Main intelligent search engine
- **`interactive_intelligent_search.py`** - Interactive interface
- **`enhanced_search_server.py`** - MCP server with test entries

### Dependencies

- **`openai_client_with_mcp.py`** - OpenAI client with MCP integration
- **`requirements.txt`** - Updated with beautifulsoup4

## 💡 Usage Examples

### Interactive Mode

```
🔍 Enter your search query: What are the latest features of OpenAI's GPT-4?

🚀 Starting intelligent search for: 'What are the latest features of OpenAI's GPT-4?'
============================================================

📋 INITIAL SEARCH RESULTS:
----------------------------------------
1. 📄 🧪 MCP Test Entry - Tool Working!
   🔗 https://github.com/modelcontextprotocol
   📝 This test entry confirms the MCP search tool is working...

2. 📄 OpenAI GPT-4 Features and Capabilities
   🔗 https://platform.openai.com/docs/models/gpt-4
   📝 Comprehensive guide to GPT-4 features...

🧠 LLM SITE SELECTION:
----------------------------------------
1. 🎯 OpenAI GPT-4 Features and Capabilities
   🔗 https://platform.openai.com/docs/models/gpt-4
   ⭐ Confidence: 9/10
   💭 Reason: Official OpenAI documentation, most authoritative source

2. 🎯 Latest GPT-4 Updates and Features
   🔗 https://openai.com/blog/gpt-4
   ⭐ Confidence: 8/10
   💭 Reason: Official blog with latest updates

📄 CONTENT EXTRACTION RESULTS:
----------------------------------------
1. ✅ Success - OpenAI GPT-4 Features and Capabilities
   🔗 https://platform.openai.com/docs/models/gpt-4
   ⭐ Confidence: 9/10
   📏 Content length: 3247 characters

2. ✅ Success - Latest GPT-4 Updates and Features
   🔗 https://openai.com/blog/gpt-4
   ⭐ Confidence: 8/10
   📏 Content length: 2156 characters

📝 OPTIMIZED SUMMARY:
============================================================
Based on the latest information from OpenAI's official documentation and blog...

📊 SEARCH STATISTICS:
----------------------------------------
   • Initial search results: 8
   • Sites selected by LLM: 2
   • Content extraction attempts: 2
   • Successful extractions: 2
   • Average confidence score: 8.5/10
```

### Programmatic Usage

```python
from intelligent_search_tool import IntelligentSearchTool

# Initialize tool
tool = IntelligentSearchTool()

# Perform search
results = tool.intelligent_search("How to implement machine learning in Python?")

# Access different parts of the results
initial_results = results['initial_results']  # Raw search results
selected_sites = results['selected_sites']    # LLM's site selection
extracted_content = results['extracted_content']  # Extracted content
summary = results['summary']  # Final optimized summary

# Check success
if results.get('success'):
    print("Search completed successfully!")
else:
    print(f"Search failed: {results.get('error')}")
```

## 🎯 Key Features

### LLM-Guided Site Selection

The LLM analyzes search results and decides which sites to visit based on:

- **Relevance Score** - How well the site matches the query
- **Authority Assessment** - Reputation and credibility
- **Content Quality** - Based on snippets and titles
- **Information Uniqueness** - Avoiding duplicate sources

### Intelligent Content Extraction

- **Smart Parsing** - Handles various website structures
- **Content Focus** - Extracts main content, not ads/navigation
- **Rate Limiting** - Respects websites and robots.txt
- **Error Handling** - Graceful failure for problematic sites

### Comprehensive Summarization

- **Multi-Source Synthesis** - Combines information from multiple sites
- **Source Attribution** - Properly cites sources
- **Structured Output** - Well-organized, detailed summaries
- **Query-Focused** - Directly answers the original question

## 🔧 Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (for web search)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CSE_ID=your-google-cse-id-here
```

### Customization Options

```python
# Initialize with custom settings
tool = IntelligentSearchTool(
    openai_api_key="your-key",  # Optional, uses env var by default
    mcp_url="http://localhost:8000"  # MCP server URL
)

# Customize search parameters
results = tool.intelligent_search(
    query="Your search query",
    max_sites=5  # Maximum sites to visit (default: 5)
)
```

## 📊 Understanding the Results

### Initial Search Results
- Raw search results from your MCP server
- Includes test entries to verify functionality
- Titles, links, and snippets

### LLM Site Selection
- Sites chosen by the LLM for deeper analysis
- Confidence scores (1-10) for each site
- Reasoning for why each site was selected

### Content Extraction Results
- Success/failure status for each site
- Extracted content length
- Error messages for failed extractions

### Optimized Summary
- Comprehensive answer synthesized from multiple sources
- Well-structured and detailed
- Properly cites sources

## 🛠️ Troubleshooting

### Common Issues

1. **MCP Server Not Running**
   ```bash
   # Start the server
   ./start_openai_mcp.sh
   ```

2. **Missing Dependencies**
   ```bash
   # Install beautifulsoup4
   pip install beautifulsoup4
   ```

3. **Content Extraction Failures**
   - Some sites block scraping
   - Check if site is accessible
   - Verify robots.txt compliance

4. **LLM Analysis Failures**
   - Check OpenAI API key
   - Verify API quota
   - Check network connectivity

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
tool = IntelligentSearchTool()
results = tool.intelligent_search("test query")
```

## 🎨 Advanced Usage

### Custom Site Selection Criteria

You can modify the LLM's analysis prompt in `intelligent_search_tool.py`:

```python
# In analyze_search_results method
analysis_prompt = f"""
Your task is to analyze these results and decide which websites would be most valuable to visit.

Consider these criteria:
1. **Relevance**: How well does the site match the search query?
2. **Authority**: Is this a reputable, authoritative source?
3. **Content Quality**: Does the snippet suggest high-quality, detailed content?
4. **Uniqueness**: Does this site offer unique information not found elsewhere?
5. **Recency**: Is the information up-to-date?
6. **Depth**: Does the site likely contain comprehensive information?

For each site you want to visit, provide:
- A confidence score (1-10)
- A brief reason why this site is valuable
- What specific information you expect to find

Return your analysis as a JSON array.
"""
```

### Custom Content Extraction

Modify the content extraction logic in `_extract_site_content`:

```python
def _extract_site_content(self, url: str) -> Optional[str]:
    # Add custom selectors for specific sites
    custom_selectors = {
        'wikipedia.org': '.mw-parser-output',
        'stackoverflow.com': '.post-text',
        'github.com': '.markdown-body'
    }
    
    # Use custom selectors if available
    domain = urlparse(url).netloc
    if domain in custom_selectors:
        content_selectors.insert(0, custom_selectors[domain])
```

## 🚀 Next Steps

1. **Add More Site Selectors** - Improve content extraction for specific sites
2. **Implement Caching** - Cache extracted content to avoid re-scraping
3. **Add Site Blacklisting** - Exclude problematic sites
4. **Implement Parallel Extraction** - Speed up content extraction
5. **Add Content Filtering** - Remove ads, navigation, etc.
6. **Implement Site Ranking** - Use historical success rates

## 📚 Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Web Scraping Best Practices](https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/)

---

**Happy intelligent searching! 🧠🔍**

Your LLM can now intelligently decide which websites to visit and extract the most valuable information for comprehensive research. 