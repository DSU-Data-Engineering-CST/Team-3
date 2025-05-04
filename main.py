from load import load_data
from transform import transform_data
import subprocess

def main():
    print("🚀 Starting Full ETL Pipeline...")

    # Step 1: Extract
    subprocess.run(["python", "run_all_extractors.py"])

    # Step 2: Load
    data = load_data()
    print("✅ Data Loaded Successfully.")

    # Step 3: Transform
    final_data = transform_data(data)
    print("✅ Data Transformed Successfully.")

    # Step 4: Save Output
    final_data.to_csv('final_movie_predictions.csv', index=False)
    print("🎯 Final predictions saved to final_movie_predictions.csv!")

if __name__ == "__main__":
    main()
