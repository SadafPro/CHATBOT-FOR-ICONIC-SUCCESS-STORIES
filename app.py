import nltk
from flask import Flask, render_template, jsonify, request
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.chat.util import Chat, reflections
import random

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

app = Flask(__name__)

# Neural Network Model
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(NeuralNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

# Load data from JSON file
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Preprocess text
def preprocess_text(text):
    tokens = nltk.word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    return lemmatized_tokens

# Initialize model and training parameters
def initialize_model(data):
    word_to_idx = {}
    all_words = []

    for item in data.get("FAQ", []):
        question = item.get("question")
        if question:
            processed_tokens = preprocess_text(question)
            all_words.extend(processed_tokens)

    all_words = sorted(set(all_words))
    for i, word in enumerate(all_words):
        word_to_idx[word] = i

    input_size = len(word_to_idx)
    hidden_size = 64
    output_size = 2

    model = NeuralNet(input_size, hidden_size, output_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.0001)

    return model, criterion, optimizer, word_to_idx

# Create bag of words
def bag_of_words(tokenized_sentence, word_to_idx):
    bag = np.zeros(len(word_to_idx), dtype=np.float32)
    for word in tokenized_sentence:
        if word in word_to_idx:
            bag[word_to_idx[word]] = 1
    return bag

# Load FAQ data
file_path = "faq_data1.json"
faq_data = load_data(file_path)
model, criterion, optimizer, word_to_idx = initialize_model(faq_data)

# Define conversation patterns
pairs = [
    [r"hi|hello|hey", ["Hello! Nice to meet you"]],
    [r"what's your name|what is your name", ["I'm ChatSHAH. What's your name?"]],
    [r"my name is (.*)|iam (.*)" , ["Nice to meet you, %1. How can I assist you today?"]],
    [r"how are you|how are you doing", ["I'm doing well, thank you for asking!", "Feeling good today, thanks for asking!"]],
    [r"what can you do|what are your capabilities|what do you do", ["I can provide information, answer questions, tell stories, and more!", "I can assist you with telling various stories."]],
    [r"thank you|thanks", ["You're welcome!", "No problem, happy to help!"]],
    [r"bye|goodbye", ["Goodbye! Take care.", "See you later!"]],
    [r"(.*)", ["I'm sorry, I didn't understand that. Can you please rephrase it?"]],
    [ r"how old are you|what's your age",[ "Age is just a number for me!"]],
    [r"where are you from|where do you live",[ "I'm everywhere and nowhere at the same time."]],
    [r"do you have any hobbies|what do you like to do",["I love learning new things and chatting with people!", "My hobby is assisting you and making your day better."]], 
    [r"tell me about yourself",["I'm an AI chatbot designed to assist you with tellin various stories and engage in conversations.", "I'm your friendly virtual assistant here to help you with anything you need!"]],
    [r"can you help me|assist me",["Of course! I'm here to assist you with whatever you need.", "Absolutely! Just let me know what you need help with."]],
    [r"tell me a story|narrate a story",["I have many different stories and help you to motivate and inspire"]],
    [r"do you recommend any",["Absolutely, I have many stories , I recommend story of Srikanth Bolla -  visually impaired, Malala, Yuvaraj singh ,these stories will actually inspire you"]],
    [r"(.*)",["I'm sorry, I didn't understand that. Can you please rephrase it?",]]
]

# Create chatbot instance
chatbot = Chat(pairs, reflections)

@app.route('/')
def home():
    return render_template('introduction.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/database')
def database():
    return render_template('database.html')

@app.route('/submitted')
def submitted():
    return render_template('submitted.html')

@app.route('/page1.html')
def page1():
    return render_template('page1.html')

@app.route('/page2.html')
def page2():
    return render_template('page2.html')

@app.route('/page3.html')
def page3():
    return render_template('page3.html')



@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    if user_input.lower() in ['quit', 'exit']:
        return jsonify({'response': "Goodbye!"})
    elif user_input.strip() == '':
        return jsonify({'response': "Please enter something."})
    else:
        answer = get_answer(user_input, faq_data)
        return jsonify(answer)

def get_answer(question, data):
    processed_question = preprocess_text(question)
    bow = bag_of_words(processed_question, word_to_idx)
    input_tensor = torch.from_numpy(bow)
    input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension
    output = model(input_tensor)
    _, predicted = torch.max(output, dim=1)
    label = predicted.item()

    # Check if there is a matching FAQ
    for item in data["FAQ"]:
        faq_tokens = preprocess_text(item["question"])
        if processed_question == faq_tokens:
            answer = []
            for subtopic, paragraphs in item["answer"].items():
                answer.append({
                    "subtopic": subtopic,
                    "paragraphs": paragraphs
                })
            return {"response": answer}
    
    # If no direct match is found, use the chatbot
    bot_response = chatbot.respond(question)
    return {"response": bot_response}

if __name__ == "__main__":
    app.run(debug=True)
