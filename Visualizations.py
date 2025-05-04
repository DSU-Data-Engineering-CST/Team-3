import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
df = pd.read_csv("movie_data.csv")

# Ensure output directory
os.makedirs("graphs", exist_ok=True)

# 1. Views vs Likes
plt.figure(figsize=(8,6))
sns.scatterplot(x="views", y="likes", hue="is_hit", data=df)
plt.title("Views vs Likes")
plt.savefig("graphs/views_vs_likes.png")

# 2. Views vs Comments
plt.figure(figsize=(8,6))
sns.scatterplot(x="views", y="comments", hue="is_hit", data=df)
plt.title("Views vs Comments")
plt.savefig("graphs/views_vs_comments.png")

# 3. Likes vs Comments
plt.figure(figsize=(8,6))
sns.scatterplot(x="likes", y="comments", hue="is_hit", data=df)
plt.title("Likes vs Comments")
plt.savefig("graphs/likes_vs_comments.png")

# 4. Correlation Heatmap
plt.figure(figsize=(8,6))
sns.heatmap(df[["views", "likes", "comments"]].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Matrix")
plt.savefig("graphs/correlation_matrix.png")

# 5. Histogram of Views
plt.figure(figsize=(8,6))
sns.histplot(df["views"], bins=20, kde=True)
plt.title("Distribution of Views")
plt.savefig("graphs/hist_views.png")

# 6. Histogram of Likes
plt.figure(figsize=(8,6))
sns.histplot(df["likes"], bins=20, kde=True)
plt.title("Distribution of Likes")
plt.savefig("graphs/hist_likes.png")

# 7. Histogram of Comments
plt.figure(figsize=(8,6))
sns.histplot(df["comments"], bins=20, kde=True)
plt.title("Distribution of Comments")
plt.savefig("graphs/hist_comments.png")

# 8. Boxplot - Views by Hit/Flop
plt.figure(figsize=(8,6))
sns.boxplot(x="is_hit", y="views", data=df)
plt.title("Views by Movie Outcome")
plt.savefig("graphs/views_by_hit.png")

# 9. Boxplot - Likes by Hit/Flop
plt.figure(figsize=(8,6))
sns.boxplot(x="is_hit", y="likes", data=df)
plt.title("Likes by Movie Outcome")
plt.savefig("graphs/likes_by_hit.png")

# 10. Boxplot - Comments by Hit/Flop
plt.figure(figsize=(8,6))
sns.boxplot(x="is_hit", y="comments", data=df)
plt.title("Comments by Movie Outcome")
plt.savefig("graphs/comments_by_hit.png")

# 11. Pairplot
sns.pairplot(df[["views", "likes", "comments", "is_hit"]], hue="is_hit")
plt.savefig("graphs/pairplot.png")

# 12. Yearly Trend (if release_date/year exists)
if 'release_date' in df.columns or 'year' in df.columns:
    df['year'] = pd.to_datetime(df['release_date']).dt.year if 'release_date' in df.columns else df['year']
    plt.figure(figsize=(8,6))
    yearly_hit_rate = df.groupby('year')["is_hit"].mean()
    yearly_hit_rate.plot(marker='o')
    plt.title("Yearly Hit Rate Trend")
    plt.ylabel("Hit Ratio")
    plt.savefig("graphs/yearly_hit_rate.png")

print("✅ Graphs saved in /graphs folder.")
