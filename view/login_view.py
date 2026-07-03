import tkinter as tk
from tkinter import ttk, messagebox


class LoginView(tk.Tk):
    """Login screen — asks for the master password before granting access."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Password Vault — Login")
        self.geometry("380x220")
        self.resizable(False, False)
        self.result = False
        self._build_ui()

    def _build_ui(self) -> None:
        self.configure(padx=30, pady=30)

        is_first = self.controller.is_first_launch()
        title = "Create Master Password" if is_first else "Enter Master Password"

        ttk.Label(self, text="🔐 Password Vault",
                  font=("Segoe UI", 14, "bold")).pack(pady=(0, 4))
        ttk.Label(self, text=title,
                  foreground="gray").pack(pady=(0, 16))

        self.pwd_var = tk.StringVar()
        self.pwd_entry = ttk.Entry(self, textvariable=self.pwd_var, show="*", width=30)
        self.pwd_entry.pack(pady=(0, 12))
        self.pwd_entry.focus()

        btn_text = "Create" if is_first else "Unlock"
        ttk.Button(self, text=btn_text,
                   command=self._on_submit).pack()

        self.bind("<Return>", lambda e: self._on_submit())

    def _on_submit(self) -> None:
        password = self.pwd_var.get()
        if not password:
            messagebox.showwarning("Warning", "Please enter a password.")
            return

        if self.controller.is_first_launch():
            ok, msg = self.controller.setup_master(password)
        else:
            ok, msg = self.controller.verify_master(password)

        if ok:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Error", msg)
