# Azure Data Factory Pipeline Generator

A web application that helps users design Azure Data Factory pipelines and generate JSON of ADF components through natural language conversations.

## Features

- Natural language pipeline generation using Azure OpenAI
- Interactive pipeline visualization
- Real-time chat interface  
- Pipeline configuration generation and validation 

## Prerequisites

- Python 3.8+
- Node.js 14+ 
- Perplexity API
 
### Backend Setup

1. Navigate to the backend directory:
```
cd ./backend
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Install dependencies:
```
Rename .env_example to .env and add perplexity api key in it
```

4. Start the backend server:
```
python app.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```
cd ./frontend
```

2. Install dependencies:
```
npm install
```

3. Start the development server:
```
npm start
```
 
 