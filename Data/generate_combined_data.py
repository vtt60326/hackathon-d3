import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate Customer Data (100,000 records)
print("Generating customer data...")

# Customer IDs: unique numbers between 1 and 100,000
customer_ids = list(range(1, 100001))
random.shuffle(customer_ids)

# CLV Decile: 1-10, 10% each
clv_decile = np.repeat(range(1, 11), 10000)
np.random.shuffle(clv_decile)

# Churn Risk: 2% are 1, 98% are 0
churn_risk = np.random.choice([0, 1], size=100000, p=[0.98, 0.02])

# Current BB Speed distribution
# 10% Copper (below 500mb), 32% 500mb, 35% 1Gig, 20% 2Gig
speed_categories = ['Copper', '500mb', '1Gig', '2Gig']
speed_distribution = [0.10, 0.32, 0.35, 0.20]
# Normalize to ensure they sum to 1.0
speed_distribution = [p / sum(speed_distribution) for p in speed_distribution]
current_bb_speed = np.random.choice(speed_categories, size=100000, p=speed_distribution)

# Network Activity: 25% heavy, 50% medium, 25% light
network_activity = np.random.choice(['heavy', 'medium', 'light'], size=100000, p=[0.25, 0.50, 0.25])

# Account Tenure: 1-120 months
account_tenure = np.random.randint(1, 121, size=100000)

# Time of Last Broadband Upgrade: between 1/1/2016 and 11/1/2025
start_date = datetime(2016, 1, 1)
end_date = datetime(2025, 11, 1)
date_range = (end_date - start_date).days
time_of_last_upgrade = [start_date + timedelta(days=random.randint(0, date_range)) for _ in range(100000)]
time_of_last_upgrade = [d.strftime('%Y-%m-%d') for d in time_of_last_upgrade]

# Broadband Type: Copper if speed is Copper, else Fiber
broadband_type = ['Copper' if speed == 'Copper' else 'Fiber' for speed in current_bb_speed]

# Customer Segment distribution
# Aspirational Adopters - 6%, Peak Performers - 22%, Budget Balancers - 14%, 
# Foolproof Followers - 21%, Settled Simplifiers - 36%
segments = ['Aspirational Adopters', 'Peak Performers', 'Budget Balancers', 'Foolproof Followers', 'Settled Simplifiers']
segment_distribution = [0.06, 0.22, 0.14, 0.21, 0.36]
# Normalize to ensure they sum to 1.0
segment_distribution = [p / sum(segment_distribution) for p in segment_distribution]
customer_segment = np.random.choice(segments, size=100000, p=segment_distribution)

# Create Customer DataFrame
customer_df = pd.DataFrame({
    'customer_id': customer_ids,
    'clv_decile': clv_decile,
    'churn_risk': churn_risk,
    'current_bb_speed': current_bb_speed,
    'network_activity': network_activity,
    'account_tenure': account_tenure,
    'time_of_last_broadband_upgrade': time_of_last_upgrade,
    'broadband_type': broadband_type,
    'customer_segment': customer_segment
})

# Save Customer Data
customer_df.to_csv('Data Output/customer_data.csv', index=False)
print(f"Customer data generated: {len(customer_df)} records")

# Generate Device Data (300,000 records)
print("\nGenerating device data...")

device_records = []

# Split customers: 50,000 with 1 device, 50,000 with 2-6 devices
single_device_customers = customer_ids[:50000]
multi_device_customers = customer_ids[50000:]

# Track used serial numbers to ensure uniqueness
used_serials = set()

def generate_unique_serial():
    """Generate a unique 10-digit serial number"""
    while True:
        serial = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        if serial not in used_serials:
            used_serials.add(serial)
            return serial

# Device model mapping to speed compatibility
def get_compatible_device_models(bb_speed):
    """Return list of compatible device models based on broadband speed"""
    if bb_speed == 'Copper':
        # Copper customers can only have Eero 6
        return ['Eero 6']
    elif bb_speed == '500mb':
        # Can use Eero 6+ or higher models (customers at lower speeds than device max)
        # Most should have Eero 6+, but some may have lower models for realism
        return ['Eero 6+', 'Eero 6']
    elif bb_speed == '1Gig':
        # Can use Eero Pro 6 or higher models
        # Most should have Eero Pro 6, but some may have lower models
        return ['Eero Pro 6', 'Eero 6+', 'Eero 6']
    elif bb_speed == '2Gig':
        # Should use Eero Pro 6E, but can also use lower models for realism
        return ['Eero Pro 6E', 'Eero Pro 6', 'Eero 6+']
    return ['Eero Pro 6E']

