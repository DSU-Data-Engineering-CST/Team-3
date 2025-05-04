import threading
import subprocess
from datetime import datetime

def run_script(script_name):
    print(f"\n🕐 {script_name} started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", script_name])
    print(f"✅ {script_name} finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Create threads
t1 = threading.Thread(target=run_script, args=("extractViews.py",))
t2 = threading.Thread(target=run_script, args=("extractLikes.py",))
t3 = threading.Thread(target=run_script, args=("extractComments.py",))

# Start threads
print("🚀 Running all extractors in parallel...\n")
t1.start()
t2.start()
t3.start()

# Wait for all to complete
t1.join()
t2.join()
t3.join()

print("🎯 All extractors completed!")
