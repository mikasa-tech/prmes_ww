
import sys
import os
import io

# Add parent directory (required) to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils import reverse_engineer_components
    from upload_helpers import handle_three_evaluators
    from review_config import get_review_config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Ensure you are running this from the 'required/scripts' folder or project root.")
    sys.exit(1)

def test_reverse_engineering():
    print("\n--- Testing Reverse Engineering ---")
    # Phase 1 Review 1: Weights 20, 10, 10, 10. Total 50.
    total = 45
    comps = reverse_engineer_components(total, 1, 1)
    print(f"Total: {total} -> {comps}")
    assert sum(comps.values()) == total, f"Sum mismatch: {sum(comps.values())} != {total}"
    assert comps['criteria1'] == 18 # 45 * 0.4 = 18.0
    
    total = 46
    comps = reverse_engineer_components(total, 1, 1)
    print(f"Total: {total} -> {comps}")
    assert sum(comps.values()) == total
    # 46 * 0.4 = 18.4 -> 18
    # 46 * 0.2 = 9.2 -> 9
    # 18 + 9 + 9 + 9 = 45. Remainder 1.
    # Sorted decimals: 0.4, 0.2, 0.2, 0.2. Largest is 0.4.
    # So criteria1 gets +1 -> 19.
    assert comps['criteria1'] == 19
    print("Reverse engineering logic: OK (Hamilton method verified)")

def test_averaging_logic():
    print("\n--- Testing Averaging Logic ---")
    # Mock row and key map
    row = {
        'm1': 45,
        'm2': 40,
        'guide': 48
    }
    key_map = {
        'member1': 'm1',
        'member2': 'm2',
        'internal_guide': 'guide'
    }
    
    # helper returns (comp, m1_comp, m2_comp, guide_comp)
    final_comp, m1_comp, m2_comp, guide_comp = handle_three_evaluators(row, key_map, 1, 1)
    
    print(f"M1 (45): {m1_comp}")
    print(f"M2 (40): {m2_comp}")
    print(f"Guide (48): {guide_comp}")
    print(f"Final Average: {final_comp}")
    
    # Verify expected average
    # Criteria 1 (Weight 20):
    # M1(45) -> 18
    # M2(40) -> 16
    # G(48) -> 19 (48*0.4=19.2 -> 19) Wait, let's check reverse engineer for 48
    # 48 * 0.2 = 9.6 -> 9. 19+9+9+9 = 46. Remainder 2.
    # Decimals: .2, .6, .6, .6.
    # The sorted decimals will prioritize .6 ones.
    # So criteria 2,3,4 get +1. criteria1 stays 19.
    # Let's verify my manual calc against the script output.
    
    # Average Criteria 1: (18 + 16 + 19)/3 = 53/3 = 17.66 -> 18
    assert final_comp['criteria1'] == 18, f"Expected 18, got {final_comp['criteria1']}"
    
    print("Averaging logic: OK")

def main():
    test_reverse_engineering()
    test_averaging_logic()
    print("\nAll verification tests passed!")

if __name__ == "__main__":
    main()
