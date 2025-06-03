import subprocess
import sys

result = subprocess.run([sys.executable, '-m', 'pytest', 'BibleScholarProjectv2/tests/test_study_dashboard_ui.py'], capture_output=True, text=True) 