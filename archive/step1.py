import os
import shutil
import subprocess
import json

# Define paths
project_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BibleScholarLangChain'
venv_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean'
log_path = r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\logs\setup.log'

# Create project directory if it doesn't exist
if not os.path.exists(project_path):
    os.makedirs(project_path)
    print(f'Created {project_path} directory')
else:
    print(f'{project_path} directory already exists')

# Create virtual environment if it doesn't exist
if not os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    try:
        subprocess.run(['python', '-m', 'venv', venv_path], check=True)
        print(f'Created {venv_path} virtual environment')
    except Exception as e:
        print(f'Error creating virtual environment: {e}')
else:
    print(f'{venv_path} virtual environment already exists')

# Write requirements.txt
requirements_content = '''
flask==2.3.3
langchain==0.2.16
langchain-community==0.2.16
langchain-postgres==0.0.13
psycopg==3.1.8
flask-caching==2.1.0
requests==2.31.0
python-dotenv==1.0.0
colorama==0.4.6
sqlalchemy==2.0.23
'''
with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
    f.write(requirements_content.strip())
print('Created requirements.txt')

# Install dependencies if virtual environment exists
if os.path.exists(os.path.join(venv_path, 'Scripts', 'pip.exe')):
    try:
        subprocess.run([os.path.join(venv_path, 'Scripts', 'pip.exe'), 'install', '-r', os.path.join(project_path, 'requirements.txt')], check=True)
        print('Installed dependencies')
    except Exception as e:
        print(f'Error installing dependencies: {e}')
else:
    print('Skipping dependency installation: virtual environment not found')

# Configure Cursor interpreter
settings_path = os.path.join(project_path, '.cursor', 'settings.json')
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, 'w') as f:
    json.dump({
        'python.defaultInterpreterPath': r'C:\Users\mccoy\Documents\Projects\Projects\CursorMCPWorkspace\BSPclean\Scripts\python.exe'
    }, f, indent=2)
print('Configured Cursor interpreter')

# Test virtual environment if it exists
if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
    try:
        result = subprocess.run([os.path.join(venv_path, 'Scripts', 'python.exe'), '-c', 
                               "import sys; print(f'Python: {sys.executable}'); "
                               "try: import langchain, psycopg, flask_caching; print(f'Versions: langchain={langchain.__version__}, psycopg={psycopg.__version__}, flask_caching={flask_caching.__version__}') "
                               "except ImportError as e: print(f'Import error: {e}')"], 
                              capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f'Error testing virtual environment: {e}')
else:
    print('Skipping virtual environment test: virtual environment not found')

# Log action via MCP server
try:
    if os.path.exists(os.path.join(venv_path, 'Scripts', 'python.exe')):
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:
        python_exe = 'python'
    
    subprocess.run([python_exe, '-c', 
                   f"import sys; sys.path.append(r'C:\\Users\\mccoy\\Documents\\Projects\\Projects\\CursorMCPWorkspace'); "
                   f"try: from scripts.log_user_interactions import log_action; log_action('Set up BSPclean virtual environment', '{log_path}') "
                   f"except Exception as e: print(f'Logging module error: {{e}}')"], 
                  check=True)
    
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            print('Setup log:', f.read())
    else:
        print('Log file not created yet')
except Exception as e:
    print(f'Warning: MCP logging failed: {e}') 