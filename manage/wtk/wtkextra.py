import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

def wtk_input_window(main_window, string_var, title, input_info, send_info):
    def send():
        string_var.set(input_box.get())
        input_window.destroy()

    input_window = tk.Toplevel(main_window)
    input_window.title(title)
    input_window.geometry("400x200")
    input_window.resizable(False, False)
    input_window.grab_set()

    input_info = tk.Label(input_window, text=input_info, font=("Cascadia Mono", 15, "bold"))
    input_info.grid(row=0, column=0, pady=40)

    input_box = tk.Entry(input_window, width=50, textvariable=string_var)
    input_box.grid(row=1, column=0, padx=20, ipady=3)

    send_button = tk.Button(input_window, text=send_info, height=1, width=10, command=send)
    send_button.grid(row=2, column=0, padx=20, pady=15, ipady=3)

    main_window.wait_window(input_window)

def wtk_message_with_timeout(message, title, type='info', timeout=2500):
    root = tk.Tk()
    root.withdraw()
    try:
        root.after(timeout, root.destroy)
        if type == 'info':
            messagebox.showinfo(title, message, master=root)
        elif type == 'warning':
            messagebox.showwarning(title, message, master=root)
        elif type == 'error':
            messagebox.showerror(title, message, master=root)
        else:
            print("[wtk]Unknown usage. Use type 'info' or 'warning' or 'error' not {}".format(type))
    except Exception as e:
        print('[wtk]Exception: {}'.format(e))
        pass

    if root is not None:
        try:
            root.destroy()
        except tk.TclError:
            pass


class DynamicRollingText(tk.Canvas):
    def __init__(self, master, text_lines, width=300, height=100, speed=1, delay=30, font=("Arial", 14), next_time_delay=0.1
                 , bg=None):
        super().__init__(master, width=width, height=height, highlightthickness=0)
        self.lines = text_lines
        self.speed = speed
        self.delay = delay
        self.next_time_delay = next_time_delay
        self.font = font
        self.text_items = []
        self.offset_y = 0
        self.config(bg=bg)

        self.create_text_items()

        self.after(self.delay, self.scroll)

    def create_text_items(self):
        self.text_items.clear()
        self.delete("all")
        line_height = self.font[1] + 8
        y = 0
        for line in self.lines * 2:
            item = self.create_text(10, y, anchor="nw", text=line, font=self.font, fill="black")
            self.text_items.append(item)
            y += line_height
        self.total_height = y

    def scroll(self):
        self.move("all", 0, -self.speed)
        self.offset_y += self.speed

        if self.offset_y >= self.total_height / 2:
            self.offset_y = 0
            time.sleep(self.next_time_delay)
            self.create_text_items()

        self.after(self.delay, self.scroll)

class WTKUnknownException(Exception):
    def __init__(self, message="Wtk exception.", value=None):
        super().__init__(message)
        self.value = value

    def __str__(self):
        if self.value is not None:
            return f"{self.args[0]}: {self.value}"
        return self.args[0]