def select_device_model(bb_speed, compatible_models):
    """Select device model with realistic distribution based on speed"""
    if bb_speed == 'Copper':
        return 'Eero 6'
    elif bb_speed == '500mb':
        # 80% Eero 6+, 20% Eero 6
        return random.choices(['Eero 6+', 'Eero 6'], weights=[0.80, 0.20])[0]
    elif bb_speed == '1Gig':
        # 70% Eero Pro 6, 20% Eero 6+, 10% Eero 6
        return random.choices(['Eero Pro 6', 'Eero 6+', 'Eero 6'], weights=[0.70, 0.20, 0.10])[0]
    elif bb_speed == '2Gig':
        # 60% Eero Pro 6E, 25% Eero Pro 6, 10% Eero 6+, 5% Eero 6
        return random.choices(['Eero Pro 6E', 'Eero Pro 6', 'Eero 6+', 'Eero 6'], weights=[0.60, 0.25, 0.10, 0.05])[0]
    return 'Eero Pro 6E'

# Device status distribution
device_statuses = ['Provisioned', 'CustShipped', 'PendingReturn', 'StockShelved']
status_probs = [0.60, 0.05, 0.10, 0.25]

# ISP distribution
isp_options = ['Frontier Communications', 'Not Frontier ISP']
isp_probs = [0.90, 0.10]

# Ship date range: October 2021 to December 2022
ship_start = datetime(2021, 10, 1)
ship_end = datetime(2022, 12, 31)
ship_date_range = (ship_end - ship_start).days

# Last alive date: 60% current date, 40% random within last 5 years with bias towards current
current_date = datetime(2025, 11, 17)
five_years_ago = datetime(2020, 11, 17)

def generate_last_alive_date():
    """Generate last alive date with 60% current date, 40% historical with bias"""
    if random.random() < 0.60:
        return current_date.strftime('%Y-%m-%d')
    else:
        # Generate date within last 5 years with bias towards current date
        # Using exponential distribution for bias
        days_back = int(np.random.exponential(scale=365) % (5 * 365))
        date = current_date - timedelta(days=days_back)
        return date.strftime('%Y-%m-%d')

# SQS Score distribution: 90% is 3, 7% is 2, 2.5% is 1, 0.5% is 0
sqs_scores = [0, 1, 2, 3]
sqs_probs = [0.005, 0.025, 0.07, 0.90]

# Process single device customers (50,000 customers, 50,000 devices)
print("Processing single device customers...")
for cust_id in single_device_customers:
    # Get customer's broadband speed
    cust_speed = customer_df[customer_df['customer_id'] == cust_id]['current_bb_speed'].values[0]
    
    # Get compatible device models and select one
    compatible_models = get_compatible_device_models(cust_speed)
    device_model = select_device_model(cust_speed, compatible_models)
    
    device_records.append({
        'customer_id': cust_id,
        'serial_number': generate_unique_serial(),
        'device_model': device_model,
        'device_status': np.random.choice(device_statuses, p=status_probs),
        'isp': np.random.choice(isp_options, p=isp_probs),
        'ship_date': (ship_start + timedelta(days=random.randint(0, ship_date_range))).strftime('%Y-%m-%d'),
        'last_alive_date': generate_last_alive_date(),
        'sqs_score': np.random.choice(sqs_scores, p=sqs_probs)
    })

# Process multi device customers (50,000 customers)
# No device limit - distribute devices naturally to reach 300,000 total
# Need 250,000 devices from 50,000 customers (average of 5 devices per customer)

print("Processing multi device customers...")

# Distribute devices among 50,000 customers
# Target: average of 5 devices per customer to reach 250,000 total
# Strategy: Mix of 2, 3, 4, 5, and 6 devices per customer
devices_per_customer = []

