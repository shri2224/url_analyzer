import os
import sys
import shutil
import zipfile
import json
import datetime

SNAPSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'snapshots')
HISTORY_FILE = os.path.join(SNAPSHOTS_DIR, 'history.json')

EXCLUDES = {
    'node_modules', 'venv', '__pycache__', '.git', '.vscode', '.idea', 'dist', 'build', 'snapshots', '.DS_Store'
}

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def should_exclude(path, names):
    return [n for n in names if n in EXCLUDES]

def zip_directory(path, ziph):
    for root, dirs, files in os.walk(path):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDES]
        
        for file in files:
            if file in EXCLUDES:
                continue
            
            file_path = os.path.join(root, file)
            # Calculate relative path for the zip archive
            rel_path = os.path.relpath(file_path, os.path.join(path, '..'))
            ziph.write(file_path, rel_path)

def save_snapshot(tag):
    if not os.path.exists(SNAPSHOTS_DIR):
        os.makedirs(SNAPSHOTS_DIR)

    filename = f"{tag}.zip"
    filepath = os.path.join(SNAPSHOTS_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"Snapshot '{tag}' already exists. Overwriting...")

    print(f"Creating snapshot '{tag}' at {filepath}...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Save backend
        backend_dir = os.path.join(base_dir, 'backend')
        if os.path.exists(backend_dir):
            print("  Backing up backend...")
            zip_directory(backend_dir, zipf)
            
        # Save frontend
        frontend_dir = os.path.join(base_dir, 'frontend')
        if os.path.exists(frontend_dir):
            print("  Backing up frontend...")
            zip_directory(frontend_dir, zipf)

        # Save specific root files if needed (optional)
        # for item in os.listdir(base_dir):
        #     if os.path.isfile(os.path.join(base_dir, item)) and item not in EXCLUDES:
        #          zipf.write(os.path.join(base_dir, item), item)

    # Update history
    history = load_history()
    entry = {
        'tag': tag,
        'filename': filename,
        'timestamp': datetime.datetime.now().isoformat(),
        'path': filepath
    }
    # Remove old entry with same tag if exists
    history = [h for h in history if h['tag'] != tag]
    history.append(entry)
    save_history(history)
    
    print(f"✅ Snapshot '{tag}' saved successfully!")

def restore_snapshot(tag):
    filename = f"{tag}.zip"
    filepath = os.path.join(SNAPSHOTS_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Snapshot '{tag}' not found.")
        return

    print(f"Restoring snapshot '{tag}' from {filepath}...")
    print("Warning: This will overwrite existing files in backend/ and frontend/.")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    with zipfile.ZipFile(filepath, 'r') as zipf:
        zipf.extractall(base_dir)
        
    print(f"✅ Snapshot '{tag}' restored successfully!")

def list_snapshots():
    history = load_history()
    if not history:
        print("No snapshots found.")
        return
    
    print(f"{'TAG':<20} {'TIMESTAMP':<30} {'FILENAME'}")
    print("-" * 70)
    for h in history:
        print(f"{h['tag']:<20} {h['timestamp']:<30} {h['filename']}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_snapshots.py [save <tag> | restore <tag> | list]")
        return

    command = sys.argv[1]
    
    if command == 'save':
        if len(sys.argv) < 3:
            print("Usage: python manage_snapshots.py save <tag>")
            return
        save_snapshot(sys.argv[2])
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Usage: python manage_snapshots.py restore <tag>")
            return
        restore_snapshot(sys.argv[2])
    elif command == 'list':
        list_snapshots()
    else:
        print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()
