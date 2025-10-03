import datetime
import customtkinter as ctk
import tkinter as tk
import uuid

class ServerTableList(ctk.CTkFrame):
    def __init__(self, parent, width=480, height=360, corner_radius=10):
        super().__init__(parent, width=width, height=height, corner_radius=corner_radius)
        self.server_list = []

        self.info_frame = ctk.CTkFrame(self,)

        self.server_table = ctk.CTkScrollableFrame(self, width=480, height=360)
        self.server_table.pack(fill="both", expand=True)


    def add_server(self, server_name, ip, server_status, real_server_ip):
        new_uuid = uuid.uuid4()
        server_frame = ctk.CTkFrame(self.server_table, corner_radius=8, border_width=1)
        server_frame.pack(fill="x", padx=8, pady=6)

        server_title = ctk.CTkLabel(server_frame, text=server_name, width=120, anchor="w")
        server_ip = ctk.CTkLabel(server_frame, text=ip, width=120, anchor="w")
        server_status = ctk.CTkLabel(server_frame, text=server_status, width=120, anchor="w")

        server_frame.check_var = tk.BooleanVar(value=False)

        server_checkbox = ctk.CTkCheckBox(server_frame, width=120, variable=server_frame.check_var, text="")

        server_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        server_ip.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        server_status.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        server_checkbox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        server_ip.bind("<Button-1>", lambda event: self.display_real_ip(event, new_uuid))

        server_frame.grid_columnconfigure(0, weight=1)
        server_frame.grid_columnconfigure(1, weight=1)
        server_frame.grid_columnconfigure(2, weight=1)
        server_frame.grid_columnconfigure(3, weight=1)

        self.server_list.append({"widget": server_frame,
                                 "name": server_name,
                                 "ip": real_server_ip,
                                 "fake_ip": ip,
                                 "status": server_status,
                                 "uuid": new_uuid,
                                 "ip_display": False})

    def display_real_ip(self, event, current_uuid):
       for server in self.server_list:
           if server["uuid"] == current_uuid:
               try:
                   if server['ip_display'] is not True:
                       event.widget.configure(text=server["ip"])
                       server['ip_display'] = True
                   else:
                       event.widget.configure(text=server["fake_ip"])
                       server['ip_display'] = False
                   break
               except tk.TclError:
                   pass


class ServerTerminalTable(ctk.CTkFrame):
    def __init__(self, parent, width=480, height=360, corner_radius=10):
        super().__init__(parent, width=width, height=height, corner_radius=corner_radius)
        self.server_list = []

        self.info_frame = ctk.CTkFrame(self,)

        self.server_table = ctk.CTkScrollableFrame(self, width=480, height=360)
        self.server_table.pack(fill="both", expand=True)


    def add_message(self, title, message):
        message_frame = ctk.CTkFrame(self.server_table, corner_radius=8)
        message_frame.pack(fill="x", padx=1, pady=1)

        current_datetime = datetime.datetime.now()

        server_log_date = ctk.CTkLabel(message_frame, text=current_datetime.strftime("%Y-%m-%d %H:%M:%S"), width=120, anchor="w")
        server_title = ctk.CTkLabel(message_frame, text=title, width=120, anchor="w")
        server_message = ctk.CTkLabel(message_frame, text=self.line_break(message), width=120, anchor="w")

        server_log_date.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        server_title.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        server_message.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        message_frame.grid_columnconfigure(0, weight=1)
        message_frame.grid_columnconfigure(1, weight=1)
        message_frame.grid_columnconfigure(2, weight=1)

        self.server_list.append(message_frame)

    @staticmethod
    def line_break(text):
        message = ""
        part = ""
        index = 0
        for char in text:
            if char == "\n":
                continue

            if index == 10:
                index = 0
                message += part + "\n"
                part = ""

            part += text[index]
            index += 1

        return message

