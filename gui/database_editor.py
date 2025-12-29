"""
Database Editor Module for Corpus Data Manipulator

Bu modül, veritabanındaki verilerin (documents, sentences, tokens)
kullanıcı tarafından manuel olarak görüntülenmesini ve düzenlenmesini sağlar.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import logging

class DatabaseEditor:
    """GUI component for editing database content"""
    
    def __init__(self, root, db_path):
        self.root = root
        self.root.title("Veritabanı Editörü")
        self.root.geometry("1000x700")
        self.db_path = db_path
        self.conn = None
        
        self.setup_ui()
        self.connect_db()
        self.load_documents()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        """Setup the editor UI"""
        
        # Main layout: SplitView (Left: Documents/Sentences, Right: Tokens)
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # LEFT PANEL: Navigation
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Document List
        ttk.Label(left_frame, text="Dokümanlar:").pack(anchor=tk.W)
        self.doc_list = tk.Listbox(left_frame, height=10)
        self.doc_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.doc_list.bind('<<ListboxSelect>>', self.on_doc_select)
        
        # Sentence List
        ttk.Label(left_frame, text="Cümleler:").pack(anchor=tk.W)
        self.sent_list = tk.Listbox(left_frame, height=20)
        self.sent_list.pack(fill=tk.BOTH, expand=True)
        self.sent_list.bind('<<ListboxSelect>>', self.on_sent_select)
        
        # RIGHT PANEL: Token Editing
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=3)
        
        # Token Table (Treeview)
        columns = ("token_id", "form", "lemma", "upos", "xpos")
        self.token_tree = ttk.Treeview(right_frame, columns=columns, show="headings")
        
        # Column Headings
        self.token_tree.heading("token_id", text="ID")
        self.token_tree.heading("form", text="Kelime (Form)")
        self.token_tree.heading("lemma", text="Kök (Lemma)")
        self.token_tree.heading("upos", text="POS Tag")
        self.token_tree.heading("xpos", text="Detay Tag")
        
        # Column Widths
        self.token_tree.column("token_id", width=50)
        self.token_tree.column("form", width=150)
        self.token_tree.column("lemma", width=150)
        self.token_tree.column("upos", width=100)
        self.token_tree.column("xpos", width=100)
        
        self.token_tree.pack(fill=tk.BOTH, expand=True)
        self.token_tree.bind('<Double-1>', self.on_token_double_click)
        
        # Toolbar
        toolbar = ttk.Frame(right_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="Token Düzenle", command=self.edit_selected_token).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Yeni Token Ekle", command=self.add_token).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Token Sil", command=self.delete_token).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Yenile", command=self.refresh_tokens).pack(side=tk.RIGHT, padx=5)

    def connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            messagebox.showerror("Hata", f"Veritabanına bağlanılamadı: {e}")
            self.root.destroy()

    def load_documents(self):
        """Load documents into the listbox"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT doc_id, doc_name FROM documents")
        docs = cursor.fetchall()
        
        self.doc_list.delete(0, tk.END)
        self.doc_map = {} # Store ID mapping
        
        for doc in docs:
            display = f"[{doc['doc_id']}] {doc['doc_name']}"
            self.doc_list.insert(tk.END, display)
            self.doc_map[display] = doc['doc_id']

    def on_doc_select(self, event):
        """Handle document selection"""
        selection = self.doc_list.curselection()
        if not selection:
            return
            
        doc_display = self.doc_list.get(selection[0])
        doc_id = self.doc_map[doc_display]
        self.load_sentences(doc_id)

    def load_sentences(self, doc_id):
        """Load sentences for a document"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT sent_id, sent_text FROM sentences WHERE doc_id = ?", (doc_id,))
        sentences = cursor.fetchall()
        
        self.sent_list.delete(0, tk.END)
        self.sent_map = {}
        
        for sent in sentences:
            text = sent['sent_text'][:50] + "..." if len(sent['sent_text']) > 50 else sent['sent_text']
            display = f"[{sent['sent_id']}] {text}"
            self.sent_list.insert(tk.END, display)
            self.sent_map[display] = sent['sent_id']

    def on_sent_select(self, event):
        """Handle sentence selection"""
        selection = self.sent_list.curselection()
        if not selection:
            return
            
        sent_display = self.sent_list.get(selection[0])
        self.current_sent_id = self.sent_map[sent_display]
        self.load_tokens(self.current_sent_id)

    def load_tokens(self, sent_id):
        """Load tokens into the treeview"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT token_id, form, lemma, upos, xpos 
            FROM tokens 
            WHERE sent_id = ? 
            ORDER BY token_number
        """, (sent_id,))
        tokens = cursor.fetchall()
        
        # Clear tree
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
            
        for token in tokens:
            self.token_tree.insert("", tk.END, values=(
                token['token_id'],
                token['form'],
                token['lemma'] if token['lemma'] else "",
                token['upos'] if token['upos'] else "",
                token['xpos'] if token['xpos'] else ""
            ))
            
    def on_token_double_click(self, event):
        self.edit_selected_token()

    def edit_selected_token(self):
        """Edit the selected token"""
        selected = self.token_tree.selection()
        if not selected:
            return
            
        item = self.token_tree.item(selected[0])
        values = item['values']
        token_id = values[0]
        
        # Open edit dialog
        self.open_edit_dialog(token_id, values)

    def open_edit_dialog(self, token_id, current_values):
        """Dialog window for editing token fields"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Token Düzenle: {token_id}")
        dialog.geometry("400x300")
        
        # Fields
        fields = ["Form", "Lemma", "UPOS", "XPOS"]
        entries = {}
        
        for i, field in enumerate(fields):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=10)
            entry = ttk.Entry(dialog)
            # Index + 1 because first value is ID
            val = current_values[i+1]
            entry.insert(0, str(val) if val != 'None' else "")
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            entries[field.lower()] = entry
            
        def save():
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE tokens 
                    SET form=?, lemma=?, upos=?, xpos=?, norm=? 
                    WHERE token_id=?
                """, (
                    entries['form'].get(),
                    entries['lemma'].get(),
                    entries['upos'].get(),
                    entries['xpos'].get(),
                    entries['form'].get().lower(), # Simple norm
                    token_id
                ))
                self.conn.commit()
                dialog.destroy()
                self.refresh_tokens()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Güncelleme başarısız: {e}")
                
        ttk.Button(dialog, text="Kaydet", command=save).grid(row=len(fields), column=1, pady=20)

    def add_token(self):
        if not hasattr(self, 'current_sent_id'):
            messagebox.showwarning("Uyarı", "Önce bir cümle seçin!")
            return
            
        # Basit ekleme (şimdilik sona ekler)
        form = simpledialog.askstring("Yeni Token", "Kelime (Form):")
        if form:
            cursor = self.conn.cursor()
            # Get max token number
            cursor.execute("SELECT MAX(token_number) FROM tokens WHERE sent_id=?", (self.current_sent_id,))
            max_num = cursor.fetchone()[0]
            next_num = (max_num + 1) if max_num is not None else 0
            
            try:
                # Minimum fields
                cursor.execute("""
                    INSERT INTO tokens (doc_id, sent_id, token_number, form, norm, start_char, end_char)
                    VALUES ((SELECT doc_id FROM sentences WHERE sent_id=?), ?, ?, ?, ?, 0, 0)
                """, (self.current_sent_id, self.current_sent_id, next_num, form, form.lower()))
                self.conn.commit()
                self.refresh_tokens()
            except Exception as e:
                messagebox.showerror("Hata", f"Ekleme başarısız: {e}")

    def delete_token(self):
        selected = self.token_tree.selection()
        if not selected:
            return
            
        if messagebox.askyesno("Onay", "Seçili token silinsin mi?"):
            item = self.token_tree.item(selected[0])
            token_id = item['values'][0]
            
            try:
                self.conn.execute("DELETE FROM tokens WHERE token_id=?", (token_id,))
                self.conn.commit()
                self.refresh_tokens()
            except Exception as e:
                messagebox.showerror("Hata", f"Silme başarısız: {e}")

    def refresh_tokens(self):
        if hasattr(self, 'current_sent_id'):
            self.load_tokens(self.current_sent_id)

    def on_close(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()
