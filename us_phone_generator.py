import secrets
import csv
import io
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Complete US Area Codes Database
US_AREA_CODES = {
    "AL": [205, 251, 256, 334, 938],
    "AK": [907],
    "AZ": [480, 520, 623, 928],
    "AR": [479, 501, 870],
    "CA": [209, 213, 279, 310, 323, 408, 415, 424, 442, 510, 530, 559, 562, 619, 626, 628, 650, 657, 661, 669, 707, 714, 760, 805, 818, 831, 858, 909, 916, 925, 949, 951],
    "CO": [303, 719, 720, 970],
    "CT": [203, 475, 860, 959],
    "DE": [302],
    "FL": [239, 305, 321, 352, 386, 407, 561, 645, 772, 786, 813, 850, 863, 904, 941, 954],
    "GA": [229, 404, 470, 478, 678, 706, 762, 770, 912],
    "HI": [808],
    "ID": [208, 986],
    "IL": [217, 224, 309, 312, 331, 618, 630, 773, 779, 815, 847, 872],
    "IN": [219, 260, 317, 463, 574, 765, 812, 930],
    "IA": [319, 515, 563, 641, 712],
    "KS": [316, 620, 785, 913],
    "KY": [270, 364, 502, 606, 859],
    "LA": [225, 318, 337, 504, 985],
    "ME": [207],
    "MD": [240, 301, 410, 443, 667],
    "MA": [339, 351, 413, 508, 617, 774, 781, 857, 978],
    "MI": [231, 248, 269, 313, 517, 586, 616, 734, 810, 906, 989],
    "MN": [218, 320, 507, 612, 651, 763, 952],
    "MS": [228, 662, 769],
    "MO": [314, 417, 573, 660, 816],
    "MT": [406],
    "NE": [308, 402, 531],
    "NV": [702, 725, 775],
    "NH": [603],
    "NJ": [201, 551, 609, 732, 848, 856, 862, 908, 973],
    "NM": [505, 575],
    "NY": [212, 315, 347, 516, 518, 585, 607, 631, 646, 716, 718, 845, 914, 917, 929, 934],
    "NC": [252, 336, 704, 743, 828, 910, 919, 980],
    "ND": [701],
    "OH": [216, 220, 234, 330, 380, 419, 440, 513, 614, 740, 937],
    "OK": [405, 539, 580, 918],
    "OR": [458, 503, 541],
    "PA": [215, 223, 267, 412, 484, 570, 610, 717, 724, 814, 878],
    "RI": [401],
    "SC": [803, 843, 864],
    "SD": [605],
    "TN": [423, 615, 731, 865, 901, 931],
    "TX": [210, 214, 254, 281, 325, 346, 361, 409, 430, 512, 682, 713, 726, 737, 806, 817, 830, 832, 903, 915, 936, 940, 945, 956, 972, 979],
    "UT": [385, 435, 801],
    "VT": [802],
    "VA": [276, 434, 540, 571, 703, 757, 804],
    "WA": [206, 253, 360, 425, 509],
    "WV": [304, 681],
    "WI": [262, 414, 534, 608, 715, 920],
    "WY": [307]
}

# NANP Rules
N11_CODES = {"211", "311", "411", "511", "611", "711", "811", "911"}

EXCLUDED_NXX = {"555", "900", "976", "988"}

RESERVED_LINE_RANGES = [
    ("0000", "0099"),
    ("1000", "1099"),
    ("5558", "5558"),
    ("9999", "9999"),
]

# Valid NXX codes (2nd and 3rd digits)
VALID_NXX = [
    str(i).zfill(3)
    for i in range(200, 1000)
    if str(i).zfill(3) not in N11_CODES and str(i).zfill(3) not in EXCLUDED_NXX
]

USED_NUMBERS_FILE = Path(".used_numbers.json")
USED_NUMBERS_HISTORY_FILE = Path("used_numbers_history.csv")


def is_reserved_line_number(line_number: str) -> bool:
    for minimum, maximum in RESERVED_LINE_RANGES:
        if minimum <= line_number <= maximum:
            return True
    return False


