
# Pathfinder: Personalized Recommendation System




> Empowering students with equitable academic guidance using machine learning & data-driven intelligence

---

## 🔍 Overview
Pathfinder is a hybrid academic recommendation engine tailored to assist students in making informed educational decisions. 
It helps bridge the academic guidance gap by offering dynamic, personalized suggestions for degrees and institutions based 
on user preferences, academic profiles, and behavioural data.

Built using Django, MySQL, and Python-based ML frameworks, this full-stack web platform features content-based + collaborative filtering,
adaptive learning, and chatbot integration to provide inclusive guidance.



---

## ⚙️ Installation Guide (Django App, Chatbot, Database)

### 🔧 Django Web App Setup
```bash
# Clone the repo
$ git clone https://github.com/username/pathfinder.git && cd pathfinder

# Create virtual environment
$ python -m venv venv && source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

### 🧠 Chatbot & ML Models
```bash
# Ensure transformers and sentence-transformers are installed
$ pip install transformers sentence-transformers

# (Optional) Download model assets if used offline
# $ python manage.py download_embeddings
```

### 🛢️ MySQL Database Setup
```bash
# Create MySQL database (e.g., pathfinder_db) and user
# Update settings.py with DB credentials

# Run initial migrations
$ python manage.py migrate

# Load sample or real dataset
$ python manage.py loaddata initial_data.json
```

### ▶️ Run the Application
```bash
# Launch local development server
$ python manage.py runserver
```

Then navigate to: [http://localhost:8000](http://localhost:8000)

---

## 🧾 Data Model (Simplified)

```txt
Users
├── StreamChoice
├── LocationChoice
├── Favourites
Courses
├── Description, Stream, Degree, Fees
Institutions
├── Name, Location, Accreditation
TextEmbeddings
├── Course & Institution Embeddings
```

---

## 💡 Key Features

- ⚖️ **Hybrid Recommendation Engine**
  - Combines Content-Based Filtering (CBF) and Collaborative Filtering (CF) using cosine similarity and SVD
- 💬 **Interactive Chatbot**
  - Real-time responses to student queries about academic paths
- 🔐 **Secure Authentication**
  - Google OAuth and password-based login
- 📈 **Dynamic Search & Filtering**
  - Real-time results based on location, fees, and stream preferences
- ✨ **Modern UI/UX**
  - Fully responsive Tailwind CSS interface with Flowbite components
- 👤 **Profile-Driven Personalization**
  - Each recommendation is aligned with user data and evolving preferences
- 📦 **Favorite & Bookmark System**
  - Track and compare academic programs

---

## 🚀 Tech Stack

| Layer        | Technology                 | Purpose                                     |
|--------------|----------------------------|---------------------------------------------|
| Frontend     | HTML, Tailwind CSS, JS     | UI components and styling                   |
| Backend      | Django (Python)            | Routing, logic, API, ML integration         |
| Database     | MySQL                      | Storage of courses, institutions, users     |
| ML Models    | Scikit-learn, SVD, Cosine  | Hybrid Recommendation Logic                |
| Embedding    | SentenceTransformers       | Semantic similarity on user input/query     |
| Versioning   | Git + GitHub               | Source code management                      |

---

## 🌟 Project Highlights

### 🔄 Content-Based Filtering
- Learns from user's stream and location
- Ranks by text similarity using vector embeddings

### 🔄 Collaborative Filtering
- Matrix factorization using SVD
- Leverages peer behavior for suggestions

### ⚡ Hybrid Integration
- Weighted score: `0.3 * cbf_score + 0.7 * cf_score`
- Solves the cold-start problem for new users

### 🧠 Inclusivity First
- Designed for students in low-bandwidth rural areas
- Accessible UI and optimized database queries



## 🎓 Author
**Devnith Rashmika Tissera**  
BSc (Hons) Software Engineering  
[University of Plymouth](https://www.plymouth.ac.uk)  


> _"Education is neither Eastern nor Western, it is human." — Malala Yousafzai_

---


