import os
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext
from ftplib import FTP


class FTPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Client")

        self.setup_ui()

    def setup_ui(self):
        self.server_frame = ttk.Frame(self.root)
        self.server_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.server_frame, text="Server:").grid(row=0, column=0)
        self.server_entry = ttk.Entry(self.server_frame)
        self.server_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.server_frame, text="Port:").grid(row=0, column=2)
        self.port_entry = ttk.Entry(self.server_frame)
        self.port_entry.grid(row=0, column=3, padx=5)

        ttk.Label(self.server_frame, text="User:").grid(row=1, column=0)
        self.username_entry = ttk.Entry(self.server_frame)
        self.username_entry.grid(row=1, column=1, padx=5)

        ttk.Label(self.server_frame, text="Pass:").grid(row=1, column=2)
        self.password_entry = ttk.Entry(self.server_frame, show="*")
        self.password_entry.grid(row=1, column=3, padx=5)

        self.connect_button = ttk.Button(self.server_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=1, column=4, padx=5)

        self.file_operation_frame = ttk.Frame(self.root)
        self.file_operation_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(self.file_operation_frame, text="File Name:").grid(row=0, column=0)
        self.file_name_entry = ttk.Entry(self.file_operation_frame)
        self.file_name_entry.grid(row=0, column=1, padx=5)

        self.create_button = ttk.Button(self.file_operation_frame, text="Create/Edit", command=self.edit_file)
        self.create_button.grid(row=0, column=2, padx=5)

        self.upload_button = ttk.Button(self.file_operation_frame, text="Upload", command=self.upload_file)
        self.upload_button.grid(row=0, column=3, padx=5)

        self.download_button = ttk.Button(self.file_operation_frame, text="Download", command=self.download_file)
        self.download_button.grid(row=0, column=4, padx=5)

        self.delete_button = ttk.Button(self.file_operation_frame, text="Delete", command=self.delete_file)
        self.delete_button.grid(row=0, column=5, padx=5)

        self.files_text = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.files_text.grid(row=3, column=0, padx=10, pady=5)

    def connect_to_server(self):
        server = self.server_entry.get()
        port = int(self.port_entry.get()) if self.port_entry.get() else 21
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            self.ftp = FTP()
            self.ftp.connect(server, port)
            self.ftp.login(username, password)
            self.list_files()
        except Exception as e:
            messagebox.showerror("Something is wrong", str(e))
            if self.ftp:
                self.ftp.quit()

    def list_files(self):
        self.files_text.delete('1.0', tk.END)
        files = self.ftp.nlst()
        for file in files:
            self.files_text.insert(tk.END, file + '\n')

    def edit_file(self):
        file_name = self.file_name_entry.get()
        if not file_name:
            messagebox.showwarning("Warning", "Please enter a file name.")
            return
        try:
            local_file = f"temp_{file_name}"
            with open(local_file, 'wb') as file:
                self.ftp.retrbinary(f'RETR {file_name}', file.write)

            with open(local_file, 'r') as file:
                content = file.read()

            self.open_editor(file_name, content)

            os.remove(local_file)
        except Exception as e:
            self.open_editor(file_name, "")

    def open_editor(self, file_name, content):
        editor = tk.Toplevel(self.root)
        editor.title(f"Editing {file_name}")
        text_area = scrolledtext.ScrolledText(editor, width=80, height=25)
        text_area.pack(padx=10, pady=10)
        text_area.insert(tk.END, content)

        save_button = ttk.Button(editor, text="Save",
                                 command=lambda: self.save_file(file_name, text_area.get("1.0", tk.END), editor))
        save_button.pack(pady=5)

    def save_file(self, file_name, content, editor):
        try:
            with open(file_name, 'w') as file:
                file.write(content)
            self.upload_file(file_name)
            editor.destroy()
            messagebox.showinfo("Success", "File saved and uploaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upload_file(self, file_name=None):
        file_name = file_name or self.file_name_entry.get()
        if not file_name:
            messagebox.showwarning("Warning", "Please enter a file name.")
            return
        try:
            file_path = Path(file_name)
            if not file_path.exists() or not file_path.is_file():
                messagebox.showwarning("Error", "No such file in your computer.")
                return
            with open(file_name, 'rb') as file:
                self.ftp.storbinary(f'STOR {file_name}', file)
            self.list_files()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def download_file(self):
        file_name = self.file_name_entry.get()
        if not file_name:
            messagebox.showwarning("Warning", "Please enter a file name.")
            return
        with open(file_name, 'wb') as file:
            self.ftp.retrbinary(f'RETR {file_name}', file.write)
        messagebox.showinfo("Info", f"File {file_name} downloaded successfully.")

    def delete_file(self):
        file_name = self.file_name_entry.get()
        if not file_name:
            messagebox.showwarning("Warning", "Please enter a file name.")
            return
        self.ftp.delete(file_name)
        self.list_files()


def main():
    root = tk.Tk()
    FTPClientGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
