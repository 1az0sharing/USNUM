import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext
import threading
import csv
from us_phone_generator import USPhoneNumberGenerator

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
        main_frame.grid(row=0, column=0, sticky="nsew")
        
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
        state_combo.grid(row=1, column=1, sticky="ew", padx=5)
        
        # Count input
        ttk.Label(main_frame, text="Number of Entries:", font=("Helvetica", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.count_var = tk.StringVar(value="100")
        count_entry = ttk.Entry(main_frame, textvariable=self.count_var, width=35)
        count_entry.grid(row=2, column=1, sticky="ew", padx=5)

        # Carrier selection (multi-select)
        ttk.Label(main_frame, text="Carrier Selection:", font=("Helvetica", 11)).grid(row=3, column=0, sticky=tk.W, pady=5)
        carrier_frame = ttk.Frame(main_frame)
        carrier_frame.grid(row=3, column=1, sticky="ew", padx=5)

        self.carrier_names = [
            "AT&T",
            "Verizon",
            "T-Mobile",
            "Sprint",
            "US Cellular",
            "Boost Mobile",
            "Cricket Wireless",
            "Metro by T-Mobile",
            "Xfinity Mobile",
            "NEW CINGULAR WIRELESS PCS",
        ]
        self.carrier_vars = {
            "AT&T": tk.BooleanVar(value=True),
            "Verizon": tk.BooleanVar(value=True),
            "T-Mobile": tk.BooleanVar(value=True),
            "Sprint": tk.BooleanVar(value=False),
            "US Cellular": tk.BooleanVar(value=False),
            "Boost Mobile": tk.BooleanVar(value=False),
            "Cricket Wireless": tk.BooleanVar(value=False),
            "Metro by T-Mobile": tk.BooleanVar(value=False),
            "Xfinity Mobile": tk.BooleanVar(value=False),
            "NEW CINGULAR WIRELESS PCS": tk.BooleanVar(value=False),
        }

        for idx, carrier in enumerate(self.carrier_names):
            ttk.Checkbutton(
                carrier_frame,
                text=carrier,
                variable=self.carrier_vars[carrier],
            ).grid(row=idx // 3, column=idx % 3, sticky=tk.W, padx=(0, 10), pady=2)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.generate_btn = ttk.Button(btn_frame, text="Generate Numbers", command=self.generate_numbers)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to CSV", 
                  command=self.save_to_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", 
                  command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="", font=("Helvetica", 10))
        self.progress_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Text display area
        ttk.Label(main_frame, text="Generated Numbers:", font=("Helvetica", 11)).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        self.text_area = scrolledtext.ScrolledText(main_frame, height=25, width=80, wrap=tk.WORD)
        self.text_area.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.generated_numbers = []
        self.generated_rows = []
        self.selected_state = None
        self.selected_carriers = []

    def get_selected_carriers(self):
        return [carrier for carrier in self.carrier_names if self.carrier_vars[carrier].get()]

    def _on_generate_success(self, state, numbers, rows):
        self.generated_numbers = numbers
        self.generated_rows = rows
        self.selected_state = state

        output = (
            f"Generated {len(self.generated_numbers)} phone numbers for {state} "
            f"(Carriers: {', '.join(self.selected_carriers)})\n"
        )
        output += "=" * 60 + "\n\n"

        for i, row in enumerate(self.generated_rows, 1):
            num = row["number"]
            carrier = row["carrier"]
            formatted = f"{num[:3]}-{num[3:6]}-{num[6:]}"
            output += f"{i}. {formatted} | carrier: {carrier}\n"
            if i % 50 == 0:
                output += "\n"

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, output)
        self.text_area.config(state=tk.NORMAL)
        self.progress_label.config(text=f"✓ Generated {len(self.generated_numbers)} numbers successfully")
        self.generate_btn.config(state=tk.NORMAL)

    def _on_generate_error(self, error_text):
        messagebox.showerror("Error", error_text)
        self.progress_label.config(text="Error generating numbers")
        self.generate_btn.config(state=tk.NORMAL)
    
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
            if count > 1_000_000:
                messagebox.showerror("Error", "Please enter a number up to 1,000,000")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid number format")
            return
        
        # Disable button and show progress
        self.selected_carriers = self.get_selected_carriers()
        if not self.selected_carriers:
            messagebox.showerror("Error", "Please select at least one carrier")
            return

        self.generate_btn.config(state=tk.DISABLED)
        self.progress_label.config(text=f"Generating {count} numbers for {state}...")
        self.root.update()
        
        # Run generation in a separate thread to prevent freezing
        def generate():
            try:
                generated_numbers = USPhoneNumberGenerator.generate_numbers(state, count)
                generated_rows = [
                    {
                        "number": num,
                        "carrier": self.selected_carriers[idx % len(self.selected_carriers)],
                    }
                    for idx, num in enumerate(generated_numbers)
                ]
                self.root.after(0, lambda: self._on_generate_success(state, generated_numbers, generated_rows))
            except Exception as e:
                self.root.after(0, lambda: self._on_generate_error(str(e)))
        
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
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["phone_number", "state", "area_code", "requested_carrier"])
                for row in self.generated_rows:
                    number = row["number"]
                    writer.writerow([
                        f"{number[:3]}-{number[3:6]}-{number[6:]}",
                        self.selected_state,
                        number[:3],
                        row["carrier"],
                    ])
            
            messagebox.showinfo("Success", f"File saved successfully!\n{file_path}")
            self.progress_label.config(
                text=f"✓ Saved {len(self.generated_numbers)} numbers to CSV"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.generated_numbers = []
        self.generated_rows = []
        self.selected_state = None
        self.selected_carriers = []
        self.carrier_vars["AT&T"].set(True)
        self.carrier_vars["Verizon"].set(True)
        self.carrier_vars["T-Mobile"].set(True)
        self.carrier_vars["Sprint"].set(False)
        self.carrier_vars["US Cellular"].set(False)
        self.carrier_vars["Boost Mobile"].set(False)
        self.carrier_vars["Cricket Wireless"].set(False)
        self.carrier_vars["Metro by T-Mobile"].set(False)
        self.carrier_vars["Xfinity Mobile"].set(False)
        self.carrier_vars["NEW CINGULAR WIRELESS PCS"].set(False)
        self.progress_label.config(text="")


def main():
    root = tk.Tk()
    app = PhoneGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
