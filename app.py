from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import csv
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from difflib import get_close_matches
import re
import random
import warnings
from symptoms_synonyms import SYMPTOM_SYNONYMS
from textblob import TextBlob
import pickle
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'



training = pd.read_csv('Data/Training.csv')
testing = pd.read_csv('Data/Testing.csv')
training.head()
training.columns = training.columns.str.replace(r"\.\d+$", "", regex=True)
testing.columns = testing.columns.str.replace(r"\.\d+$", "", regex=True)
training = training.loc[:, ~training.columns.duplicated()]
testing = testing.loc[:, ~testing.columns.duplicated()]
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']
le = preprocessing.LabelEncoder()
y = le.fit_transform(y)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42, stratify=y)
model = RandomForestClassifier(
    n_estimators=500,
    max_depth=20,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features='sqrt',
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(x_train, y_train)



with open("model.pkl","rb") as model_file:
    model = pickle.load(model_file)

# Load dictionaries
severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {symptom: idx for idx, symptom in enumerate(x)}

def load_data():
    with open('MasterData/symptom_Description.csv') as csv_file:
        for row in csv.reader(csv_file):
            description_list[row[0]] = row[1]
    
    with open('MasterData/symptom_severity.csv') as csv_file:
        for row in csv.reader(csv_file):
            try:
                severityDictionary[row[0]] = int(row[1])
            except:
                pass
    
    with open('MasterData/symptom_precaution.csv') as csv_file:
        for row in csv.reader(csv_file):
            precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]

load_data()

# helper functions
def correct_spelling(text):
    """Correct spelling in user input using TextBlob"""
    try:
        blob = TextBlob(text)
        corrected = str(blob.correct())
        return corrected
    except:
        return text

def extract_symptoms(user_input, all_symptoms):
    corrected_input = correct_spelling(user_input)
    
    extracted = []
    text = corrected_input.lower().replace("-", " ")

    for phrase, mapped in SYMPTOM_SYNONYMS.items():
        if phrase in text:
            extracted.append(mapped)

    for symptom in all_symptoms:
        if symptom.replace("_", " ") in text:
            extracted.append(symptom)

    words = re.findall(r"\w+", text)
    for word in words:
        close = get_close_matches(word, [s.replace("_", " ") for s in all_symptoms], n=1, cutoff=0.75)
        if close:
            for sym in all_symptoms:
                if sym.replace("_", " ") == close[0]:
                    extracted.append(sym)

    return list(set(extracted))

def predict_disease(symptoms_list):
    input_vector = np.zeros(len(symptoms_dict))
    for symptom in symptoms_list:
        if symptom in symptoms_dict:
            input_vector[symptoms_dict[symptom]] = 1

    pred_proba = model.predict_proba([input_vector])[0]
    pred_class = np.argmax(pred_proba)
    disease = le.inverse_transform([pred_class])[0]
    confidence = round(pred_proba[pred_class] * 100, 2)
    return disease, confidence

