import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("iCACode 1.0")
        self.dark_theme = False  # Variable to track the theme
        self.language = "plain"  # Default language (no syntax highlighting)
        self.create_widgets()
        self.setup_directory_observer()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Treeview to display directory tree
        self.treeview = ttk.Treeview(main_frame, style="Treeview")
        self.treeview.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the Treeview
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)

        # Text widget for the code editor
        self.text_widget = tk.Text(main_frame, wrap="word", undo=True)
        self.text_widget.pack(side="right", fill="both", expand=True)

        # Initial settings for syntax highlighting
        self.set_syntax_highlighting()

        # Menu bar
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save as...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Delete File", command=self.delete_file)
        file_menu.add_separator()
        file_menu.add_command(label="Open Directory", command=self.open_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        # Advanced Menu
        advanced_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Advanced", menu=advanced_menu)
        advanced_menu.add_command(label="Show Version", command=self.show_version)
        advanced_menu.add_command(label="Reload Tree", command=self.update_treeview)
        advanced_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

        # Language Menu
        language_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Language", menu=language_menu)
        language_menu.add_command(label="C", command=lambda: self.change_language("c"))
        language_menu.add_command(label="C++", command=lambda: self.change_language("cpp"))
        language_menu.add_command(label="C#", command=lambda: self.change_language("csharp"))
        language_menu.add_command(label="Java", command=lambda: self.change_language("java"))
        language_menu.add_command(label="JavaScript", command=lambda: self.change_language("javascript"))
        language_menu.add_command(label="Python", command=lambda: self.change_language("python"))
        language_menu.add_command(label="Plain Text", command=lambda: self.change_language("plain"))

        # Update the directory tree
        self.update_treeview()

        # Connect directory tree selection to editor update function
        self.treeview.bind("<<TreeviewSelect>>", self.update_editor)

        # Connect syntax highlighting function to text modification event
        self.text_widget.bind("<KeyRelease>", self.highlight_syntax)

        # Connect keyboard shortcuts
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-Alt-s>', lambda event: self.save_file_as())
        self.root.bind('<Control-o>', lambda event: self.open_directory())

    def new_file(self):
        self.text_widget.delete("1.0", tk.END)
        self.root.title("iCACode 1.0")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, content)
                self.root.title(f"iCACode 1.0 - {file_path}")

    def save_file(self):
        if hasattr(self, 'current_file'):
            with open(self.current_file, "w") as file:
                content = self.text_widget.get("1.0", tk.END)
                file.write(content)
                self.root.title(f"iCACode 1.0 - {self.current_file}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                content = self.text_widget.get("1.0", tk.END)
                file.write(content)
                self.current_file = file_path
                self.root.title(f"iCACode 1.0 - {file_path}")

    def show_version(self):
        tk.messagebox.showinfo("Version", "iCACode 1.0")

    def update_treeview(self):
        # Clear the existing directory tree
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Get the list of files and directories in the current directory
        current_directory = os.getcwd()
        for item in os.listdir(current_directory):
            # Add each item to the tree
            self.treeview.insert("", "end", text=item, open=True)

    def update_editor(self, event):
        # Get the selected item in the directory tree
        selected_item = self.treeview.selection()
        if selected_item:
            # Get the text of the selected item
            item_text = self.treeview.item(selected_item, "text")

            # Open the selected file and display its content in the editor
            file_path = os.path.join(os.getcwd(), item_text)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    content = file.read()
                    self.text_widget.delete("1.0", tk.END)
                    self.text_widget.insert(tk.END, content)
                    self.root.title(f"iCACode 1.0 - {file_path}")

    def delete_file(self):
        # Get the selected item in the directory tree
        selected_item = self.treeview.selection()
        if selected_item:
            # Get the text of the selected item
            item_text = self.treeview.item(selected_item, "text")

            # Build the path of the selected file
            file_path = os.path.join(os.getcwd(), item_text)

            # Display a confirmation message
            confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the file '{item_text}'?")
            if confirmation:
                try:
                    # Delete the file
                    os.remove(file_path)
                    messagebox.showinfo("Success", f"File '{item_text}' deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting file '{item_text}': {str(e)}")

    def open_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            os.chdir(directory_path)
            self.update_treeview()
            self.root.title(f"iCACode 1.0 - {directory_path}")

    def toggle_theme(self):
        # Toggle between light and dark themes
        self.dark_theme = not self.dark_theme

        if self.dark_theme:
            self.root.tk_setPalette(background="#2E2E2E", foreground="#FFFFFF")
            style = ttk.Style(self.root)
            style.configure("Treeview", background="#2E2E2E", foreground="#FFFFFF", fieldbackground="#2E2E2E")
            style.map("Treeview", background=[("selected", "#0078d4")])
        else:
            self.root.tk_setPalette(background="#f0f0f0", foreground="#000000")
            style = ttk.Style(self.root)
            style.configure("Treeview", background="#f0f0f0", foreground="#000000", fieldbackground="#f0f0f0")
            style.map("Treeview", background=[("selected", "#0078d4")])

    def change_language(self, language):
        self.language = language
        self.set_syntax_highlighting()

    def set_syntax_highlighting(self):
        # Configure syntax highlighting for the current language
        content = self.text_widget.get("1.0", tk.END)
        self.text_widget.tag_delete("c", "1.0", tk.END)
        self.text_widget.tag_delete("cpp", "1.0", tk.END)
        self.text_widget.tag_delete("csharp", "1.0", tk.END)
        self.text_widget.tag_delete("java", "1.0", tk.END)
        self.text_widget.tag_delete("javascript", "1.0", tk.END)
        self.text_widget.tag_delete("python", "1.0", tk.END)

        if self.language == "c":
            self.text_widget.tag_configure("c", foreground="#00F", font=("Courier New", 12, "bold"))
            self.text_widget.tag_add("c", "1.0", tk.END)
        elif self.language == "cpp":
            self.text_widget.tag_configure("cpp", foreground="#00F", font=("Courier New", 12, "bold"))
            self.text_widget.tag_add("cpp", "1.0", tk.END)
        elif self.language == "csharp":
            self.text_widget.tag_configure("csharp", foreground="#178600", font=("Courier New", 12, "bold"))
            self.text_widget.tag_add("csharp", "1.0", tk.END)
        elif self.language == "java":
            self.text_widget.tag_configure("java", foreground="#00A", font=("Courier New", 12, "italic"))
            self.text_widget.tag_add("java", "1.0", tk.END)
        elif self.language == "javascript":
            self.text_widget.tag_configure("javascript", foreground="#f00", font=("Courier New", 12, "normal"))
            self.text_widget.tag_add("javascript", "1.0", tk.END)
        elif self.language == "python":
            self.text_widget.tag_configure("python", foreground="#0A0", font=("Courier New", 12, "normal"))
            self.text_widget.tag_add("python", "1.0", tk.END)

    def highlight_syntax(self, event):
        # Highlight syntax while typing
        self.set_syntax_highlighting()

    def setup_directory_observer(self):
        # Set up monitoring for the current directory
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_any_event = self.handle_directory_event

        self.directory_observer = Observer()
        self.directory_observer.schedule(self.event_handler, path=os.getcwd(), recursive=False)
        self.directory_observer.start()

    def handle_directory_event(self, event):
        # Update the directory tree when there is a change in the directory
        self.update_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
