import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="white")

# Load data
try:
    df = pd.read_csv('src/model5/dataset/baseline_result_train_first_train.csv', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('src/model5/dataset/baseline_result_train_first_train.csv', encoding='cp949')

# Define category logic
def get_category(row):
    # Check for 'Easy Negative' based on logic derived from observation
    # Assuming 'Low' sim_level and 'Dissimilar' result -> Easy Negative
    if row['sim_level'] == 'Low' and row['result'] == '비유사':
        return 'Easy Negative'
    elif row['result'] == '비유사':
        return 'Case Law (Dissimilar)'
    else:
        return 'Case Law (Similar)'

df['category'] = df.apply(get_category, axis=1)

# Melt the dataframe to combine grade columns
grade_cols = ['grade_vis', 'grade_pho', 'grade_sem']
melted_df = df.melt(id_vars=['case_id', 'category'], value_vars=grade_cols, var_name='grade_type', value_name='grade')

# Set up the plot
plt.figure(figsize=(10, 6))

# Define palette
palette = {
    'Case Law (Similar)': '#ff9f43',   # Orange-ish
    'Case Law (Dissimilar)': '#54a0ff', # Blue-ish
    'Easy Negative': '#1dd1a1'          # Green-ish
}

# Plot stacked histogram
# Use discrete=True to center bars on integers
sns.histplot(
    data=melted_df,
    x='grade',
    hue='category',
    multiple='stack',
    palette=palette,
    discrete=True,
    shrink=0.8,
    edgecolor='black'
)

# Customize plot
plt.title('Total Grade Distribution (1-5)', fontsize=14)
plt.xlabel('Grade (1:None, 5:Exclusive)', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.xticks([1, 2, 3, 4, 5])

# Add count labels on top of bars if possible, or just let the y-axis show it.
# The reference image doesn't have labels on bars, just axis.

# Save the plot
output_dir = 'src/report/train_report/node5'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'total_grade_distribution.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Graph saved to {output_path}")

# Also print the counts for verification
print("\nCounts by Grade and Category:")
print(melted_df.groupby(['grade', 'category']).size().unstack(fill_value=0))
print(f"\nTotal count: {len(melted_df)}")
