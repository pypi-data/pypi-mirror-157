from distutils.command.build import build
import tkinter as tk
from tkinter import * 
from tkinter import ttk
from earth_api import *
from webbrowser import open as webopen
import webbrowser
import os
import sys

expr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../'))

if  expr_path not in sys.path:
    sys.path.insert(0, expr_path)
from test.manager import add_layer, add_graphic, patch_graphic, all_v1_api, all_latest_api


top = tk.Tk()

test_add_layer_btn = tk.Button(
    top, 
    text ="Test Add Layer", 
    command = add_layer)
test_add_layer_btn.pack()

test_add_graphic_btn = tk.Button(
    top, 
    text ="Test Add Graphic", 
    command = add_graphic)
test_add_graphic_btn.pack()

test_patch_graphic_btn = tk.Button(
    top, 
    text ="Test Add Graphic", 
    command = patch_graphic)
test_patch_graphic_btn.pack()

test_all_v1_api_btn = tk.Button(
    top, 
    text ="Test All V1 API", 
    command = all_v1_api)
test_all_v1_api_btn.pack()

test_all_latest_api_btn = tk.Button(
    top, 
    text ="Test All Latest API", 
    command = all_latest_api)
test_all_latest_api_btn.pack()



help_page_link = "https://devtopia.esri.com/runtime/arcgis-earth/wiki/Automation-API-Automated-QA-based-on-Python"

link = tk.Label(top, text='Click and Get More Information.', font=('Arial', 10, "underline"), foreground='blue')
link.pack()

def open_url(event):
    webbrowser.open(help_page_link, new=0)
link.bind("<Button-1>", open_url)


# 进入消息循环
top.mainloop()