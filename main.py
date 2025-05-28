from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import joblib
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk

nltk.download('stopwords')

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load model and frequency dictionary
model = joblib.load("sentiment_model.pkl")
freqs = joblib.load("freqs.pkl")

# Preprocessing utilities
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess(text):
    text = re.sub(r"http\S+|@\S+|#\S+|[^a-zA-Z\s]", '', text)
    text = text.lower()
    tokens = text.split()
    tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return tokens

def extract_features(tokens):
    pos_freq = sum([freqs[word][1] for word in tokens])
    neg_freq = sum([freqs[word][0] for word in tokens])
    return [1, pos_freq, neg_freq]

# ✅ Serve the HTML form
@app.get("/", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Handle form submission
@app.post("/predict")
def predict(tweet: str = Form(...)):
    tokens = preprocess(tweet)
    features = extract_features(tokens)
    prediction = model.predict([features])[0]
    sentiment = "Positive 😊" if prediction == 1 else "Negative 😞"
    return {"sentiment": sentiment}
