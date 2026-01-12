from utils import reverse_engineer_components

# Your actual Excel data (first student: Bhavani C)
m1 = 45  # Member 1
m2 = 46  # Member 2  
mg = 50  # Internal Guide

print("="*60)
print("Testing with your actual data: Member1=45, Member2=46, Guide=50")
print("="*60)

print("\nPhase 2 Review 1 (weights: 15/15/10/10):")
print("-" * 40)
p2r1_m1 = reverse_engineer_components(m1, 2, 1)
p2r1_m2 = reverse_engineer_components(m2, 2, 1)
p2r1_mg = reverse_engineer_components(mg, 2, 1)

print(f"Member1 ({m1}): {p2r1_m1}")
print(f"Member2 ({m2}): {p2r1_m2}")
print(f"Guide   ({mg}): {p2r1_mg}")

print("\nAverages:")
avg_p2r1 = {}
for k in p2r1_m1.keys():
    avg = round((p2r1_m1[k] + p2r1_m2[k] + p2r1_mg[k]) / 3)
    avg_p2r1[k] = avg
    print(f"  {k}: ({p2r1_m1[k]} + {p2r1_m2[k]} + {p2r1_mg[k]}) / 3 = {avg}")

total_p2r1 = sum(avg_p2r1.values())
print(f"Total: {total_p2r1}")

print("\n" + "="*60)
print("Phase 2 Review 2 (weights: 10/10/15/15):")
print("-" * 40)
p2r2_m1 = reverse_engineer_components(m1, 2, 2)
p2r2_m2 = reverse_engineer_components(m2, 2, 2)
p2r2_mg = reverse_engineer_components(mg, 2, 2)

print(f"Member1 ({m1}): {p2r2_m1}")
print(f"Member2 ({m2}): {p2r2_m2}")
print(f"Guide   ({mg}): {p2r2_mg}")

print("\nAverages:")
avg_p2r2 = {}
for k in p2r2_m1.keys():
    avg = round((p2r2_m1[k] + p2r2_m2[k] + p2r2_mg[k]) / 3)
    avg_p2r2[k] = avg
    print(f"  {k}: ({p2r2_m1[k]} + {p2r2_m2[k]} + {p2r2_mg[k]}) / 3 = {avg}")

total_p2r2 = sum(avg_p2r2.values())
print(f"Total: {total_p2r2}")

print("\n" + "="*60)
print("EXPECTED in database:")
print("="*60)
print(f"P2R1: {list(avg_p2r1.values())} = {total_p2r1}")
print(f"P2R2: {list(avg_p2r2.values())} = {total_p2r2}")

print("\n" + "="*60)
print("ACTUAL in database (from earlier check):")
print("="*60)
print("P2R1: [14, 14, 9, 9] = 46")
print("P2R2: [14, 14, 9, 9] = 46")

print("\n" + "="*60)
if list(avg_p2r1.values()) == [14, 14, 9, 9]:
    print("✓ P2R1 matches! Code is working correctly for P2R1")
else:
    print("✗ P2R1 doesn't match!")

if list(avg_p2r2.values()) == [14, 14, 9, 9]:
    print("✗ P2R2 matches P2R1 - THIS IS THE BUG!")
    print(f"  Expected: {list(avg_p2r2.values())}")
    print(f"  Got: [14, 14, 9, 9]")
else:
    print("✓ P2R2 is different from P2R1 - Code is correct!")
