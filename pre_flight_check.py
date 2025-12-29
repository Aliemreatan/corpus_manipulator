"""
Pre-Flight Check Script

Bu script, projeyi başka bir bilgisayara kurduğunuzda veya GitHub'a yüklemeden önce
tüm bağımlılıkların ve modüllerin doğru çalışıp çalışmadığını kontrol eder.
"""

import sys
import importlib
import os

def check_module(module_name, install_name=None):
    if install_name is None:
        install_name = module_name
    
    print(f"Kontrol ediliyor: {module_name}...", end=" ")
    try:
        importlib.import_module(module_name)
        print("✅ OK")
        return True
    except ImportError:
        print(f"❌ EKSİK! (Yüklemek için: pip install {install_name})")
        return False

def check_project_structure():
    print("\nProje yapısı kontrol ediliyor...")
    required_files = [
        "run_gui.py",
        "requirements.txt",
        "README.md",
        "gui/__init__.py",
        "nlp/__init__.py",
        "database/__init__.py",
        "query/__init__.py",
        "ingestion/__init__.py"
    ]
    
    all_ok = True
    for f in required_files:
        if os.path.exists(f):
            print(f"  ✅ {f} mevcut")
        else:
            print(f"  ❌ {f} EKSİK!")
            all_ok = False
            
            # Create empty __init__.py if missing
            if f.endswith("__init__.py"):
                print(f"     -> Oluşturuluyor: {f}")
                os.makedirs(os.path.dirname(f), exist_ok=True)
                with open(f, 'w') as init_file:
                    init_file.write("")
    
    return all_ok

def main():
    print("=== CORPUS MANIPULATOR SİSTEM KONTROLÜ ===\n")
    
    # 1. Kütüphane Kontrolü
    libraries = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("sqlite3", None), # Standard lib
        ("tkinter", None), # Standard lib
        ("matplotlib", "matplotlib"),
        ("wordcloud", "wordcloud"),
        ("torch", "torch"),
        ("transformers", "transformers"),
        ("tqdm", "tqdm")
    ]
    
    missing_libs = []
    for mod, install in libraries:
        if not check_module(mod, install):
            if install: missing_libs.append(install)
            
    if missing_libs:
        print("\n⚠️ EKSİK KÜTÜPHANELER VAR!")
        print("Lütfen şu komutu çalıştırın:")
        print(f"pip install {' '.join(missing_libs)}")
        print("-" * 40)
    else:
        print("\n✅ Tüm dış kütüphaneler hazır.")

    # 2. Proje Yapısı Kontrolü
    if check_project_structure():
        print("\n✅ Proje yapısı düzgün.")
    
    # 3. GUI Import Testi
    print("\nGUI Modülü Test Ediliyor...")
    try:
        sys.path.insert(0, os.path.abspath("."))
        from gui.corpus_gui import CorpusGUI
        print("✅ GUI modülü başarıyla yüklendi (Syntax hatası yok).")
    except Exception as e:
        print(f"❌ GUI YÜKLEME HATASI: {e}")
        return

    print("\n" + "="*40)
    print("🚀 SİSTEM HAZIR! GitHub'a yüklenebilir.")
    print("="*40)

if __name__ == "__main__":
    main()
