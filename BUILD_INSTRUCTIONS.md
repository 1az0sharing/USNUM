# US Phone Number Generator - Build Instructions

## ✨ Features

- **All 50 US States** - Generate phone numbers for any US state
- **NANP Compliant** - Follows North American Numbering Plan rules
- **Unlimited Datasets** - No limits on number generation
- **CSV Export** - Download unlimited phone number sets in CSV format
- **Desktop GUI** - Easy-to-use graphical interface
- **Portable EXE** - Single standalone executable file

## 📋 System Requirements for Building

- **Windows 10 or later** (to create .exe file)
- **Python 3.8 or higher**
- **Administrator privileges** (for installation)

## 🔨 Build Instructions

### Step 1: Install Python

1. Download from [python.org](https://www.python.org/downloads/)
2. During installation, **CHECK** "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   ```

### Step 2: Download/Prepare Files

1. Create a folder: `C:\PhoneGenerator`
2. Copy the following files to this folder:
   - `gui_app.py`
   - `us_phone_generator.py`
   - `gui_app.spec`
   - `requirements.txt`

### Step 3: Install Dependencies

Open Command Prompt in the folder and run:

```cmd
pip install -r requirements.txt
```

### Step 4: Build the EXE

Run one of these commands:

**Option A: Using the spec file (Recommended)**
```cmd
pyinstaller gui_app.spec
```

**Option B: Quick build (one-liner)**
```cmd
pyinstaller --onefile --windowed --name USPhoneNumberGenerator gui_app.py
```

### Step 5: Locate Your EXE

The executable will be in:
```
dist/USPhoneNumberGenerator.exe
```

## 📦 Distribution

You can now distribute `USPhoneNumberGenerator.exe` to anyone. It requires:
- **Windows 10+** - Yes
- **Python installed** - No (it's bundled)
- **Internet** - No
- **Installation** - No

Just double-click to run!

## 🚀 Usage

1. **Run the Application**
   - Double-click `USPhoneNumberGenerator.exe`

2. **Select a State**
   - Choose from dropdown (AL, AK, AZ, AR, CA, ... WY)

3. **Enter Count**
   - Enter number of phone numbers to generate
   - No limit!

4. **Generate**
   - Click "Generate Numbers"
   - Numbers appear in the text area

5. **Save to CSV**
   - Click "Save to CSV"
   - Choose location and filename
   - Get a properly formatted CSV file with:
     - Phone Number (formatted as XXX-XXX-XXXX)
     - State Code
     - Area Code

## 📊 CSV Format

The generated CSV files contain:

```
phone_number,state,area_code
305-234-5678,FL,305
305-987-6543,FL,305
...
```

## 🎯 Supported States

All 50 US states:
- AL (Alabama)
- AK (Alaska)
- AZ (Arizona)
- AR (Arkansas)
- CA (California)
- CO (Colorado)
- CT (Connecticut)
- DE (Delaware)
- FL (Florida)
- GA (Georgia)
- HI (Hawaii)
- ID (Idaho)
- IL (Illinois)
- IN (Indiana)
- IA (Iowa)
- KS (Kansas)
- KY (Kentucky)
- LA (Louisiana)
- ME (Maine)
- MD (Maryland)
- MA (Massachusetts)
- MI (Michigan)
- MN (Minnesota)
- MS (Mississippi)
- MO (Missouri)
- MT (Montana)
- NE (Nebraska)
- NV (Nevada)
- NH (New Hampshire)
- NJ (New Jersey)
- NM (New Mexico)
- NY (New York)
- NC (North Carolina)
- ND (North Dakota)
- OH (Ohio)
- OK (Oklahoma)
- OR (Oregon)
- PA (Pennsylvania)
- RI (Rhode Island)
- SC (South Carolina)
- SD (South Dakota)
- TN (Tennessee)
- TX (Texas)
- UT (Utah)
- VT (Vermont)
- VA (Virginia)
- WA (Washington)
- WV (West Virginia)
- WI (Wisconsin)
- WY (Wyoming)

## 📱 Phone Number Validation

Generated numbers follow NANP standards:
- ✓ Valid area codes for each state
- ✓ Valid NXX codes (no N11 codes)
- ✓ Valid line numbers
- ✓ Excludes reserved 555-01xx numbers

## 🛠️ Troubleshooting

**Issue: "python" not found**
- Solution: Reinstall Python with "Add Python to PATH"

**Issue: PyInstaller not found**
- Solution: Run `pip install pyinstaller` again

**Issue: EXE won't execute**
- Solution: Try running as Administrator or rebuild

**Issue: GUI looks strange**
- Solution: Windows is rendering it correctly; this is normal on some versions

## 📝 Command Line Alternative

If you prefer command line, run:
```cmd
python us_phone_generator.py
```

## 💡 Advanced Usage

### Generate 1 Million Numbers
1. Select state
2. Enter: `1000000`
3. Click Generate (will take a minute)
4. Save to CSV

### Bulk Export Multiple States
1. Generate numbers for CA
2. Save file
3. Repeat for NY
4. Repeat for TX
5. You now have 3 CSV files

## 📞 Number Format

Numbers are formatted as: `XXX-XXX-XXXX`
Example: `305-234-5678`

## ⚙️ Technical Details

- **Language**: Python 3
- **GUI Framework**: tkinter (built-in)
- **Algorithm**: Cryptographically secure random (secrets module)
- **No External Dependencies**: Only tkinter needed
- **File Size**: ~50-100 MB (includes Python runtime)

## 🔒 Privacy

- All processing is local
- No internet connection needed
- No data collection
- No telemetry

## 📄 License

Free to use and distribute.

---

**Ready to build?** Follow Steps 1-5 above to create your EXE!
