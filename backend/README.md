# Chrome History RAG System 🚀

A powerful Retrieval-Augmented Generation (RAG) system that integrates your Chrome browsing history with OpenAI's GPT models for intelligent, context-aware search and query responses.

## 🌟 Features

- Chrome browsing history extraction and processing
- Automatic metadata scraping (titles and descriptions) from visited websites
- Embedding generation using OpenAI's text-embedding-ada-002 model
- Fast similarity search powered by FAISS indexing
- Intelligent response generation using GPT-4
- Modern React-based user interface with Tailwind CSS
- Dual-mode operation: RAG-based search and direct OpenAI queries

## 🏗️ System Architecture

```
1. Database Creation (database_creation.py)
   └── Extract Chrome history → Store in SQLite

2. Data Enrichment (scrape_data.py)
   └── Fetch metadata → Update database

3. Index Creation (index_creation.py)
   └── Generate embeddings → Build FAISS index

4. RAG System (rag_system.py)
   └── Query processing → Response generation

5. Frontend (App.js)
   └── React-based user interface
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Google Chrome browser
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chrome-history-rag.git
cd chrome-history-rag
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install @headlessui/react @heroicons/react @tailwindcss/forms autoprefixer postcss tailwindcss
npx tailwindcss init -p
```

4. Configure OpenAI API:
```json
{
    "openai_api_key": "your-api-key-here"
}
```

### Configuration Files

1. Update `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/forms')],
}
```

2. Update `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## 💻 Running the System

### Backend Setup

1. Initialize the database:
```bash
python database_creation.py
python scrape_data.py
python index_creation.py
```

2. Start the backend server:
```bash
python main.py
# For development mode:
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Start the development server:
```bash
cd rag-interface
npm start
```

2. Access the application at `http://localhost:3000`

## 📁 Project Structure

```
chrome-history-rag/
├── backend/
│   ├── config.json
│   ├── database_creation.py
│   ├── scrape_data.py
│   ├── index_creation.py
│   ├── rag_system.py
│   └── main.py
├── rag-interface/
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── index.js
│       └── index.css
├── requirements.txt
└── README.md
```

## ⚙️ Technical Stack

- **Backend**
  - Database: SQLite3
  - Embeddings: OpenAI text-embedding-ada-002
  - Vector Search: Facebook AI Similarity Search (FAISS)
  - API Framework: FastAPI
  - Language Model: GPT-4

- **Frontend**
  - Framework: React
  - Styling: Tailwind CSS
  - UI Components: Headless UI

## 🔧 Troubleshooting

### Common Issues

1. **CORS Issues**
   - Verify backend CORS configuration matches frontend URL
   - Confirm frontend is using correct backend URL

2. **Database Access**
   - Close Chrome before accessing history database
   - Verify Chrome history file path

3. **OpenAI API**
   - Confirm API key is properly configured
   - Monitor API quota and rate limits

4. **FAISS Index**
   - Ensure sufficient memory for index creation
   - Verify index file location

### Configuration Parameters

- `DEFAULT_CHROME_PATH`: Chrome history database location
- `request_delay`: Metadata scraping request delay
- `batch_size`: Embedding generation batch size
- `max_urls`: URL processing limit

## 🤝 Contributing

Contributions are welcome! Please submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.