def _load_used_numbers() -> Dict[str, List[str]]:
    if not USED_NUMBERS_FILE.exists():
        return {}
    try:
        with open(USED_NUMBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {
                str(state).upper(): [str(num) for num in numbers]
                for state, numbers in data.items()
                if isinstance(numbers, list)
            }
    except Exception:
        return {}
    return {}


def _save_used_numbers(data: Dict[str, List[str]]) -> None:
    with open(USED_NUMBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def _append_used_numbers_history(state: str, numbers: List[str]) -> None:
    is_new_file = not USED_NUMBERS_HISTORY_FILE.exists()
    timestamp = datetime.now().isoformat(timespec="seconds")
    with open(USED_NUMBERS_HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new_file:
            writer.writerow(["timestamp", "state", "phone_number", "area_code"])
        for number in numbers:
            writer.writerow([
                timestamp,
                state,
                f"{number[:3]}-{number[3:6]}-{number[6:]}",
                number[:3],
            ])


def register_generated_numbers(state: str, numbers: List[str]) -> None:
    if not numbers:
        return
    state_upper = state.upper()
    used_data = _load_used_numbers()
    existing = set(used_data.get(state_upper, []))
    existing.update(numbers)
    used_data[state_upper] = sorted(existing)
    _save_used_numbers(used_data)
    _append_used_numbers_history(state_upper, numbers)


def get_used_numbers_for_state(state: str) -> set:
    used_data = _load_used_numbers()
    return set(used_data.get(state.upper(), []))

class USPhoneNumberGenerator:
    """Generate valid NANP phone numbers for US states"""
    
    @staticmethod
    def get_states() -> List[str]:
        """Get list of all US states"""
        return sorted(US_AREA_CODES.keys())
    
    @staticmethod
    def get_area_codes_for_state(state: str) -> List[int]:
        """Get area codes for a specific state"""
        return US_AREA_CODES.get(state.upper(), [])
    
    @staticmethod
    def generate_single_number(state: str) -> str:
        """Generate a single valid phone number for a state"""
        state_upper = state.upper()
        if state_upper not in US_AREA_CODES:
            raise ValueError(f"Invalid state: {state}")

        while True:
            area_code = secrets.choice(US_AREA_CODES[state_upper])
            nxx = secrets.choice(VALID_NXX)
            line_number = str(secrets.randbelow(10000)).zfill(4)

            if is_reserved_line_number(line_number):
                continue

            return f"{area_code}{nxx}{line_number}"
    
    @staticmethod
    def generate_numbers(state: str, count: int) -> List[str]:
        """Generate multiple valid phone numbers for a state"""
        if count <= 0:
            raise ValueError("Count must be positive")
        
        state_upper = state.upper()
        if state_upper not in US_AREA_CODES:
            raise ValueError(f"Invalid state: {state}")
        
        used_numbers = get_used_numbers_for_state(state_upper)
        numbers = set()
        attempts = 0
        max_attempts = max(count * 30, 10000)
        
        while len(numbers) < count and attempts < max_attempts:
            candidate = USPhoneNumberGenerator.generate_single_number(state)
            if candidate in used_numbers or candidate in numbers:
                attempts += 1
                continue
            numbers.add(candidate)
            attempts += 1

        if len(numbers) < count:
            raise ValueError(
                "Could not generate enough unique numbers. "
                "Try a smaller count or clear used-number history."
            )

        generated = sorted(list(numbers))[:count]
        register_generated_numbers(state_upper, generated)
        return generated
    
    @staticmethod
    def export_to_csv(state: str, numbers: List[str], filename: Optional[str] = None) -> str:
        """Export phone numbers to CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phone_numbers_{state}_{timestamp}.csv"
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["phone_number", "state", "area_code"])
        
        for number in numbers:
            area_code = number[:3]
            writer.writerow([
                f"{number[:3]}-{number[3:6]}-{number[6:]}",
                state.upper(),
                area_code
            ])
        
        return output.getvalue()
    
    @staticmethod
    def save_csv_file(state: str, numbers: List[str], directory: str = ".") -> str:
        """Save phone numbers to a CSV file and return the file path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phone_numbers_{state}_{timestamp}.csv"
        filepath = os.path.join(directory, filename)
        
        csv_content = USPhoneNumberGenerator.export_to_csv(state, numbers, filename)
        
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)
        
        return filepath


def main():
    """Simple CLI interface"""
    print("=" * 60)
    print("US PHONE NUMBER GENERATOR")
    print("=" * 60)
    
    # Display available states
    states = USPhoneNumberGenerator.get_states()
    print(f"\nAvailable states: {', '.join(states)}\n")
    
    while True:
        state = input("Enter state code (or 'quit' to exit): ").strip().upper()
        
        if state == "QUIT":
            break
        
        if state not in states:
            print(f"Invalid state. Please choose from: {', '.join(states)}")
            continue
        
        try:
            count = int(input(f"Enter number of phone numbers to generate (for {state}): ").strip())
            if count <= 0:
                print("Please enter a positive number")
                continue
        except ValueError:
            print("Please enter a valid number")
            continue
        
        print(f"\nGenerating {count} phone numbers for {state}...")
        numbers = USPhoneNumberGenerator.generate_numbers(state, count)
        
        save = input("Save to CSV file? (y/n): ").strip().lower()
        if save == 'y':
            filepath = USPhoneNumberGenerator.save_csv_file(state, numbers)
            print(f"✓ Saved to: {filepath}")
        else:
            # Show first 10 numbers
            print(f"\nFirst 10 generated numbers for {state}:")
            for i, num in enumerate(numbers[:10], 1):
                formatted = f"{num[:3]}-{num[3:6]}-{num[6:]}"
                print(f"  {i}. {formatted}")
            if len(numbers) > 10:
                print(f"  ... and {len(numbers) - 10} more")
        
        print()


if __name__ == "__main__":
    main()
