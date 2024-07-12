import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

# Global variables
data = None
columns = []
search_column_vars = []  # List to store search column variables

# Function to load CSV file
def load_csv():
    global data, columns
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        data = pd.read_csv(file_path)
        columns = data.columns.tolist()
        column_list.set(columns)
        
        # Populate columns in search option menu
        update_search_column_menus()
        
        column_listbox.select_set(0, tk.END)
        update_status(f"Loaded CSV file: {file_path}")
    else:
        update_status("No file selected.")

# Function to update all search column menus
def update_search_column_menus():
    for var in search_column_vars:
        var.set('')
    for row in search_rows:
        row.populate_column_menu()

# Function to select output folder
def select_output_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder_var.set(folder_path)
        update_status(f"Selected output folder: {folder_path}")

# Function to add a new keyword search row
def add_search_row():
    search_rows.append(SearchRow())
    update_search_rows()

# Function to update the display of search rows
def update_search_rows():
    for row in search_rows:
        row.frame.pack_forget()
    for idx, row in enumerate(search_rows):
        row.frame.pack(pady=5)
        row.index_label.config(text=f"Search {idx + 1}:")

# Function to remove the last search row
def remove_search_row():
    if search_rows:
        search_rows.pop()
        update_search_rows()

# Function to apply filter
def apply_filter():
    selected_columns = [column_listbox.get(i) for i in column_listbox.curselection()]
    output_folder = output_folder_var.get()
    output_filename = output_filename_var.get()
    
    if not selected_columns or not output_folder or not output_filename:
        messagebox.showwarning("Input Error", "Please select columns, select an output folder, and enter a filename.")
        return
    
    filtered_data = data[selected_columns]
    
    for row in search_rows:
        search_column = row.column_var.get()
        keywords = row.keyword_var.get().split(',')
        condition = row.condition_var.get()
        
        if not search_column or not keywords:
            continue
        
        if search_column not in filtered_data.columns:
            messagebox.showwarning("Column Error", f"Column '{search_column}' does not exist in the filtered data.")
            continue
        
        try:
            if condition == "contains":
                for keyword in keywords:
                    keyword = keyword.strip()
                    filtered_data = filtered_data[filtered_data[search_column].str.contains(keyword, na=False)]
            else:
                for keyword in keywords:
                    keyword = keyword.strip()
                    filtered_data = filtered_data[~filtered_data[search_column].str.contains(keyword, na=False)]
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while filtering: {str(e)}")
            return
    
    output_file_path = os.path.join(output_folder, f"{output_filename}.csv")
    
    if os.path.exists(output_file_path):
        # File already exists, ask user for action
        result = messagebox.askquestion("File Exists", "File already exists. Do you want to overwrite it?", icon='warning')
        if result == 'yes':
            # User chose to overwrite
            pass  # Proceed with saving
        else:
            # User chose not to overwrite, ask for new filename
            new_filename = filedialog.asksaveasfilename(initialdir=output_folder,
                                                       filetypes=[("CSV files", "*.csv")],
                                                       defaultextension=".csv")
            if new_filename:
                output_file_path = new_filename
            else:
                return  # Cancelled by user
    
    try:
        filtered_data.to_csv(output_file_path, index=False)
        update_status(f"Filtered data saved to: {output_file_path}")
    except PermissionError:
        messagebox.showerror("Permission Error", "Permission denied. Please choose a different output folder.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Function to update status label
def update_status(message):
    status_label.config(text=message)

# Class to represent a search row
class SearchRow:
    def __init__(self):
        self.frame = tk.Frame(search_frame)
        self.index_label = tk.Label(self.frame, text="Search 1:")
        self.index_label.grid(row=0, column=0, padx=5)
        
        self.column_var = tk.StringVar()
        self.column_menu = tk.OptionMenu(self.frame, self.column_var, "")
        self.column_menu.grid(row=0, column=1, padx=5)
        search_column_vars.append(self.column_var)  # Store the variable for later use
        self.populate_column_menu()
        
        self.keyword_var = tk.StringVar()
        self.keyword_entry = tk.Entry(self.frame, textvariable=self.keyword_var)
        self.keyword_entry.grid(row=0, column=2, padx=5)
        
        self.condition_var = tk.StringVar(value="contains")
        self.condition_menu = tk.OptionMenu(self.frame, self.condition_var, "contains", "does not contain")
        self.condition_menu.grid(row=0, column=3, padx=5)
    
    def populate_column_menu(self):
        self.column_menu['menu'].delete(0, 'end')
        for column in columns:
            self.column_menu['menu'].add_command(label=column, command=tk._setit(self.column_var, column))

# Setting up the GUI
root = tk.Tk()
root.title("CSV Filter Tool")

# Load CSV button
load_button = tk.Button(root, text="Load CSV", command=load_csv)
load_button.pack(pady=5)

# Column selection listbox
column_list = tk.Variable(value=[])
column_listbox = tk.Listbox(root, listvariable=column_list, selectmode=tk.MULTIPLE, height=10)
column_listbox.pack(pady=5)

# Search frame
search_frame = tk.Frame(root)
search_frame.pack(pady=5)

# Initial search row
search_rows = []
add_search_row()  # Add the initial search row when starting the GUI

# Add and remove buttons for search rows
add_button = tk.Button(root, text="Add Search", command=add_search_row)
add_button.pack(pady=5)

remove_button = tk.Button(root, text="Remove Last Search", command=remove_search_row)
remove_button.pack(pady=5)

# Output folder selection
output_frame = tk.Frame(root)
output_frame.pack(pady=5)

tk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, padx=5)
output_folder_var = tk.StringVar()
output_folder_entry = tk.Entry(output_frame, textvariable=output_folder_var, width=50)
output_folder_entry.grid(row=0, column=1, padx=5)
output_folder_button = tk.Button(output_frame, text="Browse", command=select_output_folder)
output_folder_button.grid(row=0, column=2, padx=5)

# Output filename
tk.Label(output_frame, text="Output Filename:").grid(row=1, column=0, padx=5)
output_filename_var = tk.StringVar()
output_filename_entry = tk.Entry(output_frame, textvariable=output_filename_var, width=50)
output_filename_entry.grid(row=1, column=1, padx=5)

# Apply filter button
apply_button = tk.Button(root, text="Apply Filter", command=apply_filter)
apply_button.pack(pady=5)

# Status label
status_label = tk.Label(root, text="No file loaded.")
status_label.pack(pady=5)

# Main loop
root.mainloop()
