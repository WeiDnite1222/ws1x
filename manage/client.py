from structure import SpaceNETManage
import customtkinter as ctk
from lang import LanguageUtil
import os
from ui import ServerTableList
import random
import string

root_dir = os.path.dirname(os.path.abspath(__file__))

class Manage(SpaceNETManage):
    def __init__(self):
        SpaceNETManage.__init__(self)
        self.root = ctk.CTk()

        # Language
        self.ln = LanguageUtil(os.path.join(root_dir, "languages"), "zh_TW")

        # Title
        self.root.title(self.ln("SpaceNET Manager > {}", "CLIENT"))

        # Layout
        self.user_hello_label = ctk.CTkLabel(self.root, text=self.ln("Hi, {}", "User"),
                                             font=("Helvetica", 25, "bold"), text_color="#ffffff")
        self.user_hello_label.pack(side="top", anchor="nw", padx=10, pady=10)

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, width=200)
        self.main_frame.pack(side="top", expand=True, fill="both", padx=10, pady=10)

        # > Server List
        self.server_list_frame = ctk.CTkFrame(self.main_frame)
        self.server_list_frame.pack(side="left", anchor="nw", padx=10, pady=10)

        self.server_list_info = ctk.CTkLabel(self.server_list_frame, text=self.ln("List of available servers"),
                                             font=("Helvetica", 15))
        self.server_list_info.pack(side="top", anchor="nw", padx=10, pady=2)

        self.server_list = ServerTableList(self.server_list_frame)
        self.server_list.pack(side="bottom", padx=10, pady=10, expand=True, fill="both")

        # > Settings Button
        self.settings_bin_frame = ctk.CTkFrame(self.main_frame)
        self.settings_bin_frame.pack(side="right", padx=10, pady=10, expand=True, fill="both")

        self.cloudflare_options_btn = ctk.CTkButton(self.settings_bin_frame, text=self.ln("Cloudflare Options"), height=35)
        self.cloudflare_options_btn.grid(row=0, column=0, padx=10, pady=10)

        self.server_service_btn = ctk.CTkButton(self.settings_bin_frame, text=self.ln("Server Options"), height=35)
        self.server_service_btn.grid(row=1, column=0, padx=10, pady=10)

        self.status_monitor = ctk.CTkButton(self.settings_bin_frame, text=self.ln("Status Monitor"), height=35)
        self.status_monitor.grid(row=2, column=0, padx=10, pady=10)

        self.settings_bin_frame.rowconfigure(0, weight=1)
        self.settings_bin_frame.rowconfigure(1, weight=1)
        self.settings_bin_frame.rowconfigure(2, weight=1)
        self.settings_bin_frame.rowconfigure(3, weight=1)
        self.settings_bin_frame.rowconfigure(4, weight=1)

        # Workspace Frame
        self.workspace_frame = ctk.CTkFrame(self.root)
        self.workspace_frame.pack(side="bottom", padx=10, pady=10, expand=True, fill="both")

        self.main()


    def main(self):
        self.load_server_data()
        self.root.mainloop()

    def load_server_data(self):
        for i in range(0, 10) :
            name = random.choice(string.ascii_lowercase*5)
            ip = self.ln("Click to view the IP")
            read_ip = str(f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}")

            self.server_list.add_server(name, ip, "在線", read_ip)