# Calculate distribution to reach exactly 250,000 devices from 50,000 customers
# Average needed: 250,000 / 50,000 = 5 devices per customer
# Distribution (must total 50,000 customers and 250,000 devices):
# - 10,000 customers with 2 devices = 20,000 devices
# - 15,000 customers with 3 devices = 45,000 devices
# - 15,000 customers with 4 devices = 60,000 devices
# - 10,000 customers with 5 devices = 50,000 devices
# Total customers: 10,000 + 15,000 + 15,000 + 10,000 = 50,000 ✓
# Total devices: 20,000 + 45,000 + 60,000 + 50,000 = 175,000 devices
# Need 75,000 more devices, so add:
# - 5,000 customers with 6 devices = 30,000 devices
# - 5,000 customers with 7 devices = 35,000 devices
# Updated totals:
# Customers: 10k + 15k + 15k + 10k + 5k + 5k = 60k ✗ (too many!)
#
# Let me recalculate properly:
# Need 250,000 devices from 50,000 customers = average 5
# Distribution:
# - 5,000 customers with 2 devices = 10,000 devices
# - 10,000 customers with 3 devices = 30,000 devices
# - 15,000 customers with 4 devices = 60,000 devices
# - 10,000 customers with 5 devices = 50,000 devices
# - 10,000 customers with 6 devices = 60,000 devices
# Total: 5k + 10k + 15k + 10k + 10k = 50,000 customers ✓
# Total devices: 10k + 30k + 60k + 50k + 60k = 210,000 devices
# Need 40,000 more devices...
#
# Better approach: Use a simpler distribution
# - 10,000 customers with 3 devices = 30,000 devices
# - 20,000 customers with 4 devices = 80,000 devices
# - 20,000 customers with 5 devices = 100,000 devices
# Total: 10k + 20k + 20k = 50,000 customers ✓
# Total devices: 30k + 80k + 100k = 210,000 devices
# Need 40,000 more devices, so:
# - 10,000 customers with 6 devices = 60,000 devices (but only need 40k)
# So adjust: - 10,000 customers with 4 devices, + 10,000 customers with 5 devices
# Final: - 10k with 3, - 10k with 4, + 20k with 5 = 30k + 70k + 150k = 250k ✓
# Customers: 10k + 10k + 30k = 50k ✓

# Final distribution to reach exactly 250,000 devices from 50,000 customers:
# - 20,000 customers with 3 devices = 60,000 devices
# - 20,000 customers with 4 devices = 80,000 devices
# - 10,000 customers with 5 devices = 50,000 devices
# Total customers: 20k + 20k + 10k = 50,000 ✓
# Total devices: 60k + 80k + 50k = 190,000 devices
# Need 60,000 more devices, so:
# - 10,000 customers with 6 devices = 60,000 devices
# Final: 20k with 3, 20k with 4, 10k with 5, 10k with 6
# But that's 60k customers, need 50k...
#
# Correct calculation:
# Need 250,000 devices from 50,000 customers
# If all had 5 devices: 50k * 5 = 250k ✓ Perfect!
# But prompt says "at most 3", so we need a mix
#
# Solution: Mix that averages to 5 but respects "at most 3" where possible
# - 10,000 customers with 2 devices = 20,000 devices
# - 20,000 customers with 3 devices = 60,000 devices  
# - 20,000 customers with 5 devices = 100,000 devices
# Total: 10k + 20k + 20k = 50,000 customers ✓
# Total devices: 20k + 60k + 100k = 180,000 devices
# Need 70,000 more devices, so:
# - 10,000 customers with 7 devices = 70,000 devices
# Final: 10k with 2, 20k with 3, 20k with 5, 10k with 7 = 50k customers, 250k devices ✓

# Natural distribution without device limit - mix of 2-6 devices per customer
# Need exactly 250,000 devices from 50,000 customers (average of 5)
# Distribution:
# - 5,000 customers with 2 devices = 10,000 devices
# - 10,000 customers with 3 devices = 30,000 devices
# - 15,000 customers with 4 devices = 60,000 devices
# - 15,000 customers with 5 devices = 75,000 devices
# - 5,000 customers with 6 devices = 30,000 devices
# Total: 5k + 10k + 15k + 15k + 5k = 50,000 customers ✓
# Total devices: 10k + 30k + 60k + 75k + 30k = 205,000 devices
# Need 45,000 more devices, so adjust:
# - 5,000 customers with 2 devices = 10,000 devices
# - 5,000 customers with 3 devices = 15,000 devices
# - 10,000 customers with 4 devices = 40,000 devices
# - 20,000 customers with 5 devices = 100,000 devices
# - 10,000 customers with 6 devices = 60,000 devices
# Total: 5k + 5k + 10k + 20k + 10k = 50,000 customers ✓
# Total devices: 10k + 15k + 40k + 100k + 60k = 225,000 devices
# Need 25,000 more devices, so:
# - 5,000 customers with 2 devices = 10,000 devices
# - 5,000 customers with 3 devices = 15,000 devices
# - 5,000 customers with 4 devices = 20,000 devices
# - 25,000 customers with 5 devices = 125,000 devices
# - 10,000 customers with 6 devices = 60,000 devices
# Total: 5k + 5k + 5k + 25k + 10k = 50,000 customers ✓
# Total devices: 10k + 15k + 20k + 125k + 60k = 230,000 devices
# Need 20,000 more devices, so add 20k to customers with 5 devices:
# - 5,000 customers with 2 devices = 10,000 devices
# - 5,000 customers with 3 devices = 15,000 devices
# - 5,000 customers with 4 devices = 20,000 devices
# - 25,000 customers with 5 devices = 125,000 devices
# - 10,000 customers with 6 devices = 60,000 devices
# Actually simpler: All 50,000 customers get exactly 5 devices = 250,000 devices ✓

