# frontend/src/App.css
.App {
  text-align: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.App-header {
  background: rgba(0, 0, 0, 0.1);
  padding: 20px;
  color: white;
}

.App-header h1 {
  margin: 0 0 10px 0;
  font-size: 2.5rem;
}

.tabs {
  display: flex;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  padding: 0;
}

.tabs button {
  background: none;
  border: none;
  padding: 15px 30px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tabs button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tabs button.active {
  border-bottom-color: #ffd700;
  background: rgba(255, 255, 255, 0.2);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.stats-bar {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-around;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stats-bar span {
  font-weight: bold;
  color: #333;
}

section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 30px;
  margin: 20px 0;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 10px;
  padding: 40px;
  margin: 20px 0;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #667eea;
}

.upload-area input[type="file"] {
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  width: 100%;
}

.search-form {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.search-form input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.search-form button,
.chat-form button,
.upload-area button {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: transform 0.2s;
}

.search-form button:hover,
.chat-form button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.search-form button:disabled,
.chat-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.search-results {
  text-align: left;
  margin-top: 30px;
}

.result-item {
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  padding: 20px;
  margin: 15px 0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-score {
  font-weight: bold;
  color: #667eea;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.result-source {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.result-text {
  line-height: 1.6;
  color: #333;
}

.chat-container {
  max-width: 800px;
  margin: 0 auto;
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: left;
  background: #fafafa;
}

.message {
  margin: 15px 0;
  padding: 15px;
  border-radius: 10px;
  max-width: 80%;
}

.message.user {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  margin-left: auto;
  text-align: right;
}

.message.ai {
  background: #e9ecef;
  color: #333;
  margin-right: auto;
}

.message-content {
  line-height: 1.5;
}

.message-sources {
  margin-top: 10px;
  font-size: 0.8rem;
  color: #666;
}
