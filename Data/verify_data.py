import pandas as pd

print("="*60)
print("VERIFYING GENERATED DATA")
print("="*60)

# Verify Customer Data
print("\n1. CUSTOMER DATA VERIFICATION:")
print("-" * 60)
customer_df = pd.read_csv('Data Output/customer_data.csv')
print(f"✓ Total records: {len(customer_df):,}")
print(f"✓ Unique customer IDs: {customer_df['customer_id'].nunique():,}")
print(f"✓ Customer ID range: {customer_df['customer_id'].min()} - {customer_df['customer_id'].max()}")

# Verify distributions
print(f"\n✓ CLV Decile distribution (should be ~10% each):")
clv_dist = customer_df['clv_decile'].value_counts().sort_index()
for decile, count in clv_dist.items():
    print(f"  Decile {decile}: {count:,} ({count/len(customer_df)*100:.1f}%)")

print(f"\n✓ Churn Risk (should be ~2%):")
churn_dist = customer_df['churn_risk'].value_counts()
print(f"  0: {churn_dist[0]:,} ({churn_dist[0]/len(customer_df)*100:.1f}%)")
print(f"  1: {churn_dist[1]:,} ({churn_dist[1]/len(customer_df)*100:.1f}%)")

print(f"\n✓ Broadband Speed distribution:")
speed_dist = customer_df['current_bb_speed'].value_counts()
for speed, count in speed_dist.items():
    print(f"  {speed}: {count:,} ({count/len(customer_df)*100:.1f}%)")

print(f"\n✓ Customer Segment distribution:")
segment_dist = customer_df['customer_segment'].value_counts()
for segment, count in segment_dist.items():
    print(f"  {segment}: {count:,} ({count/len(customer_df)*100:.1f}%)")

# Verify Device Data
print("\n\n2. DEVICE DATA VERIFICATION:")
print("-" * 60)
device_df = pd.read_csv('Data Output/device_data.csv')
print(f"✓ Total records: {len(device_df):,}")
print(f"✓ Unique serial numbers: {device_df['serial_number'].nunique():,}")
print(f"✓ Unique customer IDs: {device_df['customer_id'].nunique():,}")

devices_per_customer = device_df.groupby('customer_id').size()
print(f"\n✓ Devices per customer:")
print(f"  Min: {devices_per_customer.min()}")
print(f"  Max: {devices_per_customer.max()}")
print(f"  Mean: {devices_per_customer.mean():.2f}")

# Count customers with 1 device vs multiple devices
single_device_count = (devices_per_customer == 1).sum()
multi_device_count = (devices_per_customer > 1).sum()
print(f"\n✓ Customers with 1 device: {single_device_count:,}")
print(f"✓ Customers with 2-6 devices: {multi_device_count:,}")

print(f"\n✓ Device Status distribution:")
status_dist = device_df['device_status'].value_counts()
for status, count in status_dist.items():
    print(f"  {status}: {count:,} ({count/len(device_df)*100:.1f}%)")

print(f"\n✓ Device Model distribution:")
model_dist = device_df['device_model'].value_counts()
for model, count in model_dist.items():
    print(f"  {model}: {count:,} ({count/len(device_df)*100:.1f}%)")

print(f"\n✓ ISP distribution:")
isp_dist = device_df['isp'].value_counts()
for isp, count in isp_dist.items():
    print(f"  {isp}: {count:,} ({count/len(device_df)*100:.1f}%)")

print(f"\n✓ SQS Score distribution:")
sqs_dist = device_df['sqs_score'].value_counts().sort_index(ascending=False)
for score, count in sqs_dist.items():
    print(f"  Score {score}: {count:,} ({count/len(device_df)*100:.1f}%)")

# Verify device-customer speed compatibility
print("\n\n3. DEVICE-CUSTOMER SPEED COMPATIBILITY:")
print("-" * 60)
merged = device_df.merge(customer_df[['customer_id', 'current_bb_speed']], on='customer_id', how='left')
print("✓ Checking device model compatibility with customer speeds...")

# Check for incompatible combinations
incompatible = []
for idx, row in merged.iterrows():
    speed = row['current_bb_speed']
    model = row['device_model']
    
    if speed == 'Copper' and model != 'Eero 6':
        incompatible.append((row['customer_id'], speed, model))
    elif speed == '500mb' and model not in ['Eero 6', 'Eero 6+']:
        incompatible.append((row['customer_id'], speed, model))
    # Note: Higher speed customers can have lower speed devices (realistic)

if incompatible:
    print(f"  ⚠ Found {len(incompatible)} potentially incompatible combinations")
    print("  Sample incompatible combinations:")
    for cust_id, speed, model in incompatible[:5]:
        print(f"    Customer {cust_id}: {speed} speed with {model}")
else:
    print("  ✓ All device models are compatible with customer speeds")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
