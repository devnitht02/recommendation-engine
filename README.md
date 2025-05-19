# Pathfinder: Personalized Recommendation System

> Empowering students with equitable academic guidance using machine learning & data-driven intelligence

---

![Final Product](https://github.com/devinith02/recommendation-engine/raw/main/static/assets/images/final-product/final-product.png)


## 🔍 Overview

**Pathfinder** is a hybrid academic recommendation engine tailored to assist students in making informed educational decisions. 
It helps bridge the academic guidance gap by offering dynamic, personalized suggestions for degrees and institutions based 
on user preferences, academic profiles, behavioural data and feedback.

Built using Django, MySQL, and Python-based ML frameworks, this full-stack web platform features content-based + collaborative filtering,
adaptive learning, and chatbot integration to provide inclusive guidance.


---

## ⚙️ Installation Guide (Django App, Custom Chatbot, Database)

### 📋 Prerequisites

* **Python 3.8+**
* **Docker Desktop**

  * Enable WSL2 integration

    * Go to: Docker Desktop > Settings > Resources > WSL Integration
    * Check: "Enable integration with my default WSL distro"
    * Enable: `Ubuntu-22.04`
    * Click: `Apply & Restart`
* **Ngrok**

  * Download from [https://ngrok.com/download](https://ngrok.com/download)
  * Sign up & set up authentication token
* **MySQL**

  * Install from [https://dev.mysql.com/](https://dev.mysql.com/)

---

### 🐍 Step 1: Set Up the Python Virtual Environment

```bash
# Clone the repository
$ git clone https://github.com/devnitht02/recommendation-engine.git && cd recommendation-engine

# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
# Windows:
$ venv\Scripts\activate
# macOS/Linux:
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

---

### 🛢️ Step 2: Set Up the MySQL Database

#### 2.1 Install MySQL

* Download and install from [mysql.com](https://www.mysql.com)
* Set up a root user and password

#### 2.2 Create the Database and User

```sql
CREATE DATABASE pathfinder_db;
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON pathfinder_db.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 2.3 Configure Django to Use MySQL

Update `pathfinder/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pathfinder_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Install MySQL client:

```bash
$ pip install mysqlclient
```

#### 2.4 Run Migrations

```bash
$ python manage.py migrate
```

---

### 🔁 Step 3: Set Up the Qdrant Vector Database

Qdrant stores vector embeddings for recommendations & chatbot responses.

#### 3.1 Run Qdrant in Docker

```bash
# Pull Qdrant Docker image
$ docker pull qdrant/qdrant

# Run Qdrant container
$ docker run -d -p 6333:6333 --name qdrant_container qdrant/qdrant
```

Verify container is running via Docker Desktop.

#### 3.2 Populate Vector DB

```bash
# Activate virtual environment
$ source venv/bin/activate  # macOS/Linux
$ venv\Scripts\activate     # Windows

# Update embeddings
$ python vectordb_update_service.py
```

---

### 📡 Step 4: Run the Application with ngrok

```bash
# Start ngrok hosting
$ ngrok http --url=https://glowing-profound-sawfish.ngrok-free.app 8000

# Launch Django development server
$ python manage.py runserver
```

Access the app at:
➡️ [https://glowing-profound-sawfish.ngrok-free.app](https://glowing-profound-sawfish.ngrok-free.app)

---

## 🧾 Data Model (Simplified)

```
📂 Users
├── 📋 StreamChoice
├── 📍 LocationChoice
├── ⭐ Favourites

📚 Courses
├── 📝 Description, Stream, Degree, Fees

🏫 Institutions
├── 📛 Name, Location, Accreditation

🔍 TextEmbeddings
├── 📊 Course & Institution Embeddings
```

---

## 💡 Key Features

* ⚖️ **Hybrid Recommendation Engine**

  * CBF + CF using cosine similarity and SVD

* 💬 **Custom Chatbot**

  * Intelligent responses using LLaMA3 + Groq API + Qdrant

* 🔐 **Secure Authentication**

  * Google OAuth & password login

* 📈 **Live Filtering**

  * Location, fees, stream-wise recommendations

* ✨ **Modern UI/UX**

  * Tailwind CSS + Flowbite components

* 👤 **User Personalization**

  * Recommendations adapt to profile and behavior

* 📦 **Bookmarks & Favorites**

  * Track and save programs

---

## 🚀 Tech Stack

| Layer      | Technology                | Purpose                       |
| ---------- | ------------------------- | ----------------------------- |
| Frontend   | HTML, Tailwind CSS, JS    | UI & Styling                  |
| Backend    | Django (Python)           | Routing, APIs, ML             |
| Database   | MySQL                     | Relational data               |
| Vector DB  | Qdrant                    | Embedding-based similarity    |
| ML Models  | Scikit-learn, Cosine, SVD | Hybrid filtering              |
| Embeddings | SentenceTransformers      | Semantic search               |
| Hosting    | ngrok                     | External URL for local server |
| Versioning | Git + GitHub              | Codebase management           |

---

## 🌟 Project Highlights

* 🔄 **Content-Based Filtering**

  * Ranks based on user preferences using embeddings

* 🔄 **Collaborative Filtering**

  * Uses matrix factorization (SVD) from peer activity

* ⚡ **Hybrid Recommendation Engine**

  * `0.3 * CBF + 0.7 * CF`
  * Fixes the cold-start problem

* 🧠 **Built for Accessibility**

  * Low-bandwidth optimization
  * Inclusive design principles

---

## 🎓 Author

**Devnith Rashmika Tissera**
BSc (Hons) Software Engineering
[University of Plymouth](https://www.plymouth.ac.uk)

> *"Education is neither Eastern nor Western, it is human." — Malala Yousafzai*
