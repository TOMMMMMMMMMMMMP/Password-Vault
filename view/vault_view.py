import tkinter as tk
from tkinter import ttk, messagebox


class VaultView(tk.Tk):
    """Main vault screen — list, search, add, edit, delete credentials."""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Password Vault")
        self.geometry("750x520")
        self.resizable(False, False)
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        self.configure(padx=16, pady=16)

        # Top bar
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="🔐 Password Vault",
                  font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(top, text="Export",
                   command=self._on_export).pack(side="right", padx=(6, 0))
        ttk.Button(top, text="+ Add",
                   command=self._on_add).pack(side="right")

        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search())
        ttk.Entry(search_frame, textvariable=self.search_var,
                  width=40).pack(side="left")
        ttk.Label(search_frame, text="  Search by site or username",
                  foreground="gray").pack(side="left")

        # Table
        cols = ("ID", "Site", "Username", "Password", "Notes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        self.tree.heading("ID",       text="ID")
        self.tree.heading("Site",     text="Site")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.heading("Notes",    text="Notes")
        self.tree.column("ID",       width=40,  anchor="center")
        self.tree.column("Site",     width=160)
        self.tree.column("Username", width=160)
        self.tree.column("Password", width=130)
        self.tree.column("Notes",    width=200)
        self.tree.pack(fill="both", expand=True)

        # Action buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_frame, text="👁 Show Password",
                   command=self._on_show_password).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="✏ Edit",
                   command=self._on_edit).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="🗑 Delete",
                   command=self._on_delete).pack(side="left")

    # ── Data ─────────────────────────────────────────────────────────────────

    def _refresh(self, creds=None) -> None:
        """Reload the table with fresh data."""
        self.tree.delete(*self.tree.get_children())
        if creds is None:
            creds = self.controller.get_all()
        for c in creds:
            self.tree.insert("", "end", values=(
                c.id, c.site, c.username, "••••••••", c.notes
            ))

    def _on_search(self) -> None:
        keyword = self.search_var.get().strip()
        if keyword:
            creds = self.controller.search(keyword)
        else:
            creds = self.controller.get_all()
        self._refresh(creds)

    def _get_selected_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry.")
            return None
        return int(self.tree.item(selected[0])["values"][0])

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_show_password(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an entry.")
            return
        values = self.tree.item(selected[0])["values"]
        cred_id = int(values[0])
        creds = self.controller.get_all()
        for c in creds:
            if c.id == cred_id:
                messagebox.showinfo("Password", f"Password for {c.site}:\n\n{c.password}")
                return

    def _on_add(self) -> None:
        self._open_form()

    def _on_edit(self) -> None:
        cred_id = self._get_selected_id()
        if cred_id is None:
            return
        creds = self.controller.get_all()
        for c in creds:
            if c.id == cred_id:
                self._open_form(c)
                return

    def _on_delete(self) -> None:
        cred_id = self._get_selected_id()
        if cred_id is None:
            return
        if not messagebox.askyesno("Confirm", "Delete this credential?"):
            return
        ok, msg = self.controller.delete(cred_id)
        if ok:
            self._refresh()
        else:
            messagebox.showerror("Error", msg)

    def _on_export(self) -> None:
        ok, msg = self.controller.export_vault()
        if ok:
            messagebox.showinfo("Export", msg)
        else:
            messagebox.showerror("Error", msg)

    def _open_form(self, cred=None) -> None:
        """Open add/edit form in a popup window."""
        win = tk.Toplevel(self)
        win.title("Edit Credential" if cred else "Add Credential")
        win.geometry("400x380")
        win.resizable(False, False)
        win.configure(padx=20, pady=20)

        fields = {}
        for label in ("Site", "Username", "Password", "Notes"):
            ttk.Label(win, text=label).pack(anchor="w")
            var = tk.StringVar()
            if cred:
                mapping = {
                    "Site": cred.site, "Username": cred.username,
                    "Password": cred.password, "Notes": cred.notes
                }
                var.set(mapping[label])
            entry = ttk.Entry(win, textvariable=var, width=40,
                              show="*" if label == "Password" else "")
            entry.pack(pady=(2, 10))
            fields[label] = var

        # Generate password button
        def generate():
            fields["Password"].set(self.controller.generate_password())

        ttk.Button(win, text="⚡ Generate Password",
                   command=generate).pack(pady=(0, 10))

        def on_save():
            site     = fields["Site"].get()
            username = fields["Username"].get()
            password = fields["Password"].get()
            notes    = fields["Notes"].get()

            if cred:
                ok, msg = self.controller.update(cred.id, site, username, password, notes)
            else:
                ok, msg = self.controller.add(site, username, password, notes)

            if ok:
                self._refresh()
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        ttk.Button(win, text="Save", command=on_save).pack()
