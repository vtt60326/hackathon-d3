import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Number of records
n_records = 300000

print("Generating 300,000 customer records...")

# Generate customer IDs: unique numbers between 1 and 200,000, but can repeat
# Since we need 300,000 records but only 200,000 unique IDs, IDs will repeat
unique_ids = list(range(1, 200001))  # IDs from 1 to 200,000
# Randomly sample with replacement to get 300,000 IDs
ids = np.random.choice(unique_ids, size=n_records, replace=True)

# Generate clv_decile (10% for each value 1-10)
clv_decile = np.repeat(range(1, 11), n_records // 10)
np.random.shuffle(clv_decile)

# Generate churn_risk (2% are 1, 98% are 0)
churn_risk = np.random.choice([0, 1], size=n_records, p=[0.98, 0.02])

# Generate current_bb_speed with exact specified distributions
# 10% Copper (below 500mb), 32% 500mb, 35% 1Gig, 20% 2Gig
# Normalizing to ensure they sum to 100%
speed_categories = [
    'Copper',  # Below 500mb
    '500mb',
    '1Gig',
    '2Gig'
]
# Raw percentages: 10, 32, 35, 20 = 97, normalize to 100%
speed_probabilities = [0.10, 0.32, 0.35, 0.20]
total = sum(speed_probabilities)
speed_probabilities = [p/total for p in speed_probabilities]  # Normalize to sum to 1.0
current_bb_speed = np.random.choice(speed_categories, size=n_records, p=speed_probabilities)

# Generate network_activity (25% heavy, 50% medium, 25% light)
network_activity = np.random.choice(['heavy', 'medium', 'light'], size=n_records, p=[0.25, 0.50, 0.25])

# Generate account_tenure (1 to 120 months)
account_tenure = np.random.randint(1, 121, size=n_records)

# Generate time_of_last_broadband_upgrade (between 1/1/2016 and 11/01/2025)
start_date = datetime(2016, 1, 1)
end_date = datetime(2025, 11, 1)
date_range = (end_date - start_date).days
random_days = np.random.randint(0, date_range + 1, size=n_records)
time_of_last_broadband_upgrade = [
    (start_date + timedelta(days=int(days))).strftime('%Y-%m-%d') 
    for days in random_days
]

# Generate broadband_type (Copper for Copper speed, Fiber for all others)
broadband_type = ['Copper' if speed == 'Copper' else 'Fiber' for speed in current_bb_speed]

# Generate customer_segment with exact specified distributions
# Asipirational Adopters - 6%, Peak Performers - 22%, Budget Balancers - 14%,
# Foolproof Followers - 21%, Settled Simplifiers - 36%
# Normalizing to ensure they sum to 100%
segments = [
    'Asipirational Adopters',  # Note: keeping typo from prompt
    'Peak Performers',
    'Budget Balancers',
    'Foolproof Followers',
    'Settled Simplifiers'
]
# Raw percentages: 6, 22, 14, 21, 36 = 99, normalize to 100%
segment_probabilities = [0.06, 0.22, 0.14, 0.21, 0.36]
total = sum(segment_probabilities)
segment_probabilities = [p/total for p in segment_probabilities]  # Normalize to sum to 1.0
customer_segment = np.random.choice(segments, size=n_records, p=segment_probabilities)

# Create DataFrame
df = pd.DataFrame({
    'customer_id': ids,
    'clv_decile': clv_decile,
    'churn_risk': churn_risk,
    'current_bb_speed': current_bb_speed,
    'network_activity': network_activity,
    'account_tenure': account_tenure,
    'time_of_last_broadband_upgrade': time_of_last_broadband_upgrade,
    'broadband_type': broadband_type,
    'customer_segment': customer_segment
})

# Save to CSV
output_file = 'Data Output/customer_data.csv'
df.to_csv(output_file, index=False)

print(f"\n✓ Successfully generated {len(df):,} customer records!")
print(f"✓ Saved to: {output_file}")

# Print summary statistics
print("\n" + "="*60)
print("DATA SUMMARY")
print("="*60)

print(f"\nTotal Records: {len(df):,}")

print("\nCLV Decile Distribution:")
print(df['clv_decile'].value_counts().sort_index())

print("\nChurn Risk Distribution:")
churn_counts = df['churn_risk'].value_counts()
print(f"  0 (No Risk): {churn_counts[0]:,} ({churn_counts[0]/len(df)*100:.1f}%)")
print(f"  1 (At Risk): {churn_counts[1]:,} ({churn_counts[1]/len(df)*100:.1f}%)")

print("\nBroadband Speed Distribution:")
for speed in df['current_bb_speed'].value_counts().sort_index().items():
    print(f"  {speed[0]}: {speed[1]:,} ({speed[1]/len(df)*100:.1f}%)")

print("\nNetwork Activity Distribution:")
for activity in df['network_activity'].value_counts().items():
    print(f"  {activity[0]}: {activity[1]:,} ({activity[1]/len(df)*100:.1f}%)")

print("\nBroadband Type Distribution:")
for bb_type in df['broadband_type'].value_counts().items():
    print(f"  {bb_type[0]}: {bb_type[1]:,} ({bb_type[1]/len(df)*100:.1f}%)")

print("\nCustomer Segment Distribution:")
for segment in df['customer_segment'].value_counts().items():
    print(f"  {segment[0]}: {segment[1]:,} ({segment[1]/len(df)*100:.1f}%)")

print("\nAccount Tenure Statistics:")
print(f"  Min: {df['account_tenure'].min()} months")
print(f"  Max: {df['account_tenure'].max()} months")
print(f"  Mean: {df['account_tenure'].mean():.1f} months")
print(f"  Median: {df['account_tenure'].median():.1f} months")

print("\nDate Range for Last Broadband Upgrade:")
print(f"  Earliest: {df['time_of_last_broadband_upgrade'].min()}")
print(f"  Latest: {df['time_of_last_broadband_upgrade'].max()}")

print("\n" + "="*60)
print("✓ Data generation complete!")
print("="*60)
