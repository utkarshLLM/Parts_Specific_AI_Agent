# Instalily AI Backend Integration Guide

## Quick Start

### 1. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Deepseek API key
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# Run the backend
python main.py
```

Backend will start on `http://localhost:5000` by default.

---

## API Endpoints

### Chat Endpoint
**POST** `/api/chat`

Send a message to the AI chat agent.

```javascript
fetch('http://localhost:5000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "How can I install part number PS11752778?",
    session_id: "user-123" // optional
  })
})
.then(res => res.json())
.then(data => {
  console.log(data.response_text);
  console.log(data.products);
  console.log(data.suggestions);
})
```

**Response:**
```json
{
  "response_text": "The ice maker assembly PS11752778 can be installed...",
  "products": [
    {
      "id": "PS11752778",
      "name": "Ice Maker Assembly",
      "price": "$89.99",
      "compatible_models": ["WRF989SDAW", "WRF970SMHW"],
      "link": "https://www.partselect.com/products/PS11752778",
      ...
    }
  ],
  "suggestions": [
    "Check compatibility with my model",
    "View installation guide",
    "Add to cart"
  ],
  "intent": "installation",
  "metadata": {
    "session_id": "user-123",
    "message_count": 1
  }
}
```

---

### Product Search
**GET** `/api/products/search?q=ice maker&category=refrigerator&limit=5`

Search for products.

```javascript
fetch('http://localhost:5000/api/products/search?q=ice+maker&category=refrigerator&limit=5')
  .then(res => res.json())
  .then(data => console.log(data.products))
```

---

### Get Product Details
**GET** `/api/products/:id`

Get detailed information about a specific product.

```javascript
fetch('http://localhost:5000/api/products/PS11752778')
  .then(res => res.json())
  .then(data => console.log(data.product))
```

---

### Check Compatibility
**POST** `/api/compatibility`

Check if a part is compatible with a model.

```javascript
fetch('http://localhost:5000/api/compatibility', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    part_id: "PS11752778",
    model_number: "WDT780SAEM1"
  })
})
.then(res => res.json())
.then(data => {
  console.log(data.compatible); // true/false
  console.log(data.message);
})
```

---

### Session Management
**GET** `/api/session/info?session_id=user-123`

Get information about a session.

```javascript
fetch('http://localhost:5000/api/session/info?session_id=user-123')
  .then(res => res.json())
  .then(data => console.log(data))
```

---

**POST** `/api/session/clear`

Clear a session history.

```javascript
fetch('http://localhost:5000/api/session/clear', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id: "user-123" })
})
```

---

## Frontend Implementation

### Basic React Hook for Chat

```javascript
import { useState } from 'react';

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState('user-' + Math.random().toString(36).substr(2, 9));

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: inputValue }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputValue,
          session_id: sessionId
        })
      });

      const data = await response.json();

      // Add assistant message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response_text,
        products: data.products,
        suggestions: data.suggestions,
        intent: data.intent
      }]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.'
      }]);
    }

    setInputValue('');
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.products && msg.products.length > 0 && (
              <div className="products">
                {msg.products.map(product => (
                  <div key={product.id} className="product-card">
                    <h4>{product.name}</h4>
                    <p>Part #: {product.id}</p>
                    <p>Price: {product.price}</p>
                    <a href={product.link} target="_blank">View on PartSelect</a>
                  </div>
                ))}
              </div>
            )}
            {msg.suggestions && (
              <div className="suggestions">
                {msg.suggestions.map((sug, i) => (
                  <button key={i} onClick={() => setInputValue(sug)}>
                    {sug}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about parts, compatibility, installation..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default ChatComponent;
```

---

## Integration Checklist

- [ ] Backend running on localhost:5000
- [ ] DEEPSEEK_API_KEY set in .env file
- [ ] Frontend calls `/api/chat` endpoint
- [ ] Frontend handles products array in response
- [ ] Frontend displays suggestions
- [ ] Session management implemented (optional but recommended)
- [ ] CORS errors resolved (backend has CORS enabled)
- [ ] Error handling for network failures

---

## Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
1. Backend has `CORS(app)` enabled (it does by default)
2. Frontend is calling `http://localhost:5000` (not `localhost:5000`)
3. Requests include `Content-Type: application/json` header

### API Key Errors
- Ensure `DEEPSEEK_API_KEY` is set in .env
- The API key should be from https://api.deepseek.com
- Restart the backend after updating .env

### No Products Showing
- Check that sample products loaded correctly
- Vector store should initialize with 10 sample products
- Try searching by part number (e.g., "PS11752778")

### Slow Responses
- First request may be slower as model loads
- For production, consider using FAISS for faster vector search
- Cache responses using Redis for frequently asked questions

---

## Production Deployment

### Using Gunicorn (instead of Flask dev server)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

### Environment Variables for Production
- Set `FLASK_ENV=production`
- Set `FLASK_DEBUG=false`
- Use a real database instead of in-memory storage
- Deploy with Gunicorn + Nginx
- Set proper CORS origins (not * in production)

---

## File Structure

```
backend/
├── main.py                 # Flask app entry point
├── chat_handler.py        # Chat orchestration
├── deepseek_client.py     # LLM integration
├── product_service.py     # Product queries
├── vector_store.py        # Embeddings & search
├── sample_products.py     # Demo product data
├── scrapers.py            # Data pipeline (optional)
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
└── README.md              # This file
```

---

## Next Steps

1. **Customize Product Data**: Replace sample_products.py with real PartSelect data
2. **Improve Embeddings**: Use sentence-transformers instead of simple TF-IDF
3. **Add Vector Database**: Migrate from numpy to FAISS or Pinecone for scale
4. **Implement Caching**: Add Redis for faster responses
5. **Add Analytics**: Track common questions and improve responses
6. **Mobile Optimization**: Test on mobile devices and optimize UI

---

For more help, see the docstrings in each Python file!