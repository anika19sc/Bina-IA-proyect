import PyInstaller.__main__
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
start_script = os.path.join(backend_dir, "start.py")

PyInstaller.__main__.run([
    start_script,
    '--name=backend',
    '--onefile',
    #'--windowed', # Uncomment to hide console window
    '--add-data=app;app', # Include the app package
    # '--add-data=.env;.', # Include .env if needed, though usually better to load from user home or relative path
    '--clean',
    '--distpath=dist',
])
