# 📱 US Phone Number Generator

A powerful, lightweight utility to generate unlimited valid US phone numbers for any state and export them to CSV.

## 🎯 What It Does

✅ Generates **valid NANP-compliant phone numbers** for **all 50 US states**  
✅ **Unlimited generation** - create millions of numbers if needed  
✅ **CSV export** - download your data instantly  
✅ **No internet required** - works completely offline  
✅ **Single .EXE file** - portable, no installation needed  

## 🚀 Quick Start

### Option 1: Use Pre-Built EXE (Easiest)

1. **Download**: `USPhoneNumberGenerator.exe` from the dist folder
2. **Run**: Double-click the .exe file
3. **Select**: Choose a state from the dropdown
4. **Generate**: Enter count and click "Generate Numbers"
5. **Download**: Click "Save to CSV" and choose your location

### Option 2: Build Your Own EXE (5 minutes)

**Windows Only:**

```bash
# 1. Install Python from python.org (check "Add to PATH")

# 2. Open Command Prompt in this folder

# 3. Install dependencies
pip install -r requirements.txt

# 4. Build the EXE
pyinstaller gui_app.spec

# 5. Find your EXE in the dist folder
```

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed steps.

### Option 3: Run with Python (Any OS)

```bash
# Install Python 3.8+

# Run GUI version
python gui_app.py

# OR Run CLI version
python us_phone_generator.py
```

## 💾 CSV Output Format

Perfect for databases, testing, and data analysis:

```csv
phone_number,state,area_code
305-234-5678,FL,305
415-987-6543,CA,415
212-555-1234,NY,212
```

## 🎮 Features

### Desktop GUI Application
- Click-and-generate interface
- Real-time preview
- Drag-and-save CSV export
- Works for all 50 states
- No programming knowledge required

### Command Line Interface
- Batch processing
- Scriptable
- Perfect for developers

### Technical Features
- ✓ Cryptographically secure random generation
- ✓ NANP standard compliance
- ✓ State-specific area codes
- ✓ Reserved number filtering
- ✓ No duplicate prevention
- ✓ Unlimited generation capacity

## 🌐 Online Verification (allareacodes.com)

To verify numbers online using `allareacodes.com` and local area-code checks:

```bash
python allareacodes_verifier.py \
    --input input_numbers.csv \
    --output verified_numbers_allareacodes.csv

# Optional flags:
# --carrier "Verizon"
# --no-allareacodes --no-intelius --no-whitepages --no-wirefly
# --internet-mobile-only --min-connected-sites 2
```

Output columns include:
- `input_number`
- `exact_number`
- `area_code`
- `local_area_valid`
- `local_state`
- `requested_carrier`
- `source`
- `verification_status`
- `http_status`
- `online_title`
- `source_url`
- `connected_sites`
- `internet_connectivity`
- `mobile_signal`
- `allareacodes_url`
- `intelius_url`
- `whitepages_url`
- `wirefly_url`
- `error`

Note: some environments may be blocked by `allareacodes.com` anti-bot protection (`verification_status=blocked`).
If `allareacodes.com` is disabled via `--no-allareacodes`, the script still outputs selected lookup URLs and uses `verification_status=website_linked`.
Use `--internet-mobile-only --min-connected-sites 2` for strict internet-based filtering (best-effort, not carrier API guaranteed).

## ✅ Simple Website Lookup (No API)

The web app now works with no API key and no server dependency:

1. Open `index.html` in your browser.
2. Generate numbers as usual.
3. Choose a carrier from the dropdown (`Any Carrier` or a specific carrier).
4. Select one or more verification website checkboxes.
5. Each row includes lookup links only for the selected websites.
6. CSV export includes `requested_carrier`, `verification_status`, `source`, `source_url`, `allareacodes_url`, `intelius_url`, `whitepages_url`, and `wirefly_url` columns.

This is a simple website-based lookup workflow and avoids paid API integrations.
In no-API mode, mobile line type and connectivity cannot be guaranteed.

## ✅ Guaranteed Mobile + Connectivity (API Required)

For strict output (only verified mobile numbers with connected lookup status), use:

```bash
export TELNYX_API_KEY="YOUR_TELNYX_API_KEY"

python guaranteed_mobile_generator.py \
    --state TX \
    --count 100 \
    --output verified_mobile_guaranteed.csv
```

