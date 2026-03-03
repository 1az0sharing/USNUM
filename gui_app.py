import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import threading
from us_phone_generator import USPhoneNumberGenerator
import os

class PhoneGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("US Phone Number Generator")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        # Set style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="US Phone Number Generator", 
                         font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # State selection
        ttk.Label(main_frame, text="Select State:", font=("Helvetica", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.state_var = tk.StringVar()
        states = USPhoneNumberGenerator.get_states()
        state_combo = ttk.Combobox(main_frame, textvariable=self.state_var, 
                                   values=states, state="readonly", width=35)
        state_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Count input
        ttk.Label(main_frame, text="Number of Entries:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.StringVar(value="100")
        count_entry = ttk.Entry(main_frame, textvariable=self.count_var, width=35)
        count_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ttk.Button(btn_frame, text="Generate Numbers", 
                  command=self.generate_numbers).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to CSV", 
                  command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", 
                  command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="", font=("Helvetica", 10))
        self.progress_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Text display area
        ttk.Label(main_frame, text="Generated Numbers:", font=("Helvetica", 11)).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, height=25, width=80, wrap=tk.WORD)
        self.text_area.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.generated_numbers = []
        self.selected_state = None
    
    def generate_numbers(self):
        state = self.state_var.get()
        if not state:
            messagebox.showerror("Error", "Please select a state")
            return
        
        try:
            count = int(self.count_var.get())
            if count <= 0:
                messagebox.showerror("Error", "Please enter a positive number")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number format")
            return
        
        # Disable button and show progress
        self.progress_label.config(text=f"Generating {count} numbers for {state}...")
        self.root.update()
        
        # Run generation in a separate thread to prevent freezing
        def generate():
            try:
                self.generated_numbers = USPhoneNumberGenerator.generate_numbers(state, count)
                self.selected_state = state
                
                # Format output
                output = f"Generated {len(self.generated_numbers)} phone numbers for {state}\n"
                output += "=" * 60 + "\n\n"
                
                for i, num in enumerate(self.generated_numbers, 1):
                    formatted = f"{num[:3]}-{num[3:6]}-{num[6:]}"
                    output += f"{i}. {formatted}\n"
                    if i % 50 == 0:  # Add a blank line every 50 numbers
                        output += "\n"
                
                self.text_area.config(state=tk.NORMAL)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, output)
                self.text_area.config(state=tk.NORMAL)
                
                self.progress_label.config(text=f"✓ Generated {len(self.generated_numbers)} numbers successfully")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.progress_label.config(text="Error generating numbers")
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
    
    def save_to_csv(self):
        if not self.generated_numbers:
            messagebox.showerror("Error", "No numbers to save. Generate numbers first!")
            return
        
        if not self.selected_state:
            messagebox.showerror("Error", "No state selected")
            return
        
        # Ask user for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"phone_numbers_{self.selected_state}.csv"
        )
        
        if not file_path:
            return
        
        try:
            csv_content = USPhoneNumberGenerator.export_to_csv(
                self.selected_state, 
                self.generated_numbers,
                os.path.basename(file_path)
            )
            
            with open(file_path, 'w', newline='') as f:
                f.write(csv_content)
            
            messagebox.showinfo("Success", f"File saved successfully!\n{file_path}")
            self.progress_label.config(text=f"✓ Saved {len(self.generated_numbers)} numbers to CSV")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.generated_numbers = []
        self.selected_state = None
        self.progress_label.config(text="")


def main():
    root = tk.Tk()
    app = PhoneGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
