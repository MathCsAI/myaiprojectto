---
title: LLM Code Deployment System
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.16.0
app_file: app.py
pinned: false
license: mit
---

# LLM Code Deployment System

An automated system for building, deploying, and evaluating student-submitted web applications using LLM-assisted code generation.

## Features

- 🤖 **LLM-Powered Code Generation**: Automatically generate web apps from task briefs
- 🚀 **GitHub Integration**: Create repos, push code, and enable GitHub Pages
- ✅ **Automated Evaluation**: Run static, dynamic, and LLM-based checks
- 📊 **Dashboard**: Monitor submissions and results in real-time
- 🔄 **Multi-Round System**: Support for initial builds and revisions

## Quick Start

1. Configure environment variables in `.env`
2. Run: `python app.py`
3. Access dashboard at `http://localhost:7860/dashboard`

## API Endpoints

- **Student API**: `/student/api/task` - Receive tasks and deploy apps
- **Evaluation API**: `/evaluation/api/evaluate` - Submit repositories
- **Dashboard**: `/dashboard` - Monitoring interface

## Documentation

See [README.md](./README.md) for full documentation.
