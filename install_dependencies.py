#!/usr/bin/env python3
"""
Dependencies Installer for BERT Model

Bu script BERT modeli için gerekli kütüphaneleri yükler.
"""

import subprocess
import sys
import os

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 veya üstü gerekli!")
        print(f"   Mevcut sürüm: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} uyumlu")
    return True

def install_package(package):
    """Install a Python package"""
    try:
        print(f"📦 {package} yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} başarıyla yüklendi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} yüklenemedi: {e}")
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Main installation function"""
    print("BERT Model Dependencies Installer")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        return False
    
    print()
    
    # Required packages
    packages = [
        ("transformers", "Transformers library for BERT models"),
        ("torch", "PyTorch deep learning framework"),
        ("numpy", "Numerical computing library"),
    ]
    
    print("📋 Gerekli paketler kontrol ediliyor...")
    print()
    
    failed_packages = []
    
    for package, description in packages:
        print(f"🔍 {package}: {description}")
        
        if check_package(package):
            print(f"   ✅ Zaten yüklü")
        else:
            print(f"   📥 Yükleniyor...")
            if not install_package(package):
                failed_packages.append(package)
                print(f"   ❌ Yükleme başarısız")
        
        print()
    
    # Summary
    print("=" * 50)
    if failed_packages:
        print("❌ Yüklenemeyen paketler:")
        for pkg in failed_packages:
            print(f"   - {pkg}")
        print()
        print("💡 Manuel yükleme için:")
        print("   pip install transformers torch numpy")
        return False
    else:
        print("🎉 Tüm paketler başarıyla yüklendi!")
        print()
        print("🚀 Şimdi BERT modelini kullanabilirsiniz:")
        print("   python run_gui.py")
        print()
        print("📖 Daha fazla bilgi için:")
        print("   python bert_gui_demo.py")
        return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print()
        print("🔧 Sorun giderme:")
        print("1. Python'un PATH'de olduğundan emin olun")
        print("2. Internet bağlantınızı kontrol edin")
        print("3. Yönetici izinleri gerekebilir")
        print("4. Python sanal ortamı kullanmayı deneyin:")
        print("   python -m venv bert_env")
        print("   bert_env\\Scripts\\activate  (Windows)")
        print("   source bert_env/bin/activate  (Linux/Mac)")
        print("   python install_dependencies.py")
    
    input("\nÇıkmak için Enter'a basın...")