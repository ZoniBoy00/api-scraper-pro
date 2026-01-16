# API Scraper Pro

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Professional-grade API discovery and scraping tool with stealth capabilities and beautiful web interface.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🕷️ **Smart Crawling** | Intelligent URL discovery with configurable depth |
| 🛡️ **Stealth Mode** | Advanced bot detection evasion techniques |
| 📡 **Network Capture** | Automatic API call interception and logging |
| 💾 **Database Storage** | SQLite with automatic backups and statistics |
| 📊 **Web Dashboard** | Beautiful Streamlit interface with analytics |
| ⚙ **CLI Interface** | Full command-line control for automation |
| 📥 **Export Options** | JSON and CSV export capabilities |
| 🔒 **GDPR Compliant** | PII anonymization and robots.txt respect |
| ⚡ **Modular Design** | Clean, maintainable component architecture |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ZoniBoy00/api-scraper-pro.git
cd api-scraper-pro

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Verify installation
python test_installation.py
```

### Usage

#### Web Dashboard (Recommended)

```bash
python main.py dashboard
```

Then:
1. Open `http://localhost:8501` in your browser
2. Enter target URL in sidebar
3. Click "▶ Start Scraping"
4. View results in real-time

#### Command Line

```bash
# Basic scraping
python main.py scrape https://jsonplaceholder.typicode.com

# With options
python main.py scrape https://api.example.com --depth 5

# View statistics
python main.py stats

# Export data
python main.py export --format json --output results.json
```

## 📸 Screenshots

### Dashboard Overview
*Summary statistics and top endpoints visualization*

### Analytics
*Detailed charts and insights*

### Endpoint Browser
*Filterable list with export options*

## 📁 Project Structure

```
api-scraper-pro/
├── main.py                 # CLI entry point
├── core/                   # Scraping engine
│   ├── browser.py         # Stealth browser manager
│   ├── crawler.py         # Smart URL crawler
│   ├── interceptor.py     # Network traffic capture
│   └── database.py        # Data persistence
├── utils/                  # Utility modules
│   ├── helpers.py         # Common functions
│   ├── proxy.py           # Proxy management
│   ├── normalization.py   # PII handling
│   └── robots.py          # Robots.txt parser
├── dashboard/              # Web interface
│   ├── app.py            # Main application
│   ├── utils.py          # Dashboard helpers
│   └── components/       # UI components
└── config/
    └── default.yaml      # Configuration
```

## ⚙️ Configuration

Edit `config/default.yaml` to customize:

```yaml
scraping:
  max_depth: 3              # Crawling depth
  timeout: 30000            # Page timeout (ms)
  headless: true            # Browser mode
  page_delay: 2000          # Delay between pages

stealth:
  enabled: true             # Stealth techniques
  mouse_movements: true     # Simulate human behavior

compliance:
  respect_robots_txt: true  # Honor robots.txt
  anonymize_pii: true       # GDPR compliance
```

## 🎯 Use Cases

- **API Documentation** - Automatically discover and document APIs
- **Security Testing** - Find API endpoints for authorized testing
- **Integration Planning** - Understand third-party API structures
- **Competitive Analysis** - Research API capabilities (authorized)
- **Development** - Speed up API integration planning

## 🛡️ Stealth Features

- User agent rotation
- Mouse movement simulation
- Human-like delays and patterns
- WebGL/Canvas fingerprint protection
- Adaptive rate limiting

## 📊 Dashboard Features

### Control Panel
- ▶️ **Run Tab**: Start/stop scraping with custom settings
- ⚙️ **Settings Tab**: Live configuration editor
- 📊 **Status Tab**: Real-time scraping status

### Main Tabs
- **📊 Overview**: Summary statistics and visualizations
- **📍 Endpoints**: Browse and filter discovered APIs
- **📈 Analytics**: Timeline and distribution charts
- **🔍 Search**: Advanced endpoint search
- **⚙️ Configuration**: Full settings management

### Quick Actions
- 🔄 Refresh dashboard
- 📥 Export JSON/CSV
- 🗑️ Clear all data (with confirmation)

## 📝 Examples

### Basic Scraping
```bash
python main.py scrape https://jsonplaceholder.typicode.com
```

### Deep Crawl
```bash
python main.py scrape https://api.example.com --depth 5 --no-headless
```

### Automated Export
```bash
python main.py scrape https://example.com --output results.json
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/ZoniBoy00/api-scraper-pro.git
cd api-scraper-pro
pip install -r requirements.txt

# Run tests
python test_installation.py
```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is intended for:
- ✅ Educational purposes
- ✅ Authorized security testing
- ✅ Your own websites/APIs
- ✅ APIs with explicit permission

Users are responsible for ensuring proper authorization before scraping any website.

## 🤝 Support

- 📖 [Documentation](README.md)
- 🚀 [Quick Start Guide](QUICKSTART.md)
- 🐛 [Report Issues](https://github.com/yourusername/api-scraper-pro/issues)
- 💬 [Discussions](https://github.com/yourusername/api-scraper-pro/discussions)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

## 📊 Tech Stack

- **Python 3.8+**
- **Playwright** - Browser automation
- **Streamlit** - Web interface
- **SQLite** - Data storage
- **Plotly** - Data visualization
- **AsyncIO** - Concurrent operations

## 🏆 Credits

Created with ❤️ by the API Scraper Pro team

---