# Create a natural varied distribution (2-6 devices per customer)
# Use weighted random selection to create variety, then adjust to reach exactly 250,000
devices_per_customer = []
target_total = 250000

# Start with weighted random distribution (favoring middle values)
# Weights: 2=0.1, 3=0.2, 4=0.3, 5=0.3, 6=0.1
for _ in range(50000):
    num_devices = np.random.choice([2, 3, 4, 5, 6], p=[0.1, 0.2, 0.3, 0.3, 0.1])
    devices_per_customer.append(num_devices)

# Adjust to reach exactly 250,000 devices
current_total = sum(devices_per_customer)
difference = target_total - current_total

# Adjust devices to reach target
if difference > 0:
    # Need to add devices
    indices = list(range(50000))
    random.shuffle(indices)
    for idx in indices:
        if difference <= 0:
            break
        devices_per_customer[idx] += 1
        difference -= 1
elif difference < 0:
    # Need to remove devices (but keep at least 2 per customer)
    indices = list(range(50000))
    random.shuffle(indices)
    for idx in indices:
        if difference >= 0:
            break
        if devices_per_customer[idx] > 2:
            devices_per_customer[idx] -= 1
            difference += 1

# Verify final distribution
total_devices = sum(devices_per_customer)
assert total_devices == 250000, f"Expected 250,000 devices, got {total_devices}"
assert len(devices_per_customer) == 50000, f"Expected 50,000 customers, got {len(devices_per_customer)}"

# Generate device records for multi-device customers
for i, cust_id in enumerate(multi_device_customers):
    if (i + 1) % 10000 == 0:
        print(f"  Processed {i + 1}/{len(multi_device_customers)} multi-device customers...")
    
    # Get customer's broadband speed
    cust_speed = customer_df[customer_df['customer_id'] == cust_id]['current_bb_speed'].values[0]
    
    # Get compatible device models
    compatible_models = get_compatible_device_models(cust_speed)
    
    # Generate devices for this customer
    num_devices = devices_per_customer[i]
    for _ in range(num_devices):
        device_model = select_device_model(cust_speed, compatible_models)
        
        device_records.append({
            'customer_id': cust_id,
            'serial_number': generate_unique_serial(),
            'device_model': device_model,
            'device_status': np.random.choice(device_statuses, p=status_probs),
            'isp': np.random.choice(isp_options, p=isp_probs),
            'ship_date': (ship_start + timedelta(days=random.randint(0, ship_date_range))).strftime('%Y-%m-%d'),
            'last_alive_date': generate_last_alive_date(),
            'sqs_score': np.random.choice(sqs_scores, p=sqs_probs)
        })

# Create Device DataFrame
device_df = pd.DataFrame(device_records)

# Verify we have exactly 300,000 device records
assert len(device_df) == 300000, f"Expected 300,000 device records, got {len(device_df)}"

# Save Device Data
device_df.to_csv('Data Output/device_data.csv', index=False)
print(f"\nDevice data generated: {len(device_df)} records")

# Print summary statistics
print("\n" + "="*60)
print("DATA GENERATION SUMMARY")
print("="*60)
print(f"\nCustomer Data: {len(customer_df)} records")
print(f"Device Data: {len(device_df)} records")
print(f"\nCustomer BB Speed Distribution:")
print(customer_df['current_bb_speed'].value_counts(normalize=True).sort_index())
print(f"\nDevice Model Distribution:")
print(device_df['device_model'].value_counts(normalize=True).sort_index())
print(f"\nDevice Status Distribution:")
print(device_df['device_status'].value_counts(normalize=True).sort_index())
print(f"\nCustomers with 1 device: {len(single_device_customers)}")
print(f"Customers with multiple devices: {len(multi_device_customers)}")
print(f"\nDevices per customer stats:")
devices_per_customer = device_df.groupby('customer_id').size()
print(f"  Min: {devices_per_customer.min()}")
print(f"  Max: {devices_per_customer.max()}")
print(f"  Mean: {devices_per_customer.mean():.2f}")
print(f"\nSerial number uniqueness: {len(device_df['serial_number'].unique())} unique serials out of {len(device_df)} records")
print("\n" + "="*60)
print("Generation complete!")
