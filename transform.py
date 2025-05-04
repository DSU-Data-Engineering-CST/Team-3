def transform_data(df):
    def label_movie(row):
        if row['views'] > 1000000 and row['likes'] > 50000 and row['comments'] > 5000:
            return 'Hit'
        else:
            return 'Flop'

    df['label'] = df.apply(label_movie, axis=1)
    return df
