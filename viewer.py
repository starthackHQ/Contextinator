#!/usr/bin/env python3
from flask import Flask, render_template_string, request
import chromadb

app = Flask(__name__)
client = chromadb.HttpClient(host="localhost", port=8000)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ChromaDB Viewer</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .meta { color: #666; font-size: 12px; }
        .content { background: #f5f5f5; padding: 10px; margin-top: 10px; white-space: pre-wrap; }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>📚 Collection: {{ collection_name }}</h1>
    <p>Total items: {{ total }}</p>
    
    <div class="nav">
        {% if offset > 0 %}
        <button onclick="location.href='?offset={{ offset - limit }}'">← Previous</button>
        {% endif %}
        {% if offset + limit < total %}
        <button onclick="location.href='?offset={{ offset + limit }}'">Next →</button>
        {% endif %}
        <span>Showing {{ offset + 1 }} - {{ min(offset + limit, total) }} of {{ total }}</span>
    </div>
    
    {% for item in items %}
    <div class="item">
        <strong>{{ loop.index + offset }}. {{ item.meta.get('node_name', 'N/A') }}</strong>
        <div class="meta">
            📄 File: {{ item.meta.get('file_path', 'N/A') }}<br>
            🏷️ Type: {{ item.meta.get('node_type', 'N/A') }}<br>
            📍 Lines: {{ item.meta.get('start_line', 'N/A') }} - {{ item.meta.get('end_line', 'N/A') }}
        </div>
        <div class="content">{{ item.content[:300] }}{% if item.content|length > 300 %}...{% endif %}</div>
    </div>
    {% endfor %}
    
    <div class="nav">
        {% if offset > 0 %}
        <button onclick="location.href='?offset={{ offset - limit }}'">← Previous</button>
        {% endif %}
        {% if offset + limit < total %}
        <button onclick="location.href='?offset={{ offset + limit }}'">Next →</button>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    collection = client.get_collection(name="symentic-v2")
    total = collection.count()
    
    offset = int(request.args.get('offset', 0))
    limit = 20
    
    results = collection.get(
        limit=limit,
        offset=offset,
        include=['documents', 'metadatas']
    )
    
    items = []
    for doc, meta in zip(results['documents'], results['metadatas']):
        items.append({'content': doc, 'meta': meta})
    
    return render_template_string(
        HTML,
        collection_name="symentic-v2",
        total=total,
        offset=offset,
        limit=limit,
        items=items,
        min=min
    )

if __name__ == '__main__':
    print("🌐 Starting ChromaDB Viewer at http://localhost:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)
