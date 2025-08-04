#!/usr/bin/env python3
"""
Script pour corriger les imports relatifs dans le backend
"""

import os
import re

def fix_imports_in_file(file_path):
    """Corrige les imports dans un fichier"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns à corriger
    patterns = [
        (r'from core\.', 'from app.core.'),
        (r'from api\.', 'from app.api.'),
        (r'from models\.', 'from app.models.'),
        (r'from services\.', 'from app.services.'),
        (r'from crud\.', 'from app.crud.'),
        (r'from db\.', 'from app.db.'),
        (r'import core\.', 'import app.core.'),
        (r'import api\.', 'import app.api.'),
        (r'import models\.', 'import app.models.'),
        (r'import services\.', 'import app.services.'),
        (r'import crud\.', 'import app.crud.'),
        (r'import db\.', 'import app.db.'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Corrigé: {file_path}")

def fix_imports_in_directory(directory):
    """Corrige les imports dans tous les fichiers Python d'un répertoire"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_imports_in_file(file_path)

if __name__ == "__main__":
    print("🔧 Correction des imports relatifs...")
    fix_imports_in_directory('app')
    print("✅ Correction terminée!") 