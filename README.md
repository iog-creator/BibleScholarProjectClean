# BibleScholar Project

> **Comprehensive Bible Study Platform with AI-Powered Analysis**  
> A sophisticated system combining PostgreSQL database, vector search, AI analysis, and web interfaces for deep Biblical scholarship.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/iog-creator/BibleScholarProjectClean.git
cd BibleScholarProjectClean

# Start all servers
.\start_servers.bat

# Access web interface
# API: http://localhost:5000
# Web UI: http://localhost:5002
```

## 📋 System Overview

The BibleScholar Project is a multi-component system designed for comprehensive Biblical analysis:

- **📚 Database Layer**: PostgreSQL with Hebrew/Greek lexicon data (172,928+ entries)
- **🔍 Vector Search**: Semantic search using pgvector and embeddings
- **🤖 AI Integration**: LM Studio integration for contextual analysis
- **🌐 Web Interface**: Flask-based UI for interactive study
- **🔧 MCP Operations**: 37+ automated operations for system management
- **📖 API Layer**: RESTful endpoints for all functionality

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   API Server    │    │   Database      │
│   Port: 5002    │◄──►│   Port: 5000    │◄──►│   PostgreSQL    │
│   Flask App     │    │   REST API      │    │   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   LM Studio     │
                    │   Port: 1234    │
                    │   AI Analysis   │
                    └─────────────────┘
```

### Core Components

#### 1. **BibleScholarLangChain/** - Main Application
- `src/api/api_app.py` - RESTful API server
- `web_app.py` - Main web interface
- `src/database/` - Database connection and models
- `static/` & `templates/` - Web assets

#### 2. **Database Schema**
- **Hebrew Words**: 12,743 entries with morphology
- **Greek Words**: 160,185 entries with lexical data
- **Verses**: Complete Biblical text with cross-references
- **Vector Embeddings**: Semantic search capabilities

#### 3. **MCP Operations** (`mcp_universal_operations.py`)
- 37 registered operations across 7 domains
- Direct access functions for common tasks
- Automated system monitoring and documentation

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 13+ with pgvector extension
- LM Studio (for AI functionality)
- Git

### Installation

1. **Database Setup**
   ```sql
   CREATE DATABASE bible_db;
   CREATE EXTENSION vector;
   ```

2. **Python Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy and configure
   cp .env.example .env
   # Edit database connection details
   ```

4. **Start Services**
   ```bash
   .\start_servers.bat
   ```

## 📖 Usage Guide

### Web Interface
Navigate to `http://localhost:5002` for the main interface:
- **Search**: Semantic and keyword search across Biblical texts
- **Analysis**: AI-powered contextual insights
- **Lexicon**: Hebrew/Greek word studies with morphology
- **Cross-References**: Related passages and themes

### API Endpoints
Base URL: `http://localhost:5000`

```bash
# Vector search
GET /api/search/vector?query=love&limit=10

# Lexicon lookup
GET /api/lexicon/hebrew/{strong_number}

# Verse analysis
POST /api/analyze/verse
{
  "reference": "John 3:16",
  "analysis_type": "contextual"
}
```

### MCP Operations
Direct system management functions:

```python
# Quick logging
log_issue("Description", "component", "severity")

# System health
check_system_health("focus_area")

# Git operations
analyze_git_repo("size_analysis")

# Database queries
database_query("stats")
```

## 🔧 Development

### File Structure
```
CursorMCPWorkspace/
├── BibleScholarLangChain/          # Main application
│   ├── src/
│   │   ├── api/                    # REST API
│   │   ├── database/               # DB connections
│   │   └── utils/                  # Utilities
│   ├── templates/                  # HTML templates
│   ├── static/                     # CSS/JS assets
│   └── web_app.py                  # Main web app
├── archive/                        # Historical files
├── scripts/                        # Utility scripts
├── mcp_universal_operations.py     # MCP system
├── start_servers.bat              # Server startup
└── requirements.txt               # Dependencies
```

### Key Scripts
- `start_servers.bat` - Start all services
- `mcp_universal_operations.py` - System operations
- `BibleScholarLangChain/src/api/api_app.py` - API server
- `BibleScholarLangChain/web_app.py` - Web interface

### Git Workflow
```bash
# Clean commits with semantic versioning
git add .
git commit -m "feat: add new search functionality"
git push origin master
```

## 🗃️ Data Sources

### Lexicon Data
- **Hebrew**: 12,743 words with Strong's numbers, morphology
- **Greek**: 160,185 words with lexical analysis
- **Verses**: Complete Biblical text with metadata

### Vector Embeddings
- Generated using BGE-M3 model via LM Studio
- Stored in PostgreSQL with pgvector extension
- Enables semantic similarity search

## 🚦 System Status

Current system health can be checked via:
```bash
# MCP health check
check_system_health()

# Direct API check
curl http://localhost:5000/health
curl http://localhost:5002/health
```

### Port Usage
- **5000**: API Server (Flask REST API)
- **5002**: Web Interface (Flask Web App)
- **1234**: LM Studio (AI/Embeddings)
- **5432**: PostgreSQL Database

## 🔍 Troubleshooting

### Common Issues

1. **Server Won't Start**
   ```bash
   # Check ports
   netstat -an | findstr "5000\|5002"
   
   # Check logs
   tail -f logs/api_server.log
   ```

2. **Database Connection**
   ```bash
   # Test connection
   psql -h localhost -p 5432 -U postgres -d bible_db
   ```

3. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### MCP System Issues
Use the MCP operations for systematic troubleshooting:
```python
# System analysis
check_system_health("all")

# Database check
database_query("stats")

# Process monitoring
monitor_process("servers")
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` when API server is running
- **MCP Operations**: 37 available operations documented in code
- **Database Schema**: See `src/database/` for models
- **Development Notes**: Check `archive/` for historical documentation

## 🤝 Contributing

1. Follow semantic commit conventions
2. Use MCP operations for system management
3. Update documentation for new features
4. Test with both API and web interfaces
5. Ensure database migrations are included

## 📜 License

This project is for Biblical scholarship and educational purposes.

## 🔗 Links

- **Repository**: https://github.com/iog-creator/BibleScholarProjectClean
- **Issues**: Use GitHub issues for bug reports
- **Documentation**: See `/docs` directory for detailed guides

---

**Last Updated**: 2025-06-10  
**System Version**: v1.0.0  
**MCP Operations**: 37 registered operations  
**Database Entries**: 172,928+ lexical entries 