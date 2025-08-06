#!/usr/bin/env python3
"""
diagnose.py - Діагностика RAG системи
Перевіряє стан всіх компонентів та виявляє проблеми
"""

import requests
import json
import sys
import time
from typing import Dict, List, Tuple, Optional
import subprocess
import os
from datetime import datetime

class RAGDiagnostics:
    def __init__(self):
        self.services = {
            'ChromaDB': {
                'url': 'http://localhost:8001/api/v1/heartbeat',
                'container': 'rag-system-chromadb-1',
                'healthy': False
            },
            'RAG Service': {
                'url': 'http://localhost:8002/health',
                'container': 'rag-system-rag-service-1',
                'healthy': False
            },
            'LLM Service': {
                'url': 'http://localhost:8003/health',
                'container': 'rag-system-llm-service-1',
                'healthy': False
            },
            'Ollama': {
                'url': 'http://localhost:11434/api/tags',
                'container': 'rag-system-ollama-1',
                'healthy': False
            },
            'Frontend': {
                'url': 'http://localhost:3000',
                'container': 'rag-system-frontend-1',
                'healthy': False
            },
            'Redis': {
                'url': None,  # Redis doesn't have HTTP endpoint
                'container': 'rag-system-redis-1',
                'healthy': False
            }
        }
        
        self.results = []

    def print_header(self):
        print("=" * 60)
        print("🔍 RAG SYSTEM DIAGNOSTICS")
        print("=" * 60)
        print(f"📅 Час запуску: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def check_docker_compose(self) -> bool:
        """Перевірка чи запущені контейнери"""
        print("🐳 Перевірка Docker контейнерів...")
        try:
            result = subprocess.run(['docker', 'compose', 'ps'], 
                                  capture_output=True, text=True, check=True)
            print("📊 Статус контейнерів:")
            print(result.stdout)
            
            # Перевірка чи всі контейнери працюють
            running_containers = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip() and 'Up' in line:
                    container_name = line.split()[0]
                    running_containers.append(container_name)
            
            print(f"✅ Запущено контейнерів: {len(running_containers)}")
            return len(running_containers) > 0
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Помилка Docker Compose: {e}")
            print("💡 Спробуйте: docker compose up -d")
            return False
        except FileNotFoundError:
            print("❌ Docker Compose не знайдено!")
            print("💡 Встановіть Docker та Docker Compose")
            return False

    def check_service_health(self, name: str, url: Optional[str], timeout: int = 5) -> Tuple[bool, str]:
        """Перевірка здоров'я сервісу"""
        if url is None:
            return True, "No HTTP endpoint"
        
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return True, f"OK ({response.status_code})"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_container_logs(self, container_name: str, lines: int = 10) -> str:
        """Отримання логів контейнера"""
        try:
            result = subprocess.run(['docker', 'logs', '--tail', str(lines), container_name], 
                                  capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Не вдалося отримати логи: {e}"

    def check_all_services(self):
        """Перевірка всіх сервісів"""
        print("🔍 Перевірка здоров'я сервісів...")
        print("-" * 60)
        
        for name, config in self.services.items():
            print(f"Перевірка {name}...", end=" ")
            
            healthy, message = self.check_service_health(name, config['url'])
            config['healthy'] = healthy
            
            if healthy:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
                
                # Показуємо логи для проблемних сервісів
                print(f"📋 Останні логи {config['container']}:")
                logs = self.get_container_logs(config['container'], 5)
                for line in logs.split('\n')[-5:]:
                    if line.strip():
                        print(f"  {line}")
                print()

    def check_disk_space(self):
        """Перевірка дискового простору"""
        print("💾 Перевірка дискового простору...")
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, check=True)
            print(result.stdout)
        except Exception as e:
            print(f"❌ Помилка перевірки диску: {e}")

    def check_docker_resources(self):
        """Перевірка ресурсів Docker"""
        print("🔧 Перевірка ресурсів Docker...")
        try:
            # Docker system df
            result = subprocess.run(['docker', 'system', 'df'], 
                                  capture_output=True, text=True, check=True)
            print("📊 Використання ресурсів Docker:")
            print(result.stdout)
            
            # Статистика контейнерів
            result = subprocess.run(['docker', 'stats', '--no-stream'], 
                                  capture_output=True, text=True, check=True)
            print("📈 Статистика контейнерів:")
            print(result.stdout)
            
        except Exception as e:
            print(f"❌ Помилка перевірки ресурсів: {e}")

    def test_basic_functionality(self):
        """Тестування базової функціональності"""
        print("🧪 Тестування базової функціональності...")
        
        # Тест RAG Service
        if self.services['RAG Service']['healthy']:
            try:
                # Тест пошуку
                response = requests.post('http://localhost:8002/search', 
                                       json={'query': 'test', 'limit': 1}, 
                                       timeout=10)
                if response.status_code == 200:
                    print("✅ RAG пошук працює")
                else:
                    print(f"❌ RAG пошук: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ RAG пошук: {e}")
        
        # Тест LLM Service
        if self.services['LLM Service']['healthy']:
            try:
                response = requests.get('http://localhost:8003/models', timeout=10)
                if response.status_code == 200:
                    print("✅ LLM сервіс працює")
                    models = response.json()
                    print(f"📦 Доступні моделі: {len(models.get('models', []))}")
                else:
                    print(f"❌ LLM сервіс: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ LLM сервіс: {e}")

    def generate_recommendations(self):
        """Генерація рекомендацій для виправлення проблем"""
        print("\n💡 РЕКОМЕНДАЦІЇ ДЛЯ ВИПРАВЛЕННЯ:")
        print("-" * 60)
        
        unhealthy_services = [name for name, config in self.services.items() 
                            if not config['healthy']]
        
        if not unhealthy_services:
            print("✅ Всі сервіси працюють нормально!")
            return
        
        print("❌ Проблемні сервіси:", ", ".join(unhealthy_services))
        print()
        
        recommendations = [
            "1. 🔄 Перезапустіть систему: docker compose down && docker compose up -d",
            "2. 🧹 Очистіть Docker: docker system prune -f",
            "3. 📦 Перебілдьте образи: docker compose build --no-cache",
            "4. 🔍 Перевірте логи: docker compose logs -f [service-name]",
            "5. 💾 Перевірте вільне місце на диску",
            "6. 🔧 Перевірте порти (8001-8003, 11434, 3000): netstat -tulpn",
            "7. 🐳 Перевірте Docker daemon: docker info"
        ]
        
        for rec in recommendations:
            print(rec)

    def export_results(self, filename: str = "rag_diagnostics.json"):
        """Експорт результатів діагностики"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'services': self.services,
            'summary': {
                'total_services': len(self.services),
                'healthy_services': sum(1 for s in self.services.values() if s['healthy']),
                'unhealthy_services': sum(1 for s in self.services.values() if not s['healthy'])
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Результати збережено в {filename}")
        except Exception as e:
            print(f"❌ Помилка збереження: {e}")

    def run_full_diagnostics(self):
        """Запуск повної діагностики"""
        self.print_header()
        
        # Основні перевірки
        if not self.check_docker_compose():
            print("❌ Docker контейнери не запущені. Завершення діагностики.")
            return False
        
        print()
        self.check_all_services()
        print()
        self.check_disk_space()
        print()
        self.check_docker_resources()
        print()
        self.test_basic_functionality()
        
        # Підсумок та рекомендації
        self.generate_recommendations()
        
        # Експорт результатів
        print()
        self.export_results()
        
        # Фінальний підсумок
        healthy_count = sum(1 for s in self.services.values() if s['healthy'])
        total_count = len(self.services)
        
        print(f"\n📊 ПІДСУМОК: {healthy_count}/{total_count} сервісів працює нормально")
        
        if healthy_count == total_count:
            print("🎉 Система повністю працездатна!")
            return True
        else:
            print("⚠️  Система має проблеми, що потребують уваги")
            return False

def main():
    """Головна функція"""
    print("Запуск діагностики RAG системи...\n")
    
    diagnostics = RAGDiagnostics()
    success = diagnostics.run_full_diagnostics()
    
    # Код виходу для використання в скриптах
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()