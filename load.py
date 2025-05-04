import pandas as pd

def load_data():
    views_df = pd.read_csv('views_data.csv')
    likes_df = pd.read_csv('likes_data.csv')
    comments_df = pd.read_csv('comments_data.csv')

    # Merge based on movie_id
    combined_df = views_df.merge(likes_df, on='movie_id').merge(comments_df, on='movie_id')

    return combined_df
