import PyInstaller.__main__
import shutil
import os

# 1. Run the fast build (Excluding heavy data)
PyInstaller.__main__.run([
    'main.py',
    '--onedir',
    '--noconsole',
    '--name=HindiBengaliBridge',
    '--contents-directory=_internal',
    '--collect-submodules=vosk',
    '--collect-all=customtkinter',
    '--exclude-module=PyQt5',
    '--exclude-module=tkinter.test',
    '--noupx',                     
])

print("--- Build Complete! ---")
