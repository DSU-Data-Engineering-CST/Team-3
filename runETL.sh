#!/bin/bash
echo "🚀 Starting ETL Pipeline..."

# Step 1: Extract
python run_all_extractors.py

# Step 2: Transform
python transform.py

# Step 3: Load
python load.py

# Step 4: Main Orchestration
python main.py

echo "🎯 ETL Pipeline Completed Successfully!"
