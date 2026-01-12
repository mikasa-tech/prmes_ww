import openpyxl
from pathlib import Path

def verify():
    ready_files = ["required/P1_Review1_Ready.xlsx", "required/P1_Review2_Ready.xlsx"]
    for file in ready_files:
        path = Path(file)
        if path.exists():
            wb = openpyxl.load_workbook(path, data_only=True)
            ws = wb.active
            print(f"\n--- File: {file} ---")
            rows = list(ws.iter_rows(min_row=1, max_row=5, values_only=True))
            for i, row in enumerate(rows, 1):
                print(f"Row {i}: {row}")
        else:
            print(f"File not found: {file}")

if __name__ == "__main__":
    verify()
