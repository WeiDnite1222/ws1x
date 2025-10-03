import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
from tkinter import messagebox

class ModernMessageBox(ctk.CTkToplevel):
    def __init__(self, master, title, message):
        ctk.CTkToplevel.__init__(self, master)
        self.title(title)
        self.geometry("350x200")
        self.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", bg_color="#1a1a1a", height=140)
        self.main_frame.pack(fill="both", expand="yes", anchor="n")

        self.footer_frame = ctk.CTkLabel(self, height=60, fg_color="#303030", bg_color="#303030", text="")
        self.footer_frame.pack(fill="x", expand="yes", anchor="s")

class WtkSimpleTableList(ctk.CTkScrollableFrame):
    def __init__(self, parent, width=480, height=360, corner_radius=10):
        super().__init__(parent, width=width, height=height, corner_radius=corner_radius)
        self.items = []

    def add_item(self, item_title, info_a, info_b):
        item_frame = ctk.CTkFrame(self, corner_radius=8, border_width=1)
        item_frame.pack(fill="x", padx=8, pady=6)

        lbl1 = ctk.CTkLabel(item_frame, text=item_title, width=120, anchor="w")
        lbl2 = ctk.CTkLabel(item_frame, text=info_a, width=120, anchor="w")
        lbl3 = ctk.CTkLabel(item_frame, text=info_b, width=120, anchor="w")

        lbl1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        lbl2.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        lbl3.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        item_frame.grid_columnconfigure(0, weight=1)
        item_frame.grid_columnconfigure(1, weight=1)
        item_frame.grid_columnconfigure(2, weight=1)

        self.items.append(item_frame)