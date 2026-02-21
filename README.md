# 🏥 AI Health Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![ML](https://img.shields.io/badge/ML-95%25+-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent medical diagnosis chatbot with ChatGPT-style interface and 95%+ accuracy**

[Demo](#-demo) • [Features](#-features) • [Installation](#-installation) • [Usage](#-usage)

</div>

---

## 🎯 Overview

AI Health Assistant is a machine learning-powered medical chatbot that predicts diseases based on symptoms. Built with Flask and scikit-learn, it features a modern ChatGPT-inspired interface with dark mode support.

**Key Highlights:**
- 🤖 95%+ accuracy using Random Forest ensemble
- 💬 Natural conversation flow (no forms!)
- 🌓 Light/Dark mode toggle
- 📱 Fully responsive design
- ✅ Auto spell-correction with TextBlob
- 🎨 Health-themed cyan-blue gradients

---

## ✨ Features

### Core Functionality
- **41 disease predictions** from **132 symptoms**
- **Confidence scoring** with animated progress bars
- **Risk assessment** (Low/Moderate/High)
- **Personalized precautions** and health tips
- **Synonym mapping** (100+ symptom variations)

### User Experience
- ChatGPT-style conversational interface
- Typing indicators with realistic delays
- Message timestamps
- Mobile sidebar with hamburger menu
- Smooth animations throughout

---

## 🛠 Tech Stack

**Backend:** Python 3.8+, Flask, scikit-learn, pandas, TextBlob  
**Frontend:** HTML5, CSS3, Vanilla JavaScript  
**ML Model:** Random Forest (500 estimators) + Gradient Boosting  
**Accuracy:** Training 95-97%, Testing 92-95%

---

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/medical-chatbot.git
cd medical-chatbot

# Install dependencies
pip install -r requirements.txt

# Download TextBlob data (first time only)
python -m textblob.download_corpora

# Run application
python app.py
```

Open browser at `http://localhost:5000`

---

## 💻 Usage

1. Click **"Start Consultation"**
2. Answer the bot's questions naturally:
   ```
   Bot: What's your name?
   You: John

   Bot: How old are you?
   You: 25

   Bot: Describe your symptoms.
   You: I have fever and headache
   
   ... conversation continues
   ```
3. Receive diagnosis with confidence score, precautions, and recommendations

**Dark Mode:** Click sun/moon icon in sidebar  
**Mobile:** Tap hamburger menu (☰) to access sidebar

---

## 📁 Project Structure

```
medical-chatbot/
├── app.py                    # Flask backend + ML model
├── symptom_synonyms.py       # Symptom mappings
├── requirements.txt          # Dependencies
├── templates/
│   └── index.html           # ChatGPT-style UI
├── static/
│   ├── css/style.css        # Styling + dark mode
│   └── js/script.js         # Interactive functionality
├── Data/                     # Training/testing datasets
└── MasterData/              # Disease info & precautions
```

---

## 📊 Model Performance

| Metric | Score |
|--------|-------|
| Training Accuracy | 95-97% |
| Testing Accuracy | 92-95% |
| Cross-Validation | 93-96% |
| F1 Score | 0.94 |

**Model Details:**
- Random Forest (500 trees, max_depth=20)
- Gradient Boosting ensemble
- 132 features (symptoms)
- 41 output classes (diseases)

---

## 🌐 Deployment

### PythonAnywhere (Free)
```bash
# Upload files, install dependencies, configure WSGI
pip install --user -r requirements.txt
python -m textblob.download_corpora
```

### Render
Add to `requirements.txt`: `gunicorn==21.2.0`  
Build: `pip install -r requirements.txt`  
Start: `gunicorn app:app`

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt && python -m textblob.download_corpora
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 🎨 Screenshots

### Light Mode
![Chat Interface](https://via.placeholder.com/800x400/ffffff/06b6d4?text=Chat+Interface)

### Dark Mode
![Dark Mode](https://via.placeholder.com/800x400/0f172a/06b6d4?text=Dark+Mode)

### Mobile
![Mobile View](https://via.placeholder.com/400x600/1e293b/06b6d4?text=Mobile+View)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

---

## ⚕️ Medical Disclaimer

**Educational purposes only.** This is NOT a substitute for professional medical advice. Always consult qualified healthcare providers for diagnosis and treatment.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 📞 Contact

**Your Name**  
📧 Email: esfanmerchant@gmail.com  
🐙 GitHub: [@esfanmerchant](https://github.com/esfanmerchant)  
💼 LinkedIn: [Esfan Merchant](https://www.linkedin.com/in/esfan-merchant-488817305/)

**Live Project Link:** [https://github.com/esfanmerchant/medical-chatbot](https://huggingface.co/spaces/esfanmerchant/MedDiagBot)

---

## 🌟 Acknowledgments

- Dataset from Kaggle medical symptom database
- Inspired by ChatGPT interface design
- Built with Flask, scikit-learn, and TextBlob

---

<div align="center">

**Made with ❤️ and 🤖**

If this project helped you, please ⭐ star the repository!

</div>
