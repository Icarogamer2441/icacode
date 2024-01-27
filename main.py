import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import simpledialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("iCACode 1.3")
        self.themes = {
            "Default": {"background": "#f0f0f0", "foreground": "#000000", "fieldbackground": "#f0f0f0", "selected": "#0078d4"},
            "Dark": {"background": "#2E2E2E", "foreground": "#FFFFFF", "fieldbackground": "#2E2E2E", "selected": "#0078d4"},
            "Green": {"background": "#00FF00", "foreground": "#000000", "fieldbackground": "#00FF00", "selected": "#0078d4"},
            "Blue": {"background": "#0000FF", "foreground": "#FFFFFF", "fieldbackground": "#0000FF", "selected": "#0078d4"},
            "Red": {"background": "#FF0000", "foreground": "#FFFFFF", "fieldbackground": "#FF0000", "selected": "#0078d4"},
            "Purple": {"background": "#800080", "foreground": "#FFFFFF", "fieldbackground": "#800080", "selected": "#0078d4"},
            "Orange": {"background": "#FFA500", "foreground": "#000000", "fieldbackground": "#FFA500", "selected": "#0078d4"}
        }
        self.selected_theme = "Default"
        self.language = "plain"  # Inicializando a variável language
        self.create_widgets()
        self.setup_directory_observer()
        self.treeview_open = True
        self.editor_window = None

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Treeview to display directory tree
        self.treeview = ttk.Treeview(main_frame, style="Custom.Treeview")
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

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save as...", command=self.save_file_as)
        file_menu.add_command(label="New Folder", command=self.create_new_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Open iCACode", command=self.open_icacode)
        file_menu.add_separator()
        file_menu.add_command(label="Delete File", command=self.delete_file)
        file_menu.add_separator()
        file_menu.add_command(label="Open Directory", command=self.open_directory)
        file_menu.add_separator()

        # Subsubmenu para o botão "Back"
        back_submenu = tk.Menu(file_menu, tearoff=0)
        back_submenu.add_command(label="Back", command=self.navigate_back)
        file_menu.add_cascade(label="Navigate", menu=back_submenu)

        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)


        # Advanced Menu
        advanced_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Advanced", menu=advanced_menu)
        advanced_menu.add_command(label="Show Version", command=self.show_version)
        advanced_menu.add_command(label="Reload Tree", command=self.update_treeview)
        advanced_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        advanced_menu.add_command(label="Close Treeview", command=self.toggle_treeview)
        advanced_menu.add_separator()
        theme_menu = tk.Menu(advanced_menu, tearoff=0)
        advanced_menu.add_cascade(label="Select Theme", menu=theme_menu)
        for theme_name in self.themes.keys():
            theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.select_theme(name))
        
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

        # Execute Menu
        execute_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Execute", menu=execute_menu)
        execute_menu.add_command(label="Python", command=lambda: self.execute_file("python"))
        execute_menu.add_command(label="JavaScript", command=lambda: self.execute_file("javascript"))
        execute_menu.add_command(label="C/C++", command=lambda: self.execute_file("c_cpp"))

        # Update the directory tree
        self.update_treeview()

        # Connect directory tree selection to editor update function
        self.treeview.bind("<<TreeviewSelect>>", self.update_editor)

        # Connect syntax highlighting function to text modification event
        self.text_widget.bind("<KeyRelease>", self.highlight_syntax)

        # Connect right-click event for deleting files
        self.text_widget.bind("<Button-3>", self.show_context_menu)

        # Connect keyboard shortcuts
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-Alt-s>', lambda event: self.save_file_as())
        self.root.bind('<Control-o>', lambda event: self.open_directory())
        self.root.bind('<Control-b>', lambda event: self.navigate_back())
        
        self.root.bind('<Up>', lambda event: self.navigate_directory(-1))
        self.root.bind('<Down>', lambda event: self.navigate_directory(1))

    def open_icacode(self):
        icacode_path = os.path.abspath(__file__)  # Caminho absoluto do script iCACode
        with open(icacode_path, "r") as icacode_file:
            content = icacode_file.read()
            self.open_editor_window(content)

    def open_editor_window(self, initial_content=""):
        # Abre uma nova janela para editar o conteúdo fornecido
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Code Editor")

        # Text widget para o editor de código
        editor_text_widget = tk.Text(editor_window, wrap="word", undo=True)
        editor_text_widget.pack(fill="both", expand=True)
        editor_text_widget.insert(tk.END, initial_content)

        # Botão para salvar, rodar e fechar a janela
        save_run_button = tk.Button(editor_window, text="Save, Run, and Close", command=lambda: self.save_run_close_editor(editor_text_widget, editor_window))
        save_run_button.pack(side="bottom", pady=5)

    def save_run_close_editor(self, editor_text_widget, editor_window):
        # Salva o conteúdo do editor de código no arquivo "ic_modify.py"
        modified_file_path = "ic_modify.py"
        with open(modified_file_path, "w") as modified_file:
            modified_file.write(editor_text_widget.get("1.0", tk.END))

        # Executa o código do arquivo modificado
        subprocess.run(["python", modified_file_path])

        # Fecha a janela do editor de código
        editor_window.destroy()  

    def navigate_directory(self, direction):
        selected_item = self.treeview.selection()
        if selected_item:
            index = self.treeview.index(selected_item)
            new_index = index + direction
            if 0 <= new_index < len(self.treeview.get_children()):
                new_item = self.treeview.get_children()[new_index]
                self.treeview.selection_set(new_item)
                self.treeview.see(new_item)
                self.update_editor(None)  # Atualiza o editor para exibir o conteúdo do novo item
    
    def create_new_folder(self):
        # Abre uma caixa de diálogo para inserir o nome da nova pasta
        folder_name = filedialog.askstring("New Folder", "Enter the name of the new folder:")
        if folder_name:
            try:
                # Cria a nova pasta
                os.mkdir(folder_name)
                messagebox.showinfo("Success", f"Folder '{folder_name}' created successfully.")
                # Atualiza a árvore de diretórios
                self.update_treeview()
            except Exception as e:
                messagebox.showerror("Error", f"Error creating folder '{folder_name}': {str(e)}")
    
    def toggle_treeview(self):
        if self.treeview_open:
            self.treeview.pack_forget()
            self.treeview_open = False
        else:
            self.treeview.pack(side="left", fill="both", expand=True)
            self.treeview_open = True
        
    def navigate_back(self):
        current_directory = os.getcwd()
        parent_directory = os.path.dirname(current_directory)
    
        if current_directory != parent_directory:
            os.chdir(parent_directory)
            self.update_treeview()
            self.root.title(f"iCACode 1.3 - {parent_directory}")

    def new_file(self):
        self.text_widget.delete("1.0", tk.END)
        self.root.title("iCACode 1.3")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, content)
                self.root.title(f"iCACode 1.3 - {file_path}")

    def save_file(self):
        if hasattr(self, 'current_file'):
            with open(self.current_file, "w") as file:
                content = self.text_widget.get("1.0", tk.END)
                file.write(content)
                self.root.title(f"iCACode 1.3 - {self.current_file}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                content = self.text_widget.get("1.0", tk.END)
                file.write(content)
                self.current_file = file_path
                self.root.title(f"iCACode 1.3 - {file_path}")

    def show_version(self):
        tk.messagebox.showinfo("Version", "iCACode 1.3")

    def update_treeview(self):
        # Clear the existing directory tree
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Get the list of files and directories in the current directory
        current_directory = os.getcwd()
        for item in os.listdir(current_directory):
            item_path = os.path.join(current_directory, item)
            is_directory = os.path.isdir(item_path)
            tags = ("directory",) if is_directory else ("file",)
            self.treeview.insert("", "end", text=item, open=True, tags=tags)
            
            # Tagging directories with the "directory" tag
            if is_directory:
                self.treeview.tag_configure("directory", foreground="#0000FF")


    def update_editor(self, event):
        # Get the selected item in the directory tree
        selected_item = self.treeview.selection()
        if selected_item:
            # Get the text of the selected item
            item_text = self.treeview.item(selected_item, "text")

            # Open the selected file or directory
            item_path = os.path.join(os.getcwd(), item_text)
            if os.path.isfile(item_path):
                with open(item_path, "r") as file:
                    content = file.read()
                    self.text_widget.delete("1.0", tk.END)
                    self.text_widget.insert(tk.END, content)
                    self.root.title(f"iCACode 1.3 - {item_path}")
            elif os.path.isdir(item_path):
                os.chdir(item_path)
                self.update_treeview()
                self.root.title(f"iCACode 1.3 - {item_path}")

    def delete_file(self):
        # Get the selected item in the directory tree
        selected_item = self.treeview.selection()
        if selected_item:
            # Get the text of the selected item
            item_text = self.treeview.item(selected_item, "text")

            # Build the path of the selected file or directory
            item_path = os.path.join(os.getcwd(), item_text)

            # Display a confirmation message
            confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete the { 'file' if os.path.isfile(item_path) else 'directory'} '{item_text}'?")
            if confirmation:
                try:
                    # Delete the file or directory
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        os.rmdir(item_path)
                    messagebox.showinfo("Success", f"{ 'File' if os.path.isfile(item_path) else 'Directory'} '{item_text}' deleted successfully.")
                    # Update the directory tree
                    self.update_treeview()
                except Exception as e:
                    messagebox.showerror("Error", f"Error deleting { 'file' if os.path.isfile(item_path) else 'directory'} '{item_text}': {str(e)}")

    def apply_theme(self):
        selected_theme = self.selected_theme
        theme_settings = self.themes[selected_theme]

        self.root.tk_setPalette(
            background=theme_settings["background"],
            foreground=theme_settings["foreground"]
        )

        style = ttk.Style(self.root)
        style.configure(
            "Treeview",
            background=theme_settings["fieldbackground"],
            foreground=theme_settings["foreground"]
        )
        style.map("Treeview", background=[("selected", theme_settings["selected"])])

        self.text_widget.config(
            background=theme_settings["background"],
            foreground=theme_settings["foreground"]
        )

    def open_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            os.chdir(directory_path)
            self.update_treeview()
            self.root.title(f"iCACode 1.3 - {directory_path}")

    def toggle_theme(self):
        # Toggle entre os temas existentes e o tema personalizado
        themes_list = list(self.themes.keys())
        current_index = themes_list.index(self.selected_theme)
        next_index = (current_index + 1) % len(themes_list)
        next_theme = themes_list[next_index]

        self.selected_theme = next_theme
        self.apply_theme()

    def select_theme(self, theme_name):
        # Apply the selected theme
        self.selected_theme = theme_name
        theme = self.themes[theme_name]
        self.root.tk_setPalette(
            background=theme["background"],
            foreground=theme["foreground"]
        )
        style = ttk.Style(self.root)
        style.configure("Treeview", background=theme["background"], foreground=theme["foreground"], fieldbackground=theme["fieldbackground"])
        style.map("Treeview", background=[("selected", theme["selected"])])

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

    def execute_file(self, language):
        # Execute the current file using the selected language
        if hasattr(self, 'current_file'):
            if language == "python" and self.current_file.endswith(".py"):
                subprocess.run(["python", self.current_file])
            elif language == "javascript" and self.current_file.endswith(".js"):
                subprocess.run(["node", self.current_file])
            elif language == "c_cpp" and (self.current_file.endswith(".c") or self.current_file.endswith(".cpp")):
                subprocess.run(["gcc", "-o", "output", self.current_file])
                subprocess.run(["./output"])
            else:
                messagebox.showwarning("Execution Warning", f"Cannot execute file with {language}.")

    def show_context_menu(self, event):
        # Show context menu for right-click event
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Delete File", command=self.delete_file)
        menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.mainloop()
