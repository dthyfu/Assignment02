Assignment 02 – Intelligent System

Repository for the three ML applications and the integrated Chatbot + Neo4j Knowledge Graph.

1. Project Structure

Assignment02/
├── chatbot/
├── DiabeteApp2/
├── Diabetes_notebook/
├── EcommerceApp/
├── Ecommerce_notebook/
├── HousePriceApp2/
└── Housing_notebook/

The three applications contain their notebooks, datasets, trained models, preprocessing files, APIs/web files, and Expo mobile source code.

2. Run the Web Applications

Diabetes

Open a terminal:

cd D:\...\Assignment02\Diabetes_notebook
python diabete2.py

Port: 5010.

House Price

Open a terminal:

cd D:\...\Assignment02\Housing_notebook
python house_price_web.py

Port: 5011.

E-commerce

Open a terminal:

cd D:\...\Assignment02\Ecommerce_notebook
python ecommerce_web.py

Port: 5013.

3. Run the Expo Go Mobile Applications

For each mobile application, open a terminal in its folder.

Diabetes Mobile

cd D:\...\Assignment02\DiabeteApp2
npm install
npx expo start

Scan the QR code with Expo Go.

House Price Mobile

cd D:\...\Assignment02\HousePriceApp2
npm install
npx expo start

Scan the QR code with Expo Go.

E-commerce Mobile

cd D:\...\Assignment02\EcommerceApp
npm install
npx expo start

Scan the QR code with Expo Go.

npm install is normally required for the first setup or after dependencies change. It does not need to be run every time.

4. Run the Chatbot

The chatbot uses Flask, Neo4j Knowledge Graph, and the REST APIs.

Step 1 – Start Neo4j

Open Neo4j Desktop and start the database used by the chatbot.

Neo4j connection:

neo4j://127.0.0.1:7687

Step 2 – Start the required REST APIs

Run each service in a separate terminal.

Diabetes API

cd D:\...\Assignment02\Diabetes_notebook
python diabete2.py

House Price API

cd D:\...\Assignment02\Housing_notebook
python house_price_api.py

E-commerce API

cd D:\...\Assignment02\Ecommerce_notebook
python ecommerce_api.py

Step 3 – Start the Chatbot

Open another terminal:

cd D:\...\Assignment02\chatbot
python app.py

The chatbot runs on port 5016.

Open:

http://127.0.0.1:5016

5. Chatbot Architecture

User
  ↓
Web Chat UI
  ↓
Flask Chatbot Backend
  ↓
Neo4j Knowledge Graph / REST APIs
  ↓
Process Result
  ↓
Chatbot Response
  ↓
Web Chat UI

Neo4j stores information about diabetes symptoms, foods, products, reviews, categories, keywords, and their relationships.

The REST APIs provide ML prediction functions for Diabetes, House Price, and E-commerce.

6. Quick Start for the Complete Chatbot System

Start Neo4j Desktop and the required database.

Start the Diabetes, House Price, and E-commerce APIs in separate terminals.

Start the chatbot:

cd D:\...\Assignment02\chatbot
python app.py

Open:

http://127.0.0.1:5016

For mobile testing, open the corresponding Expo project and run:

npm install
npx expo start

7. Notes

Run services that need to work simultaneously in separate terminals.

Keep the trained model and preprocessing files because the APIs use them for prediction.

The chatbot requires Neo4j and the relevant REST APIs to be running for functions that depend on them.

Replace D:\...\Assignment02 with the actual path of the repository on the computer.