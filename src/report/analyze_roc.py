import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import os

# Configuration
INPUT_FILE = r"c:\ms_ai_school\project\Trademark\src\model5\dataset\baseline_result_test_first_test.csv"
OUTPUT_DIR = r"c:\ms_ai_school\project\Trademark\src\report"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data(filepath):
    df = pd.read_csv(filepath)
    # Ground Truth: '유사' -> 1, Others -> 0
    df['gt_binary'] = df['result'].apply(lambda x: 1 if str(x).strip() == '유사' else 0)
    # Score: Ensure numeric
    df['final_score'] = pd.to_numeric(df['final_score'], errors='coerce').fillna(0.0)
    return df

def plot_roc(df):
    y_true = df['gt_binary']
    y_score = df['final_score']
    
    fpr, tpr, thresholds = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess (AUC = 0.5)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    plt.ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=15)
    plt.legend(loc="lower right", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Annotate some thresholds
    for i, thresh in enumerate(thresholds):
        if i % 10 == 0 or i == len(thresholds)-1: # Sample some points
             plt.annotate(f'{thresh:.2f}', (fpr[i], tpr[i]), textcoords="offset points", xytext=(-10,10), ha='center', fontsize=8)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, "roc_curve.png")
    plt.savefig(output_path)
    plt.close()
    
    print(f"ROC Curve saved to {output_path}")
    print(f"AUC Score: {roc_auc:.4f}")
    return roc_auc

def main():
    print("Loading data...")
    df = load_data(INPUT_FILE)
    
    print("Generating ROC Curve...")
    plot_roc(df)

if __name__ == "__main__":
    main()
