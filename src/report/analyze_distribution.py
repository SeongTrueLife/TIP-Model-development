import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
INPUT_FILE = r"c:\ms_ai_school\project\Trademark\src\model5\dataset\baseline_result_test_first_test.csv"
OUTPUT_DIR = r"c:\ms_ai_school\project\Trademark\src\report"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_prep_data(filepath):
    """Load data and create group labels."""
    df = pd.read_csv(filepath)
    
    def classify_group(row):
        # Check if case_id starts with 'EN_' (Easy Negative)
        if str(row['case_id']).strip().upper().startswith('EN_'):
            return "Easy Negative"
        # Check result for Precedent cases
        elif str(row['result']).strip() == '유사':
            return "Precedent (Sim)"
        else:
            return "Precedent (Dissim)"
            
    df['group'] = df.apply(classify_group, axis=1)
    
    # Ensure final_score is numeric
    df['final_score'] = pd.to_numeric(df['final_score'], errors='coerce').fillna(0.0)
    
    return df

def plot_distributions(df):
    """Generate KDE and Box plots."""
    
    # Set style
    sns.set_theme(style="whitegrid")
    
    # Define distinct colors
    # Sim (Red), Dissim (Blue), EasyNeg (Green)
    palette = {
        "Precedent (Sim)": "#FF4B4B",      # Red
        "Precedent (Dissim)": "#4B7DFF",   # Blue
        "Easy Negative": "#55B355"         # Green
    }
    
    # Order for plots
    order = ["Easy Negative", "Precedent (Dissim)", "Precedent (Sim)"]
    
    # 1. KDE Plot (Density)
    plt.figure(figsize=(10, 6))
    sns.kdeplot(
        data=df, 
        x='final_score', 
        hue='group', 
        fill=True, 
        palette=palette,
        alpha=0.4,
        linewidth=2,
        hue_order=reversed(order) # Reverse order for legend matching widely
    )
    plt.title('Distribution of Final Scores by Group', fontsize=15)
    plt.xlabel('Final Score (Risk)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.xlim(-0.1, 1.1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dist_kde_score_groups.png"))
    plt.close()
    
    # 2. Box Plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=df, 
        x='final_score', 
        y='group', 
        palette=palette,
        order=order
    )
    plt.title('Score Ranges by Group', fontsize=15)
    plt.xlabel('Final Score (Risk)', fontsize=12)
    plt.ylabel('Group', fontsize=12)
    plt.xlim(-0.1, 1.1)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dist_boxplot_score_groups.png"))
    plt.close()

    # 3. Print Statistics
    print("### Group Statistics")
    stats = df.groupby('group')['final_score'].describe()[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    print(stats)

def main():
    print("Loading data...")
    df = load_and_prep_data(INPUT_FILE)
    
    print(f"Data loaded. Groups found: {df['group'].unique()}")
    
    print("Generating plots...")
    plot_distributions(df)
    print("Done. Images saved to report directory.")

if __name__ == "__main__":
    main()
