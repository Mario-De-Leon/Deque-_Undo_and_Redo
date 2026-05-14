import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from editor_history import EditorHistory

COLORS = {
    "bg":           "#0f1117",
    "surface":      "#1a1d27",
    "surface2":     "#222535",
    "border":       "#2e3248",
    "accent":       "#7c6af7",        # violeta
    "accent2":      "#4ecdc4",        # teal
    "accent_undo":  "#f7a26a",        # naranja
    "accent_redo":  "#6af7a2",        # verde
    "danger":       "#f76a6a",
    "text":         "#e8eaf0",
    "text_muted":   "#6b7280",
    "text_label":   "#a0a8c0",
    "highlight":    "#7c6af720",
}

class HistoryPanel(tk.Frame):

    def __init__(self, master, title: str, color: str, **kw):
        super().__init__(master, bg=COLORS["surface"], **kw)
        self._color = color

        # Cabecera
        header = tk.Frame(self, bg=COLORS["surface2"], pady=8)
        header.pack(fill="x")
        tk.Label(
            header, text=title, bg=COLORS["surface2"],
            fg=color, font=("Courier New", 10, "bold"),
        ).pack(padx=12)

        # Lista con scroll
        frame = tk.Frame(self, bg=COLORS["surface"])
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        self._listbox = tk.Listbox(
            frame,
            bg=COLORS["surface"],
            fg=COLORS["text"],
            selectbackground=COLORS["surface2"],
            selectforeground=color,
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
            font=("Courier New", 8),
            relief="flat",
        )
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)

    def refresh(self, actions: list) -> None:
        self._listbox.delete(0, "end")
        for i, action in enumerate(actions):
            marker = "▶" if i == 0 else " "
            self._listbox.insert("end", f"{marker} {action}")
        if actions:
            self._listbox.itemconfig(0, fg=self._color)