This mode:
- keeps only rows where API lookup confirms `line_type=mobile`
- keeps only rows with `connectivity=connected`
- outputs carrier + connectivity fields in CSV

If requested count is not reached, increase `--max-attempts`.

## 📊 Supported States

All 50 states:  
AL • AK • AZ • AR • CA • CO • CT • DE • FL • GA • HI • ID • IL • IN • IA • KS • KY • LA • ME • MD • MA • MI • MN • MS • MO • MT • NE • NV • NH • NJ • NM • NY • NC • ND • OH • OK • OR • PA • RI • SC • SD • TN • TX • UT • VT • VA • WA • WV • WI • WY

## 🔧 How Numbers Are Generated

1. **Select State** → Validated against database
2. **Choose Area Code** → Random from state's valid codes
3. **Generate NXX (2nd-3rd digits)** → Valid codes, excludes N11, 555
4. **Create Line Number** → Random 4-digit sequence
5. **Validate** → Checks against NANP rules, reserves, and exclusions
6. **Return** → Formatted number ready for use

## 💡 Use Cases

- **Software Testing** - Test phone number input validation
- **Database Population** - Generate test data
- **Form Testing** - Verify form submission with valid numbers
- **API Testing** - Load testing with realistic phone data
- **Educational Projects** - Learn about NANP standards
- **Data Analysis** - Geographic phone number distribution studies

## ⚡ Performance

- **10,000 numbers** - < 1 second
- **100,000 numbers** - < 5 seconds
- **1,000,000 numbers** - < 1 minute
- **No upper limit** - Generate as many as you need!

## 🔐 Privacy & Security

- 100% offline processing
- No data collection
- No telemetry
- No internet required
- Completely private and secure

## 📦 Files Included

```
.
├── gui_app.py                 # Desktop GUI application
├── us_phone_generator.py      # Core generation engine
├── gui_app.spec              # PyInstaller configuration
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── BUILD_INSTRUCTIONS.md     # How to build .EXE
└── dist/
    └── USPhoneNumberGenerator.exe  # Ready-to-run executable
```

## 🛠️ Technical Stack

- **Language**: Python 3.8+
- **GUI**: tkinter (built-in, no installation needed)
- **Packaging**: PyInstaller (for .EXE creation)
- **Dependencies**: None! (Pure Python)

## 🚀 Getting Started

1. **Download** all files
2. **For GUI**: Run `python gui_app.py` or use the .EXE
3. **For CLI**: Run `python us_phone_generator.py`
4. **To Build**: Follow [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## 📝 CLI Example

```python
from us_phone_generator import USPhoneNumberGenerator

# Get all states
states = USPhoneNumberGenerator.get_states()
print(states)  # ['AL', 'AK', 'AZ', ...]

# Get area codes for a state
codes = USPhoneNumberGenerator.get_area_codes_for_state('CA')
print(codes)  # [209, 213, 279, ...]

# Generate single number
number = USPhoneNumberGenerator.generate_single_number('FL')
print(number)  # 3052345678

# Generate multiple numbers
numbers = USPhoneNumberGenerator.generate_numbers('NY', 100)
print(numbers)  # ['2125551234', '6465552345', ...]

# Export to CSV
csv_content = USPhoneNumberGenerator.export_to_csv('TX', numbers)
print(csv_content)  # CSV formatted string

# Save to file
filepath = USPhoneNumberGenerator.save_csv_file('CA', numbers, './data')
print(filepath)  # ./data/phone_numbers_CA_20260303_120000.csv
```

## 🎓 NANP Standards Implemented

- ✓ Valid area codes per state
- ✓ NXX codes exclude reserved N11 numbers
- ✓ Line numbers are 0000-9999
- ✓ Excludes 555-01xx (information/data)
- ✓ Proper formatting XXX-XXX-XXXX

## 📞 Support

For issues or questions, refer to the source code documentation.

## 📄 License

Free to use - no restrictions!

---

## ✨ Quick Tips

💡 **Tip 1**: Generate numbers in bulk for immediate export  
💡 **Tip 2**: Use the GUI for one-off generations  
💡 **Tip 3**: Use Python module for automation  
💡 **Tip 4**: Numbers are randomly distributed - safe for testing!  
💡 **Tip 5**: CSV import-ready format for Excel/databases  

---

**Ready to generate?** [Download the EXE](#quick-start) or [Build it yourself!](BUILD_INSTRUCTIONS.md)
