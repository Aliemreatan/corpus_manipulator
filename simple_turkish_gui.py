#!/usr/bin/env python3
"""
Simple Turkish Character GUI Fix

Direct GUI approach without console output issues.
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def main():
    """Simple Turkish character GUI"""
    
    # Create main window
    root = tk.Tk()
    root.title("Turkish Character Test - GUI Fix")
    root.geometry("800x600")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Configure grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(3, weight=1)
    
    # Title
    title_label = ttk.Label(main_frame, text="Turkish Character Test", font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Test input
    ttk.Label(main_frame, text="Enter Turkish text:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
    
    text_widget = tk.Text(main_frame, height=4, width=60)
    text_widget.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # Insert sample Turkish text
    sample_text = "Şu çalışma çok güzel. Öğrenciler okulda öğreniyor."
    text_widget.insert(tk.END, sample_text)
    
    # Process button
    def process_text():
        input_text = text_widget.get(1.0, tk.END).strip()
        
        # Check for Turkish characters
        turkish_chars = 'şçğıöüğıİÇĞÖŞÜ'
        found_chars = [c for c in input_text if c in turkish_chars]
        
        # Display results
        results_text.delete(1.0, tk.END)
        results_text.insert(tk.END, f"Input: {input_text}\n\n")
        results_text.insert(tk.END, f"Turkish characters found: {set(found_chars)}\n")
        results_text.insert(tk.END, f"Character count: {len(found_chars)}\n\n")
        
        if found_chars:
            results_text.insert(tk.END, "SUCCESS: Turkish characters are working!\n")
            results_text.insert(tk.END, "You can now use Turkish text in the GUI.\n")
        else:
            results_text.insert(tk.END, "WARNING: No Turkish characters detected.\n")
    
    process_btn = ttk.Button(main_frame, text="Test Turkish Characters", command=process_text)
    process_btn.grid(row=2, column=0, columnspan=2, pady=(0, 20))
    
    # Results display
    ttk.Label(main_frame, text="Results:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
    
    results_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
    results_text.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
    
    # Instructions
    instructions = ttk.Label(main_frame, text="Instructions:\n1. Type Turkish text above\n2. Click 'Test Turkish Characters'\n3. Check if Turkish characters are preserved", 
                           font=("Arial", 10), foreground="blue")
    instructions.grid(row=4, column=0, columnspan=2, pady=(10, 0))
    
    # Status bar
    status_var = tk.StringVar(value="Ready for Turkish character testing")
    status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    # Initial test
    process_text()
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main()