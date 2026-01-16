# Quick Start Guide - API Scraper Pro

Get started in 5 minutes!

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browser

```bash
playwright install chromium
```

### 3. Test Installation

```bash
python test_installation.py
```

You should see:
```
✓ All imports successful
✓ Configuration loaded
✓ Database initialized
✓ Installation complete!
```

## Choose Your Interface

### Option A: Web Dashboard (Easiest)

**Best for:** Visual interface, beginners, exploration

```bash
python main.py dashboard
```

**Then:**
1. Enter URL in sidebar (e.g., `https://jsonplaceholder.typicode.com`)
2. Configure depth (default: 3)
3. Click "▶ Start Scraping"
4. New console window opens showing progress
5. Wait for completion
6. **Press ENTER in console to close it**
7. Refresh dashboard to see results
8. Browse endpoints, view analytics
9. Export data if needed

**Dashboard Features:**
- Real-time status monitoring
- Visual analytics and charts
- Endpoint browser with filtering
- Advanced search
- One-click export
- Live configuration editor

### Option B: Command Line (Fastest)

**Best for:** Automation, scripting, advanced users

#### Basic Scraping

```bash
python main.py scrape https://jsonplaceholder.typicode.com
```

**What happens:**
1. Browser opens (or runs headless)
2. Starts crawling from URL
3. Captures all API calls
4. Saves to database
5. Shows statistics
6. **Window stays open - press ENTER to close**

#### View Results

```bash
python main.py stats
```

Shows:
- Total endpoints found
- Total API calls captured
- Database size
- Top 10 endpoints

#### Export Data

```bash
# Export as JSON
python main.py export --format json --output results.json

# Export as CSV
python main.py export --format csv --output results.csv
```

## First Scraping Job

### Example 1: Simple API

```bash
# Using dashboard
python main.py dashboard
# Enter: https://jsonplaceholder.typicode.com
# Click: Start Scraping

# OR using CLI
python main.py scrape https://jsonplaceholder.typicode.com
```

**Expected results:**
- 10-20 endpoints discovered
- GET/POST/PUT/DELETE methods
- JSON responses captured

### Example 2: Deeper Crawl

```bash
python main.py scrape https://jsonplaceholder.typicode.com --depth 5
```

**Expected results:**
- More endpoints discovered
- Longer scraping time
- More comprehensive coverage

### Example 3: Visible Browser

```bash
python main.py scrape https://jsonplaceholder.typicode.com --no-headless
```

**Expected results:**
- See Chrome browser open
- Watch navigation happen
- Good for debugging

## Understanding Output

### During Scraping

Console shows:
```
20:00:00 | INFO  | Starting scrape: https://example.com
20:00:01 | INFO  | Browser initialized
20:00:02 | INFO  | Crawling (depth 0): https://example.com
20:00:03 | DEBUG | Found 5 links
20:00:04 | INFO  | API call detected: GET /api/users
```

### After Scraping

Statistics display:
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Category          ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Pages crawled     │     15 │
│ APIs found        │     42 │
│ Unique endpoints  │     28 │
│ Database size     │  0.5 MB│
└───────────────────┴────────┘
```

**Press ENTER to close the window**

## Configuration

### Basic Config (`config/default.yaml`)

```yaml
scraping:
  max_depth: 3          # How deep to crawl
  timeout: 30000        # Page timeout (ms)
  headless: true        # Show browser?
  page_delay: 2000      # Delay between pages

stealth:
  enabled: true         # Use stealth mode?

compliance:
  respect_robots_txt: true
  anonymize_pii: true
```

### Quick Changes

**Via Dashboard:**
1. Settings tab in sidebar
2. Modify values
3. Click "Save Settings"

**Via File:**
1. Edit `config/default.yaml`
2. Save file
3. Restart scraping

## Common Tasks

### Task 1: Scrape and Export

```bash
# Scrape
python main.py scrape https://api.example.com --depth 3

# Export
python main.py export --format json --output my_apis.json
```

### Task 2: Monitor Progress

```bash
# Start scraping
python main.py scrape https://example.com

# In another terminal - view logs
tail -f logs/scraper.log  # Unix
Get-Content logs/scraper.log -Wait  # Windows PowerShell
```

### Task 3: Browse Results

```bash
# Launch dashboard
python main.py dashboard

# Browse to: http://localhost:8501
# Click: Endpoints tab
# Use: Filters and search
```

## Troubleshooting

### Issue: Browser Won't Start

```bash
# Solution: Reinstall Playwright
playwright install chromium --force
```

### Issue: Permission Denied

```bash
# Solution: Run as administrator (Windows) or with sudo (Unix)
# Or install to user directory:
pip install --user -r requirements.txt
```

### Issue: ModuleNotFoundError

```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Database Locked

```bash
# Solution: Close all connections and restart
# Or delete database (data will be lost):
rm data/scraper.db
```

### Issue: Console Window Closes Immediately

**This is fixed!** The window now stays open and shows:
```
============================================================
Press ENTER to close this window...
============================================================
```

Just press ENTER when you're done reviewing the stats.

## File Locations

```
api-scraper-pro/
├── config/default.yaml    ← Configuration
├── data/scraper.db        ← Your data (created automatically)
├── logs/scraper.log       ← Detailed logs
└── exports/               ← Your exports (created when needed)
    ├── export.json
    └── export.csv
```

## Next Steps

1. ✅ **Basic Scraping** - Done with this guide
2. 📚 **Read README.md** - Full documentation
3. ⚙ **Customize Config** - Adjust settings
4. 🔧 **Advanced Features** - Explore stealth, proxies, etc.
5. 📊 **Dashboard** - Use web interface

## Tips

- Start with **small sites** to test
- Use **headless mode** for speed
- Check **logs/** for debugging
- **Database persists** between runs
- **Export often** to backup data
- Console windows **stay open** - press ENTER to close

## Command Reference

```bash
# Scraping
python main.py scrape <URL> [OPTIONS]

# Statistics  
python main.py stats

# Export
python main.py export --format json --output FILE
python main.py export --format csv --output FILE

# Dashboard
python main.py dashboard
```

## Dashboard vs CLI

| Feature | Dashboard | CLI |
|---------|-----------|-----|
| Start/Stop | ✅ Click button | ✅ Run command |
| Real-time Status | ✅ Yes | ❌ No |
| Live Config Edit | ✅ Yes | ❌ Edit file |
| Visual Analytics | ✅ Yes | ❌ No |
| Data Browser | ✅ Yes | ❌ No |
| Export | ✅ One click | ✅ Command |
| Automation | ❌ No | ✅ Yes |
| Speed | Slower | ✅ Faster |

**Recommendation:** Use dashboard for exploration, CLI for automation.

## Success! 🎉

You're now ready to discover and scrape APIs!

**Happy scraping!**

---

Need help? Check:
- README.md for full documentation
- logs/scraper.log for detailed logs
- config/default.yaml for settings
