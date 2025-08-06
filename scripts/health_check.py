#!/usr/bin/env python3
# scripts/health_check.py - Перевірка здоров'я всіх компонентів RAG системи

import requests
import json
import sys
import time
from typing import Dict, List, Tuple

class HealthChecker:
    def __init__(self):
        self.services = {
            'ChromaDB': 'http://localhost:8001/api/v1/heartbeat',
            'RAG Service': 'http://localhost:8002/health',
            'LLM Service': 'http://localhost:8003/health',
            'Ollama': 'http://localhost:11434/api/tags',
            'Frontend': 'http://localhost:3000',
            'Redis': '