class EditorApp(tk.Tk):
    INITIAL_TEXT = "¡Bienvenido al Editor con Undo/Redo!\n\nEscribe aquí tu texto..."

    def __init__(self):
        super().__init__()
        self._history = EditorHistory(self.INITIAL_TEXT)
        self._setup_window()
        self._build_ui()
        self._refresh_all()

    # ─────────────────── configuración de ventana ────────────────────────────

    def _setup_window(self):
        self.title("Editor con Undo / Redo  —  Deque")
        self.configure(bg=COLORS["bg"])
        self.geometry("1100x700")
        self.minsize(900, 580)
        # Intentar centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1100) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")

    # ─────────────────── construcción de la UI ───────────────────────────────

    def _build_ui(self):
        self._build_header()

        # Contenedor central dividido en 3 columnas
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        body.columnconfigure(0, weight=1, minsize=180)
        body.columnconfigure(1, weight=3)
        body.columnconfigure(2, weight=1, minsize=180)
        body.rowconfigure(0, weight=1)

        # Panel izquierdo: historial undo
        self._panel_undo = HistoryPanel(
            body, "⟵  HISTORIAL UNDO", COLORS["accent_undo"]
        )
        self._panel_undo.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Panel central: editor
        self._build_editor(body)

        # Panel derecho: historial redo
        self._panel_redo = HistoryPanel(
            body, "HISTORIAL REDO  ⟶", COLORS["accent_redo"]
        )
        self._panel_redo.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        self._build_status_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["surface"], pady=14)
        header.pack(fill="x", padx=0)

        # Logo / título
        title_frame = tk.Frame(header, bg=COLORS["surface"])
        title_frame.pack(side="left", padx=20)
        tk.Label(
            title_frame, text="◈", bg=COLORS["surface"],
            fg=COLORS["accent"], font=("Courier New", 22, "bold"),
        ).pack(side="left", padx=(0, 8))
        tk.Label(
            title_frame, text="EDITOR", bg=COLORS["surface"],
            fg=COLORS["text"], font=("Courier New", 18, "bold"),
        ).pack(side="left")
        tk.Label(
            title_frame, text=" UNDO/REDO", bg=COLORS["surface"],
            fg=COLORS["accent"], font=("Courier New", 18),
        ).pack(side="left")

        # Botones de acción principal
        btn_frame = tk.Frame(header, bg=COLORS["surface"])
        btn_frame.pack(side="right", padx=20)

        self._btn_undo = self._make_button(
            btn_frame, "⟵  UNDO  (Ctrl+Z)", COLORS["accent_undo"], self._do_undo
        )
        self._btn_undo.pack(side="left", padx=4)

        self._btn_redo = self._make_button(
            btn_frame, "REDO  ⟶  (Ctrl+Y)", COLORS["accent_redo"], self._do_redo
        )
        self._btn_redo.pack(side="left", padx=4)

        self._make_button(
            btn_frame, "↺  RESET", COLORS["danger"], self._do_reset, small=True
        ).pack(side="left", padx=(12, 0))

        # Atajos de teclado
        self.bind("<Control-z>", lambda e: self._do_undo())
        self.bind("<Control-y>", lambda e: self._do_redo())
        self.bind("<Control-Z>", lambda e: self._do_undo())
        self.bind("<Control-Y>", lambda e: self._do_redo())

    def _build_editor(self, parent):
        center = tk.Frame(parent, bg=COLORS["bg"])
        center.grid(row=0, column=1, sticky="nsew")
        center.rowconfigure(2, weight=1)
        center.columnconfigure(0, weight=1)

        # ── Formulario de nueva acción ──
        form = tk.Frame(center, bg=COLORS["surface"], pady=10)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        form.columnconfigure(1, weight=1)

        tk.Label(
            form, text="Descripción:", bg=COLORS["surface"],
            fg=COLORS["text_label"], font=("Courier New", 9),
        ).grid(row=0, column=0, padx=(14, 6), pady=4, sticky="w")

        self._desc_var = tk.StringVar()
        desc_entry = tk.Entry(
            form, textvariable=self._desc_var,
            bg=COLORS["surface2"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat", font=("Courier New", 10),
            highlightthickness=1, highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        desc_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        tk.Label(
            form, text="Tipo:", bg=COLORS["surface"],
            fg=COLORS["text_label"], font=("Courier New", 9),
        ).grid(row=1, column=0, padx=(14, 6), pady=4, sticky="w")

        type_row = tk.Frame(form, bg=COLORS["surface"])
        type_row.grid(row=1, column=1, sticky="w", padx=6)

        self._type_var = tk.StringVar(value="edit")
        for atype, label in [("edit", "✏ Editar"), ("insert", "＋ Insertar"),
                              ("delete", "✕ Eliminar"), ("format", "◐ Formato")]:
            rb = tk.Radiobutton(
                type_row, text=label, variable=self._type_var, value=atype,
                bg=COLORS["surface"], fg=COLORS["text_label"],
                selectcolor=COLORS["surface2"],
                activebackground=COLORS["surface"],
                activeforeground=COLORS["accent"],
                font=("Courier New", 8),
            )
            rb.pack(side="left", padx=4)

        self._make_button(
            form, "  ＋  REGISTRAR ACCIÓN  ", COLORS["accent"], self._do_add,
        ).grid(row=2, column=0, columnspan=2, pady=(6, 2), padx=14)
        desc_entry.bind("<Return>", lambda e: self._do_add())

        # ── Área de texto del editor ──
        editor_label = tk.Frame(center, bg=COLORS["bg"])
        editor_label.grid(row=1, column=0, sticky="ew")
        tk.Label(
            editor_label, text="CONTENIDO DEL EDITOR",
            bg=COLORS["bg"], fg=COLORS["text_muted"],
            font=("Courier New", 8, "bold"),
        ).pack(side="left", padx=2, pady=(4, 2))

        text_frame = tk.Frame(center, bg=COLORS["border"], padx=1, pady=1)
        text_frame.grid(row=2, column=0, sticky="nsew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self._text = tk.Text(
            text_frame,
            bg=COLORS["surface"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["surface2"],
            relief="flat", wrap="word",
            font=("Courier New", 11),
            padx=14, pady=12,
            spacing1=2, spacing3=2,
        )
        text_scroll = tk.Scrollbar(text_frame, command=self._text.yview)
        self._text.configure(yscrollcommand=text_scroll.set)
        text_scroll.grid(row=0, column=1, sticky="ns")
        self._text.grid(row=0, column=0, sticky="nsew")

        self._text.insert("1.0", self.INITIAL_TEXT)

        # Botón "Aplicar texto"
        apply_row = tk.Frame(center, bg=COLORS["bg"])
        apply_row.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        self._make_button(
            apply_row, "↳ Usar texto del editor como nueva acción",
            COLORS["accent2"], self._do_apply_text, small=True,
        ).pack(side="left")
        tk.Label(
            apply_row, text="  (edita el texto y registra el cambio)",
            bg=COLORS["bg"], fg=COLORS["text_muted"], font=("Courier New", 8),
        ).pack(side="left")

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=COLORS["surface2"], pady=6)
        bar.pack(fill="x", side="bottom")

        self._status_var = tk.StringVar(value="Listo.")
        self._status_label = tk.Label(
            bar, textvariable=self._status_var,
            bg=COLORS["surface2"], fg=COLORS["text_muted"],
            font=("Courier New", 8),
        )
        self._status_label.pack(side="left", padx=14)

        self._counts_var = tk.StringVar()
        tk.Label(
            bar, textvariable=self._counts_var,
            bg=COLORS["surface2"], fg=COLORS["text_muted"],
            font=("Courier New", 8),
        ).pack(side="right", padx=14)

    # ─────────────────── helpers UI ──────────────────────────────────────────

    def _make_button(self, parent, text, color, command, small=False):
        fsize = 8 if small else 9
        btn = tk.Button(
            parent, text=text, command=command,
            bg=COLORS["surface2"], fg=color,
            activebackground=COLORS["surface"],
            activeforeground=color,
            relief="flat", cursor="hand2",
            font=("Courier New", fsize, "bold"),
            padx=10 if small else 14,
            pady=4 if small else 7,
            borderwidth=1,
        )
        btn.bind("<Enter>", lambda e: btn.configure(bg=COLORS["surface"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=COLORS["surface2"]))
        return btn

    # ─────────────────── acciones ────────────────────────────────────────────

    def _do_add(self):
        desc = self._desc_var.get().strip()
        new_state = self._text.get("1.0", "end-1c")
        atype = self._type_var.get()

        # FIX: única validación necesaria es descripción vacía.
        # Se eliminó el bloqueo por "sin cambio de estado", que impedía
        # registrar acciones descriptivas cuando el texto no había cambiado.
        if not desc:
            self._flash_status(
                "⚠  Escribe una descripción antes de registrar.",
                COLORS["danger"],
            )
            return

        try:
            action = self._history.add_action(desc, new_state, atype)
            self._desc_var.set("")
            self._flash_status(
                f"✔  Acción registrada: {action.description!r}",
                COLORS["accent_redo"],
            )
        except ValueError as e:
            self._flash_status(f"⚠  {e}", COLORS["danger"])

        self._refresh_all()

    def _do_apply_text(self):
        """Toma el texto actual del widget y lo registra como acción."""
        desc = self._desc_var.get().strip() or "Edición directa del texto"
        new_state = self._text.get("1.0", "end-1c")
        atype = self._type_var.get()
        try:
            self._history.add_action(desc, new_state, atype)
            self._desc_var.set("")
            self._flash_status("✔  Texto aplicado como nueva acción.", COLORS["accent_redo"])
        except ValueError as e:
            self._flash_status(f"⚠  {e}", COLORS["danger"])
        self._refresh_all()

    def _do_undo(self):
        action = self._history.undo()
        if action is None:
            self._flash_status("⚠  No hay acciones para deshacer.", COLORS["accent_undo"])
        else:
            self._flash_status(f"↩  Deshecho: {action.description!r}", COLORS["accent_undo"])
        self._refresh_all()

    def _do_redo(self):
        action = self._history.redo()
        if action is None:
            self._flash_status("⚠  No hay acciones para rehacer.", COLORS["accent_redo"])
        else:
            self._flash_status(f"↪  Rehecho: {action.description!r}", COLORS["accent_redo"])
        self._refresh_all()

    def _do_reset(self):
        if messagebox.askyesno(
            "Confirmar reset",
            "¿Deseas reiniciar el editor? Se perderá todo el historial.",
            parent=self,
        ):
            self._history.reset(self.INITIAL_TEXT)
            self._refresh_all()
            self._flash_status("↺  Editor reiniciado.", COLORS["danger"])

    # ─────────────────── actualización de UI ─────────────────────────────────

    def _refresh_all(self):
        """Sincroniza toda la UI con el estado actual del historial."""
        # Texto del editor
        self._text.delete("1.0", "end")
        self._text.insert("1.0", self._history.current_state)

        # Paneles de historial
        undo_items = [str(a) for a in self._history.get_undo_history()]
        redo_items = [str(a) for a in self._history.get_redo_history()]
        self._panel_undo.refresh(undo_items)
        self._panel_redo.refresh(redo_items)

        # Estado de botones
        undo_state = "normal" if self._history.can_undo else "disabled"
        redo_state = "normal" if self._history.can_redo else "disabled"
        self._btn_undo.configure(state=undo_state)
        self._btn_redo.configure(state=redo_state)

        # Contador
        self._counts_var.set(
            f"Undo: {len(undo_items)}  |  Redo: {len(redo_items)}"
        )

    def _flash_status(self, msg: str, color: str = COLORS["text_muted"]):
        """Muestra un mensaje en la barra de estado con el color indicado."""
        self._status_var.set(msg)
        self._status_label.configure(fg=color)
        self.after(3500, lambda: (
            self._status_var.set("Listo."),
            self._status_label.configure(fg=COLORS["text_muted"]),
        ))


if __name__ == "__main__":
    app = EditorApp()
    app.mainloop()