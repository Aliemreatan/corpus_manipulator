#!/usr/bin/env python3
"""
Fix for ş and ı keyboard input issue

This script specifically addresses the ş and ı character mapping problems.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext

def fix_turkish_keyboard_mapping():
    """Create GUI with proper Turkish keyboard mapping for ş and ı"""
    
    root = tk.Tk()
    root.title("Turkish Keyboard Fix - ş and ı Characters")
    root.geometry("900x700")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Configure grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(4, weight=1)
    
    # Title
    title_label = ttk.Label(main_frame, text="Turkish Keyboard Fix - ş and ı Characters", 
                           font=("Arial", 14, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Problem explanation
    problem_label = ttk.Label(main_frame, 
                             text="Problem: ş and ı characters may show as þ and ý due to keyboard layout.\n" +
                                  "Solution: This GUI provides proper character mapping and testing.",
                             font=("Arial", 10), foreground="red")
    problem_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))
    
    # Test input section
    ttk.Label(main_frame, text="Test Input (Type Turkish characters):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
    
    text_widget = tk.Text(main_frame, height=4, width=70)
    text_widget.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # Character mapping info
    mapping_frame = ttk.LabelFrame(main_frame, text="Turkish Character Keyboard Mapping", padding="10")
    mapping_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
    
    # Character mapping display
    mapping_text = scrolledtext.ScrolledText(mapping_frame, height=6, wrap=tk.WORD)
    mapping_text.pack(fill=tk.BOTH, expand=True)
    
    # Insert character mapping information
    mapping_info = """TURKISH KEYBOARD MAPPING GUIDE:

Lowercase Letters:
• ş = press 's' + cedilla (ş) - may show as 'þ' on some keyboards
• ç = press 'c' + cedilla (ç) - should work normally
• ğ = press 'g' + breve (ğ) - should work normally  
• ı = press 'i' without dot (ı) - may show as 'ý' on some keyboards
• ö = press 'o' + diaeresis (ö) - should work normally
• ü = press 'u' + diaeresis (ü) - should work normally

Uppercase Letters:
• Ş = press Shift + 's' + cedilla (Ş)
• Ç = press Shift + 'c' + cedilla (Ç)
• Ğ = press Shift + 'g' + breve (Ğ)
• İ = press Shift + 'i' with dot (İ)
• Ö = press Shift + 'o' + diaeresis (Ö)
• Ü = press Shift + 'u' + diaeresis (Ü)

COMMON KEYBOARD ISSUES:
• Some keyboards may show 'ş' as 'þ' (thorn)
• Some keyboards may show 'ı' as 'ý' (y with acute)
• This is a KEYBOARD LAYOUT issue, not a software issue

SOLUTION:
1. Use Turkish Q keyboard layout in Windows
2. Or use the character picker to insert correct characters
3. The software now handles both representations correctly
"""
    
    mapping_text.insert(tk.END, mapping_info)
    mapping_text.config(state=tk.DISABLED)
    
    # Process button
    def process_with_mapping_fix():
        input_text = text_widget.get(1.0, tk.END).strip()
        
        # Fix common keyboard mapping issues
        fixed_text = input_text
        
        # Common keyboard substitutions
        substitutions = {
            'þ': 'ş',  # thorn to s-cedilla
            'ý': 'ı',  # y-acute to dotless-i
        }
        
        # Apply substitutions
        for wrong_char, correct_char in substitutions.items():
            fixed_text = fixed_text.replace(wrong_char, correct_char)
        
        # Check for Turkish characters in both original and fixed
        turkish_chars = 'şçğıöüğıİÇĞÖŞÜ'
        
        original_chars = [c for c in input_text if c in turkish_chars]
        fixed_chars = [c for c in fixed_text if c in turkish_chars]
        
        # Character mapping analysis
        mapping_analysis = {}
        for char in fixed_text:
            if char in turkish_chars:
                if char not in mapping_analysis:
                    mapping_analysis[char] = 0
                mapping_analysis[char] += 1
        
        # Display results
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, "=== TURKISH CHARACTER ANALYSIS ===\n\n")
        
        results_text.insert(tk.END, f"Original input: {input_text}\n")
        results_text.insert(tk.END, f"Fixed text: {fixed_text}\n\n")
        
        if input_text != fixed_text:
            results_text.insert(tk.END, "KEYBOARD MAPPING FIXES APPLIED:\n")
            for wrong_char, correct_char in substitutions.items():
                if wrong_char in input_text:
                    results_text.insert(tk.END, f"  {wrong_char} → {correct_char}\n")
            results_text.insert(tk.END, "\n")
        
        results_text.insert(tk.END, f"Turkish characters found: {set(fixed_chars)}\n")
        results_text.insert(tk.END, f"Character distribution: {dict(mapping_analysis)}\n\n")
        
        # Specific check for ş and ı
        if 'ş' in fixed_text or 'ı' in fixed_text:
            results_text.insert(tk.END, "✅ SUCCESS: ş and ı characters are working!\n")
            if 'ş' in fixed_text:
                results_text.insert(tk.END, f"  - 'ş' character found {mapping_analysis.get('ş', 0)} times\n")
            if 'ı' in fixed_text:
                results_text.insert(tk.END, f"  - 'ı' character found {mapping_analysis.get('ı', 0)} times\n")
        else:
            results_text.insert(tk.END, "⚠️  ş and ı characters not detected.\n")
            results_text.insert(tk.END, "Try typing them directly or use the character guide above.\n")
        
        results_text.insert(tk.END, "\n=== RECOMMENDATIONS ===\n")
        results_text.insert(tk.END, "1. Set Windows keyboard to Turkish Q layout\n")
        results_text.insert(tk.END, "2. Use Alt+0151 for ş, Alt+0236 for ı (if needed)\n")
        results_text.insert(tk.END, "3. The software now handles keyboard mapping issues\n")
    
    process_btn = ttk.Button(main_frame, text="Process with ş and ı Fix", command=process_with_mapping_fix)
    process_btn.grid(row=4, column=0, columnspan=2, pady=(0, 15))
    
    # Results display
    ttk.Label(main_frame, text="Analysis Results:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
    
    results_text = scrolledtext.ScrolledText(main_frame, height=12, wrap=tk.WORD)
    results_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Quick test buttons
    quick_test_frame = ttk.Frame(main_frame)
    quick_test_frame.grid(row=7, column=0, columnspan=3, pady=(15, 0))
    
    def insert_test_word(word):
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, word)
        process_with_mapping_fix()
    
    ttk.Button(quick_test_frame, text="Test ş", 
              command=lambda: insert_test_word("şarkı")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(quick_test_frame, text="Test ı", 
              command=lambda: insert_test_word("ırmak")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(quick_test_frame, text="Test ç", 
              command=lambda: insert_test_word("çiçek")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(quick_test_frame, text="Test ö", 
              command=lambda: insert_test_word("öğrenci")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(quick_test_frame, text="Test ü", 
              command=lambda: insert_test_word("güzel")).pack(side=tk.LEFT, padx=(0, 5))
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Initial test
    process_with_mapping_fix()
    
    root.mainloop()

if __name__ == "__main__":
    fix_turkish_keyboard_mapping()