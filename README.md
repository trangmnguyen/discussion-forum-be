## Overview
FastAPI-based Reddit-style discussion forum backend.

### API overview
This API supports:
- Creating users
- Creating and commenting on discussions
- Retrieving all discussions
- Editing and deleting of discussions and comments

### Set up
- Requirements: Python 3.9+
- Install on your local environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- Run locally
```bash
uvicorn app.main:app --reload
```