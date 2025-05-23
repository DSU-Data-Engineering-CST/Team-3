# 🎬 Movie Hit or Flop Prediction ETL Pipeline

A Python-based ETL (Extract, Transform, Load) pipeline designed to collect, process, and analyze movie data to predict whether a movie will be a hit or a flop. The pipeline integrates data from various sources, performs necessary transformations, stores the data in both CSV files and a MySQL database, and utilizes machine learning models for prediction.

---

## 📌 Table of Contents

* [Features](#-features)
* [Technology Stack](#-technology-stack)
* [Setup Instructions](#-setup-instructions)
* [Data Pipeline Architecture](#-=data-pipeline-architecture)
* [Data Sources](#-data-sources)
* [Machine Learning Model](#-machine-learning-model)
* [Visualizations](#-visualizations)
* [Future Enhancements](#-future-enhancements)
  
---

## ✅ Features

* **Data Extraction**: Collects movie metadata, user ratings, and other relevant information from APIs and datasets.
* **Data Transformation**: Cleans and processes the data, handling missing values, encoding categorical variables, and engineering new features.
* **Data Loading**: Stores the transformed data into CSV files and a MySQL database for persistent storage.
* **Prediction Model**: Implements machine learning models to predict the success of a movie.
* **Visualization**: Generates insightful graphs to understand data distributions and model performance.
* **Automation**: Utilizes threading to run extraction scripts concurrently, improving efficiency.

---

## 🛠️ Technology Stack

* **Programming Language**: Python
* **Data Processing**: Pandas, NumPy
* **Database**: MySQL
* **APIs**: Youtube API
* **Machine Learning**: scikit-learn
* **Visualization**: Matplotlib, Seaborn
* **Environment Management**: dotenv
* **Concurrency**: threading
* **Version Control**: Git

---

## ⚙️ Setup Instructions

### Prerequisites

* Python 3.x installed
* MySQL server installed and running
* Youtube API key

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/movie-hit-flop-prediction.git
   cd movie-hit-flop-prediction
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory and add your TMDb API key and MySQL credentials:

   ```
   Youtube_API_KEY=your_Youtube_api_key
   DB_HOST=localhost
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_NAME=movie_db
   ```

5. **Initialize the Database**

   * Create a new database named `movie_db` in MySQL.
   * Run the provided SQL scripts to create necessary tables.

6. **Run the ETL Pipeline**

   ```bash
   python main.py
   ```

---

## 🗂️ Data Pipeline Architecture

The ETL pipeline consists of the following components:

1. **Extraction**: Scripts (`extractViews.py`, `extractLikes.py`, `extractComments.py`) fetch data from TMDb API and IMDb datasets.
2. **Transformation**: The `transform.py` script processes the raw data, handling missing values, encoding categorical variables, and engineering features like ROI.
3. **Loading**: The `load.py` script saves the transformed data into CSV files and inserts records into the MySQL database.
4. **Prediction**: The `predict.py` script trains machine learning models to predict movie success.
5. **Visualization**: The `visualize.py` script generates graphs to analyze data distributions and model performance.

The `main.py` script orchestrates the entire pipeline, utilizing threading to run extraction scripts concurrently.

---

## 📚 Data Sources

* **Youtube API**: Provides movie metadata, including titles, genres, release dates, budgets, revenues, and user ratings.

---

## 🤖 Machine Learning Model

The prediction component utilizes machine learning models to classify movies as hits or flops based on various features.

### Features Used

* Budget
* Revenue
* Popularity
* Vote Count
* Vote Average
* Runtime
* ROI (Return on Investment)
* Genre (encoded)

### Models Implemented

* Logistic Regression
* Decision Tree Classifier
* Random Forest Classifier

### Evaluation Metrics

* Accuracy
* Precision
* Recall
* F1-Score
* ROC-AUC Score

---

## 📊 Visualizations

The project includes a comprehensive set of graphs to analyze data distributions and model performance:

### 1. Budget vs. Revenue
![Budget vs Revenue](budget_vs_revenue.png)

### 2. Genre Distribution
![Genre Distribution](genre_vs_hit_count.png)

### 3. Popularity vs. Vote Count
![Popularity vs Vote Count](popularity_vs_votes.png)

### 4. ROI Distribution
![ROI Distribution](roi_distribution.png)

### 5. Vote Average Histogram
![Vote Average Histogram](vote_avg_histogram.png)

### 6. Runtime vs Success
![Runtime vs Success](runtime_vs_hit.png)

### 7. Yearly Success Trend
![Yearly Success Trend](yearly_hit_trend.png)

### 8. Correlation Heatmap
![Correlation Heatmap](correlation_heatmap.png)

### 9. Vote Average vs Revenue
![Vote Average vs Revenue](vote_avg_vs_revenue.png)

### 10. Budget Band vs Hit Rate
![Budget Band vs Hit Rate](budget_band_hit_rate.png)


---


## 🚀 Future Enhancements

* **Real-time Data Integration**: Incorporate real-time data fetching for up-to-date predictions.
* **Web Interface**: Develop a user-friendly web application using Flask or Django.
* **Advanced Modeling**: Explore deep learning models for improved prediction accuracy.
* **Additional Data Sources**: Integrate data from social media platforms for sentiment analysis.
* **Automated Reporting**: Generate automated reports summarizing insights and predictions.



