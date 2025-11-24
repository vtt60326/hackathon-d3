import csv
import random
import pandas as pd
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Constants
TOTAL_RECORDS = 300000
TOTAL_CUSTOMER_IDS = 200000
MIN_CUSTOMER_ID = 1
MAX_CUSTOMER_ID = 200000

# Device models with their max speeds
DEVICE_MODELS = {
    "Eero 6": "Copper",           # Copper only
    "Eero 6+": "500mb",           # Fiber up to 500 Mbps
    "Eero Pro 6": "1Gig",         # Fiber up to 1 Gig
    "Eero Pro 6E": "2Gig"        # Fiber up to 2 Gig
}

# Device status distribution
DEVICE_STATUS = {
    "Provisioned": 0.60,
    "CustShipped": 0.05,
    "PendingReturn": 0.10,
    "StockShelved": 0.25
}

# ISP distribution
ISP_OPTIONS = {
    "Frontier Communications": 0.90,
    "Not Frontier ISP": 0.10
}

# SQS Score distribution
SQS_SCORE_DIST = {
    3: 0.90,
    2: 0.07,
    1: 0.025,
    0: 0.005
}

# Date ranges
SHIP_DATE_START = datetime(2021, 10, 1)
SHIP_DATE_END = datetime(2022, 12, 31)
CURRENT_DATE = datetime(2025, 11, 17)
FIVE_YEARS_AGO = CURRENT_DATE - timedelta(days=5*365)


def load_customer_data():
    """Load customer data to match device models with customer speeds"""
    try:
        df = pd.read_csv('Data Output/customer_data.csv')
        # Create a dictionary mapping customer_id to speed
        customer_speeds = dict(zip(df['customer_id'], df['current_bb_speed']))
        return customer_speeds
    except FileNotFoundError:
        print("Warning: customer_data.csv not found. Generating without speed matching.")
        return None


def get_compatible_device_models(customer_speed):
    """
    Get device models compatible with customer speed.
    Customers can have devices that support their speed or higher.
    Some customers may have lower-speed devices for realism.
    """
    speed_hierarchy = {
        'Copper': ['Eero 6'],
        '500mb': ['Eero 6', 'Eero 6+'],
        '1Gig': ['Eero 6', 'Eero 6+', 'Eero Pro 6'],
        '2Gig': ['Eero 6', 'Eero 6+', 'Eero Pro 6', 'Eero Pro 6E']
    }
    
    compatible = speed_hierarchy.get(customer_speed, ['Eero 6'])
    
    # Add realism: some customers may have devices below their max speed
    # But most should have appropriate devices
    if customer_speed == '500mb':
        # 80% have Eero 6+, 20% have Eero 6
        return random.choices(['Eero 6+', 'Eero 6'], weights=[0.80, 0.20], k=1)[0]
    elif customer_speed == '1Gig':
        # 70% have Eero Pro 6, 20% have Eero 6+, 10% have Eero 6
        return random.choices(['Eero Pro 6', 'Eero 6+', 'Eero 6'], weights=[0.70, 0.20, 0.10], k=1)[0]
    elif customer_speed == '2Gig':
        # 60% have Eero Pro 6E, 25% have Eero Pro 6, 10% have Eero 6+, 5% have Eero 6
        return random.choices(['Eero Pro 6E', 'Eero Pro 6', 'Eero 6+', 'Eero 6'], 
                             weights=[0.60, 0.25, 0.10, 0.05], k=1)[0]
    else:  # Copper
        return 'Eero 6'


