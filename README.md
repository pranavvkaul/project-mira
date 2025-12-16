# project-mira

````markdown
# Agent Mira: Property Comparison and Price Prediction App

## Overview

Agent Mira is a full stack web application built as a technical case study.  
The application enables users to compare real estate properties side by side and predict property prices using a machine learning model based on structured property features.

As an advanced enhancement, the project also includes an AI powered conversational assistant that understands the context of the selected properties and answers comparison related questions using natural language.

---

## Key Features

### Property Comparison Engine
- Compare two properties selected from a mock dataset
- Side by side display of price, size, bedrooms, bathrooms, and amenities
- Clean, responsive UI optimized for clarity

### Machine Learning Price Prediction
- Integrates a pre trained Scikit Learn regression model
- Backend API accepts structured property data and returns a predicted price
- Graceful error handling for invalid or missing feature inputs

### Context Aware AI Assistant (Bonus)
- Powered by Google Gemini API
- Understands the currently selected properties
- Answers comparative and analytical questions using natural language
- Example queries:
  - Which property is better for a family
  - Compare price per square foot
  - Which home offers better amenities

---

## Tech Stack

| Layer | Technology | Purpose |
|------|-----------|---------|
| Frontend | React.js | UI and state management |
| Styling | Tailwind CSS | Utility first styling |
| Backend | FastAPI | API layer and ML inference |
| Machine Learning | Scikit Learn | Price prediction model |
| AI Assistant | Google Gemini API | Natural language reasoning |

---

## Project Structure

```text
PROJECT-MIRA/
├── backend/
│   ├── complex_price_model_v2.pkl
│   ├── main.py
│   ├── merging.py
│   ├── requirements.txt
│   └── data/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chatbot.js
│   │   │   └── PropertyComparison.js
│   │   ├── data.js
│   │   ├── App.js
│   │   └── index.js
│   ├── .env
│   ├── package.json
│   └── tailwind.config.js
└── README.md
````

---

## Installation and Setup

### Prerequisites

* Node.js version 14 or higher
* Python version 3.8 or higher
* Google Gemini API key (required for chatbot)

---

### Backend Setup

1. Navigate to the backend directory

```bash
cd backend
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
pip install fastapi uvicorn pandas scikit-learn pydantic
```

4. Start the FastAPI server

```bash
uvicorn main:app --reload
```

The backend will run at
[http://127.0.0.1:8000](http://127.0.0.1:8000)

---

### Frontend Setup

1. Navigate to the frontend directory

```bash
cd frontend
```

2. Install dependencies

```bash
npm install
```

3. Create an environment file

```env
REACT_APP_GEMINI_API_KEY=your_api_key_here
```

4. Start the React application

```bash
npm start
```

The frontend will run at
[http://localhost:3000](http://localhost:3000)

---

## Machine Learning Model Details

The backend loads a serialized Scikit Learn model using a custom wrapper class to ensure safe deserialization.

### Input Processing

Raw property data is transformed into a flattened feature dictionary before inference.

Example feature mapping:

```python
{
  "property_type": "SFH" or "Condo",
  "lot_area": calculated_value,
  "bedrooms": int,
  "bathrooms": int,
  "has_pool": boolean
}
```

The predicted price is returned as a numeric value and displayed alongside the listed price in the UI.

---

## How to Test the Application

### Property Comparison

1. Launch the app
2. Select two different properties
3. Click the compare button
4. View predicted price and feature comparison

### AI Assistant

1. Open the chat widget
2. Ask a question related to the selected properties
3. Receive a contextual comparison or explanation

---

## Future Enhancements

* Replace mock data with a relational database
* Add real time property data ingestion
* Integrate map based visualization
* Add user authentication and saved comparisons
* Improve ML model accuracy with real market data

---

## License

This project was developed as a technical case study for Agent Mira.

```
