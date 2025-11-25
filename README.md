# Jarvis - Office Automation Assistant

## Introduction
Jarvis is an office automation tool developed with Python. It is designed to help users automatically process Excel spreadsheets, organize folders, and batch rename files. Its goal is to reduce repetitive tasks and improve office efficiency.

## Features
* **Excel Automation**: Merge multiple Excel files with one click.
* **File Organization**: Automatically classify files into different folders based on file type.
* **Image Processing**: Batch resize images.
* **Easy to Use**: No complex configuration required; simply run and use.

## Requirements
Before using this tool, please ensure your computer has **Python 3.10** or higher installed. You will also need the following dependencies:

* numpy
* matplotlib
* opencv-python
* pillow

Alternatively, you can install all dependencies at once using the following command:
```shell
pip install -r requirements.txt

Usage
Step 1: Preparation
Ensure that the Excel files or images you want to process are located in the same directory as the script (or follow the specific instructions on the screen).

Step 2: Run the Program
Open your terminal or command prompt and run the following command:

Shell

python jarvis.py
Step 3: Select Function
Once started, the program will display a menu. Enter the corresponding number to select a function:

Merge Excel Files

Organize Folder

Exit

FAQ
Q: Why won't the program start? A: Please check if Python is correctly installed and added to your system PATH.

Q: I see an error "Module not found". A: You are likely missing some libraries. Please run pip install -r requirements.txt to fix it.

Changelog
v1.0: Initial release, including basic automation features.