def generate_customer_id_distribution():
    """
    Generate customer ID distribution for exactly 300,000 records:
    - Use customer IDs between 1 and 200,000
    - ALL IDs from 1 to 200,000 must be assigned at least once
    - No ID can repeat more than 6 times
    - Skew towards 2 devices (80-90% of IDs appear twice)
    - All combinations (1,2,3,4,5,6) must be used
    - Must generate exactly 300,000 records
    """
    all_ids = list(range(MIN_CUSTOMER_ID, MAX_CUSTOMER_ID + 1))
    random.shuffle(all_ids)
    
    # Start by assigning each ID at least once (200,000 records used)
    id_usage = {}
    for cid in all_ids:
        id_usage[cid] = 1
    
    remaining_records = TOTAL_RECORDS - TOTAL_CUSTOMER_IDS  # 300,000 - 200,000 = 100,000
    
    # Math: We have 200,000 IDs and need 300,000 total records
    # If X IDs appear twice and Y IDs appear once: 2X + Y = 300,000, X + Y = 200,000
    # Solving: X = 100,000, Y = 100,000
    # So exactly 50% should appear twice to get exactly 300,000 records
    # But prompt says "skew towards 2 devices" and "80-90% can be used twice"
    # This means 80-90% of IDs that ARE used (not all 200k) can appear twice
    # Since we must use all 200k IDs, we'll aim for ~50% twice, but allow variation
    
    # We need to ensure all combinations (1,2,3,4,5,6) are used
    # This requires at least 4 IDs with counts 3,4,5,6 (beyond their base count of 1)
    # These need: 2+3+4+5 = 14 additional records
    # So: remaining_records - 14 should be distributed to make IDs appear twice
    records_for_twice = remaining_records - 14  # Reserve 14 for counts 3,4,5,6
    
    # Make selected IDs appear twice
    ids_to_make_twice = min(records_for_twice, len(all_ids))
    ids_to_update = random.sample(all_ids, ids_to_make_twice)
    for cid in ids_to_update:
        id_usage[cid] = 2
        remaining_records -= 1
    
    # Ensure we have at least one ID with each count (3,4,5,6)
    # This ensures all combinations (1,2,3,4,5,6) are represented
    required_counts = {3, 4, 5, 6}
    current_counts = set(id_usage.values())
    missing_counts = sorted([c for c in required_counts if c not in current_counts])
    
    # Assign missing counts, starting with smallest
    available_for_adjustment = [cid for cid in all_ids if id_usage[cid] <= 2]
    random.shuffle(available_for_adjustment)
    
    for target_count in missing_counts:
        if not available_for_adjustment:
            break
        # Find an ID we can upgrade to target_count
        for i, cid in enumerate(available_for_adjustment):
            current_count = id_usage[cid]
            additional_needed = target_count - current_count
            if additional_needed > 0 and remaining_records >= additional_needed:
                id_usage[cid] = target_count
                remaining_records -= additional_needed
                available_for_adjustment.pop(i)
                break
    
    # Distribute remaining records randomly, ensuring max 6 per ID
    # Create a list of IDs that can still accept more records
    while remaining_records > 0:
        eligible_ids = [cid for cid in all_ids if id_usage[cid] < 6]
        if not eligible_ids:
            # If no eligible IDs but still have remaining records, we have a problem
            # This shouldn't happen, but let's break to avoid infinite loop
            break
        cid = random.choice(eligible_ids)
        id_usage[cid] += 1
        remaining_records -= 1
    
    # Verify total before building list
    total_records = sum(id_usage.values())
    if total_records != TOTAL_RECORDS:
        # Adjust to exactly 300,000
        diff = TOTAL_RECORDS - total_records
        if diff > 0:
            # Need to add more records
            eligible_ids = [cid for cid in all_ids if id_usage[cid] < 6]
            for _ in range(min(diff, len(eligible_ids) * 5)):  # Max 5 more per ID
                if diff <= 0:
                    break
                cid = random.choice(eligible_ids)
                if id_usage[cid] < 6:
                    id_usage[cid] += 1
                    diff -= 1
        elif diff < 0:
            # Need to remove records
            eligible_ids = [cid for cid in all_ids if id_usage[cid] > 1]
            for _ in range(abs(diff)):
                if diff >= 0:
                    break
                cid = random.choice(eligible_ids)
                if id_usage[cid] > 1:
                    id_usage[cid] -= 1
                    diff += 1
    
    # Build the final list of customer IDs
    customer_ids = []
    for cid, count in id_usage.items():
        customer_ids.extend([cid] * count)
    
    # Verify we have exactly 300,000
    assert len(customer_ids) == TOTAL_RECORDS, f"Expected {TOTAL_RECORDS}, got {len(customer_ids)}"
    
    # Verify all IDs 1-200,000 are used
    used_ids = set(customer_ids)
    assert used_ids == set(range(1, 200001)), "Not all customer IDs are assigned"
    
    # Verify no ID repeats more than 6 times
    id_counts = {}
    for cid in customer_ids:
        id_counts[cid] = id_counts.get(cid, 0) + 1
    max_repeats = max(id_counts.values())
    assert max_repeats <= 6, f"Found ID with {max_repeats} repeats, max allowed is 6"
    
    # Verify all combinations (1,2,3,4,5,6) are used
    final_counts = set(id_counts.values())
    assert final_counts.issuperset({1, 2, 3, 4, 5, 6}), f"Missing repetition counts. Found: {final_counts}"
    
    # Shuffle the final list to randomize order
    random.shuffle(customer_ids)
    
    return customer_ids


def weighted_choice(choices_dict):
    """Helper function to make weighted random choices"""
    choices = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return random.choices(choices, weights=weights, k=1)[0]


def generate_ship_date():
    """Generate a random ship date between Oct 2021 and Dec 2022"""
    time_between = SHIP_DATE_END - SHIP_DATE_START
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    return SHIP_DATE_START + timedelta(days=random_days)


def generate_last_alive_date():
    """
    Generate last_alive_date:
    - 60% will be current date (11/17/25)
    - 40% will be random date within last 5 years, biased toward current date
    """
    if random.random() < 0.60:
        return CURRENT_DATE
    else:
        # Generate random date within last 5 years with bias toward current
        # Using triangular distribution with mode at current date
        days_range = (CURRENT_DATE - FIVE_YEARS_AGO).days
        random_days = int(random.triangular(0, days_range, days_range))
        return FIVE_YEARS_AGO + timedelta(days=random_days)


