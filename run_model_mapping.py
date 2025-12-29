#!/usr/bin/env python3
"""
Model Mapping Launcher
======================

This script provides a simple interface to run the model mapping functionality
with different options and configurations.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main launcher function"""
    print("Turkish Corpus Model Mapping System")
    print("=" * 50)
    print()
    
    print("Seçenekler:")
    print("1. Model Mapping Demo Çalıştır")
    print("2. Enhanced GUI Başlat (Model Mapping ile)")
    print("3. Basit GUI Başlat (Güncellenmiş)")
    print("4. CSV Mapper Demo Çalıştır")
    print("5. Çıkış")
    print()
    
    choice = input("Seçiminizi yapın (1-5): ").strip()
    
    if choice == "1":
        print("\nModel Mapping Demo başlatılıyor...")
        try:
            from example_model_mapping import main as demo_main
            demo_main()
        except ImportError as e:
            print(f"Hata: {e}")
            print("Lütfen gerekli modüllerin yüklü olduğundan emin olun.")
    
    elif choice == "2":
        print("\nEnhanced GUI başlatılıyor...")
        try:
            from gui.enhanced_corpus_gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Hata: {e}")
            print("Lütfen gerekli modüllerin yüklü olduğundan emin olun.")
    
    elif choice == "3":
        print("\nBasit GUI başlatılıyor...")
        try:
            from gui.corpus_gui import main as simple_gui_main
            simple_gui_main()
        except ImportError as e:
            print(f"Hata: {e}")
            print("Lütfen gerekli modüllerin yüklü olduğundan emin olun.")
    
    elif choice == "4":
        print("\nCSV Mapper Demo başlatılıyor...")
        try:
            from csv_mapper import demo_usage
            demo_usage()
        except ImportError as e:
            print(f"Hata: {e}")
            print("Lütfen gerekli modüllerin yüklü olduğundan emin olun.")
    
    elif choice == "5":
        print("Çıkış yapılıyor...")
        sys.exit(0)
    
    else:
        print("Geçersiz seçim. Lütfen 1-5 arasında bir sayı girin.")
        main()

if __name__ == "__main__":
    main()