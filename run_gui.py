#!/usr/bin/env python3
"""
Corpus Data Manipulator - GUI Launcher

Tkinter tabanlı GUI uygulamasını başlatır

Kullanım:
    py run_gui.py
    veya
    python run_gui.py
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """Check if required modules are available"""
    missing_modules = []
    
    try:
        import tkinter
    except ImportError:
        missing_modules.append("tkinter")
    
    try:
        import sqlite3
    except ImportError:
        missing_modules.append("sqlite3")
    
    try:
        import threading
    except ImportError:
        missing_modules.append("threading")
    
    # Check if corpus_manipulator modules are available
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from gui.corpus_gui import CorpusGUI
    except ImportError as e:
        missing_modules.append("corpus_manipulator modules")
        print(f"Import error: {e}")
    
    return missing_modules

def main():
    """Main function"""
    print("Corpus Data Manipulator - GUI Launcher")
    print("=" * 50)
    
    # Check requirements
    missing = check_requirements()
    if missing:
        print("Eksik moduller:")
        for module in missing:
            print(f"   - {module}")
        print("\nLutfen gerekli modulleri yukleyin:")
        print("pip install -r requirements.txt")
        
        # Try to show error dialog
        try:
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror(
                "Eksik Moduller",
                "Gerekli moduller yuklu degil.\n\n"
                "Lutfen su komutu calistirin:\n"
                "pip install -r requirements.txt"
            )
            root.destroy()
        except:
            pass
        
        return 1
    
    print("Tum gereksinimler mevcut")
    
    # Import and run GUI
    try:
        from gui.corpus_gui import CorpusGUI
        import tkinter as tk
        
        print("GUI baslatiliyor...")
        
        # Create and run GUI
        root = tk.Tk()
        app = CorpusGUI(root)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenwidth() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        print("GUI hazir! Pencere aciliyor...")
        root.mainloop()
        
    except Exception as e:
        print(f"GUI baslatilamadi: {e}")
        
        # Show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Hata",
                f"GUI baslatilamadi:\n\n{str(e)}\n\n"
                "Lutfen hata mesajini kontrol edin."
            )
            root.destroy()
        except:
            pass
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)