def generate_serial_number(existing_serials):
    """Generate a unique 10-digit serial number"""
    while True:
        serial = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        if serial not in existing_serials:
            existing_serials.add(serial)
            return serial


def generate_device_data(customer_speeds=None):
    """Generate all device records"""
    print("Generating customer ID distribution...")
    customer_ids = generate_customer_id_distribution()
    
    print(f"Total customer IDs to assign: {len(customer_ids)}")
    print(f"Unique customer IDs: {len(set(customer_ids))}")
    
    # Verify distribution
    id_counts = {}
    for cid in customer_ids:
        id_counts[cid] = id_counts.get(cid, 0) + 1
    
    twice_count = sum(1 for count in id_counts.values() if count == 2)
    twice_percentage = twice_count / len(id_counts) * 100
    print(f"IDs used twice: {twice_count} ({twice_percentage:.1f}%)")
    print(f"Max occurrences of any ID: {max(id_counts.values())}")
    
    print("\nGenerating device records...")
    records = []
    existing_serials = set()
    
    for i, customer_id in enumerate(customer_ids):
        if (i + 1) % 50000 == 0:
            print(f"Generated {i + 1:,} records...")
        
        # Get customer speed if available, otherwise random
        if customer_speeds and customer_id in customer_speeds:
            customer_speed = customer_speeds[customer_id]
            device_model = get_compatible_device_models(customer_speed)
        else:
            # Fallback: random device model
            device_model = random.choice(list(DEVICE_MODELS.keys()))
        
        record = {
            'customer_id': customer_id,
            'device_model': device_model,
            'device_status': weighted_choice(DEVICE_STATUS),
            'isp': weighted_choice(ISP_OPTIONS),
            'ship_date': generate_ship_date().strftime('%Y-%m-%d'),
            'last_alive_date': generate_last_alive_date().strftime('%Y-%m-%d'),
            'sqs_score': weighted_choice(SQS_SCORE_DIST),
            'serial_number': generate_serial_number(existing_serials)
        }
        records.append(record)
    
    return records


def write_to_csv(records, filename='Data Output/device_data.csv'):
    """Write records to CSV file"""
    print(f"\nWriting {len(records):,} records to {filename}...")
    
    fieldnames = ['customer_id', 'device_model', 'device_status', 'isp', 
                  'ship_date', 'last_alive_date', 'sqs_score', 'serial_number']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✓ Successfully wrote {filename}")


def print_statistics(records):
    """Print statistics about the generated data"""
    print("\n" + "="*50)
    print("DATA GENERATION STATISTICS")
    print("="*50)
    
    # Device Status distribution
    status_counts = {}
    for record in records:
        status = record['device_status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nDevice Status Distribution:")
    for status, count in sorted(status_counts.items()):
        percentage = count / len(records) * 100
        print(f"  {status}: {count:,} ({percentage:.2f}%)")
    
    # ISP distribution
    isp_counts = {}
    for record in records:
        isp = record['isp']
        isp_counts[isp] = isp_counts.get(isp, 0) + 1
    
    print("\nISP Distribution:")
    for isp, count in sorted(isp_counts.items()):
        percentage = count / len(records) * 100
        print(f"  {isp}: {count:,} ({percentage:.2f}%)")
    
    # SQS Score distribution
    sqs_counts = {}
    for record in records:
        score = record['sqs_score']
        sqs_counts[score] = sqs_counts.get(score, 0) + 1
    
    print("\nSQS Score Distribution:")
    for score in sorted(sqs_counts.keys(), reverse=True):
        count = sqs_counts[score]
        percentage = count / len(records) * 100
        print(f"  Score {score}: {count:,} ({percentage:.2f}%)")
    
    # Device Model distribution
    model_counts = {}
    for record in records:
        model = record['device_model']
        model_counts[model] = model_counts.get(model, 0) + 1
    
    print("\nDevice Model Distribution:")
    for model, count in sorted(model_counts.items()):
        percentage = count / len(records) * 100
        print(f"  {model}: {count:,} ({percentage:.2f}%)")
    
    # Last Alive Date - current vs historical
    current_date_str = CURRENT_DATE.strftime('%Y-%m-%d')
    current_count = sum(1 for r in records if r['last_alive_date'] == current_date_str)
    historical_count = len(records) - current_count
    
    print("\nLast Alive Date Distribution:")
    print(f"  Current date (2025-11-17): {current_count:,} ({current_count/len(records)*100:.2f}%)")
    print(f"  Historical dates: {historical_count:,} ({historical_count/len(records)*100:.2f}%)")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    print("Starting device data generation...")
    print(f"Target: {TOTAL_RECORDS:,} records")
    print(f"Customer ID range: {MIN_CUSTOMER_ID:,} to {MAX_CUSTOMER_ID:,}")
    
    # Load customer data to match device models with speeds
    customer_speeds = load_customer_data()
    if customer_speeds:
        print("✓ Loaded customer data for realistic device matching")
    
    records = generate_device_data(customer_speeds)
    write_to_csv(records)
    print_statistics(records)
    
    print("\n✓ Device data generation complete!")
