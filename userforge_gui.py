"""
UserForge — GUI
----------------
Desktop GUI for generating candidate short usernames
(3-4 characters) for manual checking. 100% local/offline generation —
no network requests are made by this tool.

Run:
    python userforge_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser

from engine import generate_usernames, estimate_space, save_txt, save_json

# ---------- theme: deep purple / black ----------
BG = "#0a0710"               # near-black with a purple undertone
PANEL = "#150f24"            # dark purple-black panel
PANEL_2 = "#1d1530"          # slightly lighter panel for inputs/secondary
ACCENT = "#9d7bff"           # muted violet — main accent, easy on the eyes
ACCENT_2 = "#c9a8ff"         # soft lilac — secondary highlight
ACCENT_HOVER = "#b39bff"
TEXT = "#e6e1f5"             # warm off-white with violet tint
SUBTEXT = "#766e94"          # muted lavender-gray
LIST_BG = "#080611"          # almost black
BORDER = "#2a1f47"           # soft violet border, low contrast
GRADIENT_FROM = "#2a1659"    # deep purple
GRADIENT_TO = "#0a0710"      # fades to near-black

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_TAGLINE = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI", 10)
FONT_LABEL_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 11)
FONT_STAT = ("Segoe UI", 9)


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def _lerp_color(c1, c2, t):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex((
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    ))


class GradientHeader(tk.Canvas):
    """A horizontal-gradient header bar with title + tagline drawn on top."""

    def __init__(self, parent, height=110, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, bd=0, **kwargs)
        self._height = height
        self.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        if width <= 1:
            width = 760
        steps = 60
        for i in range(steps):
            t = i / steps
            color = _lerp_color(GRADIENT_FROM, GRADIENT_TO, t)
            x0 = width * (i / steps)
            x1 = width * ((i + 1) / steps)
            self.create_rectangle(x0, 0, x1, self._height, fill=color, outline=color)

        # subtle accent line at bottom
        self.create_rectangle(0, self._height - 2, width, self._height, fill=ACCENT, outline=ACCENT)

        self.create_text(28, 38, anchor="w", text="⚒  UserForge",
                          fill=TEXT, font=FONT_TITLE)
        self.create_text(30, 70, anchor="w",
                          text="Local candidate-username forge — offline, fast, precise.",
                          fill="#c9a8ff", font=FONT_TAGLINE)


class Card(tk.Frame):
    """A panel with rounded-corner illusion via padding + border, premium feel."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=PANEL, highlightbackground=BORDER,
                          highlightthickness=1, bd=0, **kwargs)


class UserForgeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UserForge")
        self.geometry("820x700")
        self.minsize(720, 600)
        self.configure(bg=BG)

        self._build_style()
        self._build_layout()
        self.current_results = []

    # ---------- ttk style ----------
    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)

        style.configure("TLabel", background=PANEL, foreground=TEXT, font=FONT_LABEL)
        style.configure("Sub.TLabel", background=BG, foreground=SUBTEXT, font=FONT_TAGLINE)
        style.configure("Stat.TLabel", background=BG, foreground=ACCENT_2, font=FONT_STAT)

        style.configure("Accent.TButton", background=ACCENT, foreground="#0a0710",
                         font=("Segoe UI", 11, "bold"), padding=10, borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

        style.configure("Secondary.TButton", background=PANEL_2, foreground=TEXT,
                         font=("Segoe UI", 9), padding=7, borderwidth=1)
        style.map("Secondary.TButton", background=[("active", BORDER)])

        style.configure("TEntry", fieldbackground=LIST_BG, foreground=TEXT,
                         insertcolor=TEXT, padding=7, borderwidth=0)
        style.configure("TCheckbutton", background=PANEL, foreground=TEXT, font=FONT_TAGLINE)
        style.map("TCheckbutton", background=[("active", PANEL)])
        style.configure("TRadiobutton", background=PANEL, foreground=TEXT, font=FONT_TAGLINE)
        style.map("TRadiobutton", background=[("active", PANEL)],
                  foreground=[("selected", ACCENT_2)])

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_2, foreground=SUBTEXT,
                         padding=(16, 8), font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#0a0710")])

    # ---------- Layout ----------
    def _build_layout(self):
        header = GradientHeader(self, bg=BG)
        header.pack(fill="x")

        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=22, pady=16)

        notebook = ttk.Notebook(body)
        notebook.pack(fill="both", expand=True)

        gen_tab = ttk.Frame(notebook, style="TFrame")
        about_tab = ttk.Frame(notebook, style="TFrame")
        notebook.add(gen_tab, text="  Generate  ")
        notebook.add(about_tab, text="  About  ")

        self._build_generate_tab(gen_tab)
        self._build_about_tab(about_tab)

    # ---------- Generate tab ----------
    def _build_generate_tab(self, parent):
        options = Card(parent)
        options.pack(fill="x", pady=(12, 10))

        grid = tk.Frame(options, bg=PANEL)
        grid.pack(fill="x", padx=18, pady=16)
        for col in range(4):
            grid.columnconfigure(col, weight=1)

        # Length
        ttk.Label(grid, text="LENGTH", font=FONT_LABEL_BOLD,
                  background=PANEL, foreground=ACCENT_2).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.length_var = tk.IntVar(value=3)
        lf = tk.Frame(grid, bg=PANEL)
        lf.grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(lf, text="3 characters", variable=self.length_var, value=3,
                         command=self._update_stats).pack(anchor="w")
        ttk.Radiobutton(lf, text="4 characters", variable=self.length_var, value=4,
                         command=self._update_stats).pack(anchor="w")

        # Mode
        ttk.Label(grid, text="CHARACTER SET", font=FONT_LABEL_BOLD,
                  background=PANEL, foreground=ACCENT_2).grid(row=0, column=1, sticky="w", pady=(0, 6))
        self.mode_var = tk.StringVar(value="letters")
        mf = tk.Frame(grid, bg=PANEL)
        mf.grid(row=1, column=1, sticky="w")
        for label, val in [("Letters", "letters"), ("Digits", "digits"), ("Mixed", "mixed")]:
            ttk.Radiobutton(mf, text=label, variable=self.mode_var, value=val,
                             command=self._update_stats).pack(anchor="w")

        # Style + amount
        ttk.Label(grid, text="STYLE", font=FONT_LABEL_BOLD,
                  background=PANEL, foreground=ACCENT_2).grid(row=0, column=2, sticky="w", pady=(0, 6))
        self.pronounceable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid, text="Pronounceable\n(letters only)",
                         variable=self.pronounceable_var,
                         command=self._update_stats).grid(row=1, column=2, sticky="w")

        ttk.Label(grid, text="AMOUNT", font=FONT_LABEL_BOLD,
                  background=PANEL, foreground=ACCENT_2).grid(row=0, column=3, sticky="w", pady=(0, 6))
        self.amount_var = tk.StringVar(value="100")
        vcmd = (self.register(self._validate_int), "%P")
        ttk.Entry(grid, textvariable=self.amount_var, width=12,
                  validate="key", validatecommand=vcmd).grid(row=1, column=3, sticky="w")

        # Filters
        filt_card = Card(parent)
        filt_card.pack(fill="x", pady=(0, 10))
        filt = tk.Frame(filt_card, bg=PANEL)
        filt.pack(fill="x", padx=18, pady=14)
        for col in range(4):
            filt.columnconfigure(col, weight=1)

        labels = ["Starts with", "Ends with", "Contains", "Exclude chars"]
        self.starts_var = tk.StringVar()
        self.ends_var = tk.StringVar()
        self.contains_var = tk.StringVar()
        self.exclude_var = tk.StringVar()
        vars_ = [self.starts_var, self.ends_var, self.contains_var, self.exclude_var]

        for i, (lbl, var) in enumerate(zip(labels, vars_)):
            ttk.Label(filt, text=lbl.upper(), font=("Segoe UI", 8, "bold"),
                      background=PANEL, foreground=SUBTEXT).grid(row=0, column=i, sticky="w")
            ttk.Entry(filt, textvariable=var, width=14).grid(row=1, column=i, sticky="we", padx=(0, 10))

        # Action row
        action_row = ttk.Frame(parent, style="TFrame")
        action_row.pack(fill="x", pady=(2, 10))
        ttk.Button(action_row, text="⚒  GENERATE", style="Accent.TButton",
                   command=self.on_generate).pack(side="left")
        self.stats_label = ttk.Label(action_row, text="", style="Stat.TLabel")
        self.stats_label.pack(side="left", padx=16)

        # Results list
        list_frame = tk.Frame(parent, bg=LIST_BG, highlightbackground=BORDER, highlightthickness=1)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            list_frame, bg=LIST_BG, fg=TEXT, font=FONT_MONO,
            selectbackground=ACCENT, selectforeground="#0a0710",
            borderwidth=0, highlightthickness=0, activestyle="none",
            yscrollcommand=scrollbar.set,
        )
        self.listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.config(command=self.listbox.yview)

        # Footer
        footer = ttk.Frame(parent, style="TFrame")
        footer.pack(fill="x")
        ttk.Button(footer, text="📋 Copy All", style="Secondary.TButton",
                   command=self.on_copy).pack(side="left")
        ttk.Button(footer, text="⬇ Export .txt", style="Secondary.TButton",
                   command=self.on_export_txt).pack(side="left", padx=8)
        ttk.Button(footer, text="⬇ Export .json", style="Secondary.TButton",
                   command=self.on_export_json).pack(side="left")
        ttk.Label(footer, text="Offline only — verify manually inside WhatsApp.",
                  style="Sub.TLabel").pack(side="right")

        self._update_stats()

    # ---------- About tab ----------
    def _build_about_tab(self, parent):
        card = Card(parent)
        card.pack(fill="both", expand=True, pady=12)
        inner = tk.Frame(card, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(inner, text="⚒ UserForge", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(inner, text="Local username-candidate generator",
                 bg=PANEL, fg=SUBTEXT, font=FONT_TAGLINE).pack(anchor="w", pady=(0, 18))

        points = [
            ("✓", "100% offline — no network requests, ever."),
            ("✓", "Generates unique 3 or 4 character combinations."),
            ("✓", "Pronounceable mode for natural-looking results."),
            ("✓", "Custom filters: starts/ends with, contains, exclude chars."),
            ("✓", "Export to .txt or .json, or copy straight to clipboard."),
            ("✓", "Also ships as a CLI (cli.py) for scripting / automation."),
            ("✗", "Does NOT check availability on WhatsApp or any platform."),
            ("✗", "Does NOT connect to any external server."),
        ]
        for mark, line in points:
            color = "#7dd3a8" if mark == "✓" else "#e07a7a"
            row = tk.Frame(inner, bg=PANEL)
            row.pack(anchor="w", pady=2, fill="x")
            tk.Label(row, text=mark, bg=PANEL, fg=color, font=FONT_LABEL_BOLD, width=2).pack(side="left")
            tk.Label(row, text=line, bg=PANEL, fg=TEXT, font=FONT_LABEL,
                     justify="left", wraplength=600, anchor="w").pack(side="left", fill="x")

        tk.Label(
            inner,
            text=("Availability must be verified manually, one at a time, inside the WhatsApp\n"
                  "app itself. This is by design — automated bulk checking against WhatsApp's\n"
                  "servers violates their Terms of Service and can be misused to track other\n"
                  "people's accounts."),
            bg=PANEL, fg=SUBTEXT, font=FONT_TAGLINE, justify="left",
        ).pack(anchor="w", pady=(14, 20))

        sep = tk.Frame(inner, bg=BORDER, height=1)
        sep.pack(fill="x", pady=(0, 18))

        tk.Label(inner, text="CREATOR", bg=PANEL, fg=ACCENT_2,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 8))

        links = [
            ("🔗  guns.lol/SayerSix", "https://guns.lol/SayerSix"),
            ("▶  YouTube — @sayersix-s", "https://www.youtube.com/@sayersix-s"),
            ("💬  Discord server", "https://discord.gg/isi"),
        ]
        for label, url in links:
            self._make_link(inner, label, url)

        discord_row = tk.Frame(inner, bg=PANEL)
        discord_row.pack(anchor="w", pady=(4, 0))
        tk.Label(discord_row, text="🪪", bg=PANEL, fg=TEXT, font=FONT_LABEL).pack(side="left")
        tk.Label(discord_row, text="  Discord: ", bg=PANEL, fg=SUBTEXT, font=FONT_LABEL).pack(side="left")
        tk.Label(discord_row, text="sayersix", bg=PANEL, fg=TEXT, font=FONT_LABEL_BOLD).pack(side="left")

    def _make_link(self, parent, label, url):
        lbl = tk.Label(parent, text=label, bg=PANEL, fg=ACCENT, font=FONT_LABEL, cursor="hand2")
        lbl.pack(anchor="w", pady=3)
        lbl.bind("<Button-1>", lambda e: webbrowser.open(url))
        lbl.bind("<Enter>", lambda e: lbl.config(fg=ACCENT_HOVER))
        lbl.bind("<Leave>", lambda e: lbl.config(fg=ACCENT))

    # ---------- Logic ----------
    @staticmethod
    def _validate_int(proposed):
        return proposed == "" or proposed.isdigit()

    def _update_stats(self):
        try:
            space = estimate_space(
                self.length_var.get(), self.mode_var.get(), self.pronounceable_var.get()
            )
            self.stats_label.config(text=f"★ {space:,} possible combinations in this search space")
        except Exception:
            self.stats_label.config(text="")

    def on_generate(self):
        try:
            amount = int(self.amount_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a positive integer.")
            return

        results = generate_usernames(
            amount=amount,
            length=self.length_var.get(),
            mode=self.mode_var.get(),
            pronounceable=self.pronounceable_var.get(),
            starts_with=self.starts_var.get(),
            ends_with=self.ends_var.get(),
            contains=self.contains_var.get(),
            exclude_chars=self.exclude_var.get(),
        )

        self.current_results = results
        self.listbox.delete(0, tk.END)
        for u in results:
            self.listbox.insert(tk.END, "@" + u)

        self._update_stats()
        self.stats_label.config(
            text=self.stats_label.cget("text") + f"   •   {len(results)} generated"
        )

    def on_copy(self):
        if not self.current_results:
            messagebox.showinfo("Nothing to copy", "Generate a list first.")
            return
        text = "\n".join("@" + u for u in self.current_results)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", f"{len(self.current_results)} usernames copied to clipboard.")

    def on_export_txt(self):
        if not self.current_results:
            messagebox.showinfo("Nothing to export", "Generate a list first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")])
        if path:
            save_txt(self.current_results, path)
            messagebox.showinfo("Exported", f"Saved to {path}")

    def on_export_json(self):
        if not self.current_results:
            messagebox.showinfo("Nothing to export", "Generate a list first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON file", "*.json")])
        if path:
            save_json(self.current_results, path)
            messagebox.showinfo("Exported", f"Saved to {path}")


if __name__ == "__main__":
    app = UserForgeApp()
    app.mainloop()
