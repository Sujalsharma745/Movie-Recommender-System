# 🎬 Movie Recommender System

A content-based movie recommendation system that suggests movies based on user preferences using TF-IDF vectorization and cosine similarity.

---

## 📌 About the Project

This project recommends movies similar to a selected movie by analyzing movie metadata such as genres, cast, crew, and keywords. It uses **content-based filtering** to find the closest matches based on textual similarity.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Libraries:** Pandas, NumPy, Scikit-learn
- **UI:** Streamlit
- **Algorithm:** TF-IDF Vectorization + Cosine Similarity

---

## ⚙️ How It Works

1. Movie metadata (genres, cast, keywords, overview) is combined into a single text feature
2. TF-IDF Vectorizer converts text into numerical vectors
3. Cosine Similarity measures how close two movies are to each other
4. Top N similar movies are returned as recommendations

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install pandas numpy scikit-learn streamlit
```

### Run the App
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
movie-recommender/
│
├── app.py                  # Streamlit UI
├── recommender.py          # Core recommendation logic
├── data/
│   └── movies.csv          # Dataset
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

Uses the [TMDB Movies Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) from Kaggle containing movie titles, genres, cast, crew, and keywords.

---

## 🙋‍♂️ Author

**Sujal Sharma**
- GitHub: [@Sujalsharma745](https://github.com/Sujalsharma745)
- LinkedIn: [sujal-sharma](https://www.linkedin.com/in/sujalsharma2345)