def get_disease_symptoms(disease):
    if disease in training['prognosis'].values:
        disease_symptoms = list(training[training['prognosis'] == disease].iloc[0][:-1].index[
            training[training['prognosis'] == disease].iloc[0][:-1] == 1
        ])
        return disease_symptoms
    return []

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init_chat():
    session.clear()
    session['step'] = 'ask_name'
    return jsonify({
        'success': True,
        'message': "Hello! I'm your AI Health Assistant. 👋 What's your name?"
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'success': False, 'message': 'Please type a message.'})
    
    step = session.get('step', 'ask_name')
    
    #getname
    if step == 'ask_name':
        session['name'] = user_message
        session['step'] = 'ask_age'
        return jsonify({
            'success': True,
            'message': f"Nice to meet you, {user_message}! 😊 How old are you?"
        })
    
    #getage
    elif step == 'ask_age':
        session['age'] = user_message
        session['step'] = 'ask_gender'
        return jsonify({
            'success': True,
            'message': "What's your gender? (Male/Female/Other)"
        })
    
    #getgender
    elif step == 'ask_gender':
        session['gender'] = user_message
        session['step'] = 'initial_symptoms'
        session['symptoms_list'] = []
        return jsonify({
            'success': True,
            'message': "Thank you! Now, please describe your symptoms. For example: 'I have fever and headache' or 'stomach pain and nausea'"
        })
    
    #get initial symptoms
    elif step == 'initial_symptoms':
        symptoms_list = extract_symptoms(user_message, cols)
        
        if not symptoms_list:
            return jsonify({
                'success': True,
                'message': "I couldn't detect any specific symptoms from that. Could you try describing your symptoms more clearly?\n\nFor example: 'fever and cough' or 'stomach pain and nausea'"
            })
        
        session['symptoms_list'] = symptoms_list
        session['step'] = 'duration'
        
        detected_symptoms = ', '.join([s.replace('_', ' ') for s in symptoms_list])
        return jsonify({
            'success': True,
            'message': f"✅ Detected symptoms: {detected_symptoms}\n\nFor how many days have you been experiencing these symptoms?"
        })
    
    #duration
    elif step == 'duration':
        try:
            days = int(user_message.split()[0])
            session['days'] = days
            session['step'] = 'severity'
            return jsonify({
                'success': True,
                'message': f"Got it, {days} day(s). On a scale of 1 to 10, how severe are your symptoms? (1 = mild, 10 = very severe)"
            })
        except:
            return jsonify({
                'success': True,
                'message': "Please enter the number of days (e.g., '3' or '3 days')"
            })
    
    #severity
    elif step == 'severity':
        try:
            severity = int(user_message.split()[0])
            if severity < 1 or severity > 10:
                return jsonify({
                    'success': True,
                    'message': "Please rate between 1 and 10"
                })
            session['severity'] = severity
            session['step'] = 'pre_existing'
            return jsonify({
                'success': True,
                'message': "Do you have any pre-existing medical conditions? (e.g., diabetes, hypertension, asthma, or just say 'none')"
            })
        except:
            return jsonify({
                'success': True,
                'message': "Please enter a number between 1 and 10"
            })
    
    #Preexisting
    elif step == 'pre_existing':
        session['pre_existing'] = user_message
        session['step'] = 'lifestyle'
        return jsonify({
            'success': True,
            'message': "Do you smoke, drink alcohol, or have irregular sleep patterns?"
        })
    
    #lifestyle
    elif step == 'lifestyle':
        session['lifestyle'] = user_message
        session['step'] = 'family_history'
        return jsonify({
            'success': True,
            'message': "Is there any family history of similar illnesses?"
        })
    
    #family history
    elif step == 'family_history':
        session['family_history'] = user_message
        
        #Initial prediction
        symptoms_list = session['symptoms_list']
        disease, confidence = predict_disease(symptoms_list)
        
        session['current_disease'] = disease
        session['question_index'] = 0
        
        #Get disease symptoms
        disease_symptoms = get_disease_symptoms(disease)
        remaining_symptoms = [s for s in disease_symptoms if s not in symptoms_list]
        session['disease_symptoms'] = remaining_symptoms[:8]
        
        if session['disease_symptoms']:
            session['step'] = 'follow_up'
            first_symptom = session['disease_symptoms'][0].replace('_', ' ')
            return jsonify({
                'success': True,
                'message': f"Thanks! Let me ask a few more specific questions to help with the diagnosis. Do you have {first_symptom}? (yes/no)"
            })
        else:
            return get_final_result()
    
    #followup questions
    elif step == 'follow_up':
        answer = user_message.lower().strip()
        symptoms_list = session['symptoms_list']
        question_index = session['question_index']
        disease_symptoms = session['disease_symptoms']
        
        if answer in ['yes', 'yeah', 'yep', 'y']:
            symptoms_list.append(disease_symptoms[question_index])
            session['symptoms_list'] = symptoms_list
        
        question_index += 1
        session['question_index'] = question_index
        
        if question_index < len(disease_symptoms):
            next_symptom = disease_symptoms[question_index].replace('_', ' ')
            return jsonify({
                'success': True,
                'message': f"Do you have {next_symptom}?\n(yes/no)"
            })
        else:
            return get_final_result()
    
    return jsonify({'success': False, 'message': 'Something went wrong.'})

def get_final_result():
    symptoms_list = session['symptoms_list']
    disease, confidence = predict_disease(symptoms_list)
    
    description = description_list.get(disease, 'No description available.')
    precautions = precautionDictionary.get(disease, [])
    
    days = session.get('days', 0)
    severity = session.get('severity', 0)
    
    if days > 7 or severity > 7:
        risk_level = "HIGH"
        risk_message = "⚠️ Your symptoms appear to be severe. Please consult a doctor immediately!"
        risk_class = "high"
    elif days > 3 or severity > 5:
        risk_level = "MODERATE"
        risk_message = "⚠️ Your symptoms are concerning. Consider seeing a healthcare professional soon."
        risk_class = "moderate"
    else:
        risk_level = "LOW"
        risk_message = "ℹ️ Your symptoms appear mild. Monitor them and seek help if they worsen."
        risk_class = "low"
    
    quotes = [
        "🌸 Health is wealth, take care of yourself.",
        "💪 A healthy outside starts from the inside.",
        "☀️ Every day is a chance to get stronger and healthier.",
        "🌿 Take a deep breath, your health matters the most.",
        "🌺 Remember, self-care is not selfish."
    ]
    
    result = {
        'success': True,
        'is_result': True,
        'disease': disease,
        'confidence': confidence,
        'description': description,
        'precautions': [p for p in precautions if p.strip()],
        'risk_level': risk_level,
        'risk_message': risk_message,
        'risk_class': risk_class,
        'quote': random.choice(quotes),
        'name': session.get('name', 'User')
    }
    
    session.clear()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)