import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
INPUT_FILE = r"c:\ms_ai_school\project\Trademark\src\model5\dataset\baseline_result_test_first_test.csv"
OUTPUT_DIR = r"c:\ms_ai_school\project\Trademark\src\report"
REPORT_FILE = os.path.join(OUTPUT_DIR, "test_report_1st(no_train_version).md")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data(filepath):
    """Load and preprocess the dataset."""
    df = pd.read_csv(filepath)
    
    # 1. Ground Truth mapping (result column)
    # '유사' -> 1 (Positive), '비유사' -> 0 (Negative)
    df['gt_binary'] = df['result'].apply(lambda x: 1 if str(x).strip() == '유사' else 0)
    
    # 2. Prediction mapping (risk_level column)
    # Risk Level: High, Medium, Low, Safe
    # We will create 3 binary prediction columns based on thresholds
    
    # Case 1: Low+ (Low, Medium, High are Positive)
    df['pred_low_plus'] = df['risk_level'].apply(lambda x: 1 if x in ['Low', 'Medium', 'High'] else 0)
    
    # Case 2: Medium+ (Medium, High are Positive)
    df['pred_medium_plus'] = df['risk_level'].apply(lambda x: 1 if x in ['Medium', 'High'] else 0)
    
    # Case 3: High+ (High is Positive)
    df['pred_high_plus'] = df['risk_level'].apply(lambda x: 1 if x == 'High' else 0)
    
    return df

def calculate_metrics(y_true, y_pred):
    """Calculate evaluation metrics."""
    return {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1 Score": f1_score(y_true, y_pred, zero_division=0),
        "Confusion Matrix": confusion_matrix(y_true, y_pred)
    }

def plot_confusion_matrix(cm, title, filename):
    """Generate and save confusion matrix plot."""
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Predicted Negative', 'Predicted Positive'],
                yticklabels=['Actual Negative', 'Actual Positive'])
    plt.title(title)
    plt.ylabel('Ground Truth')
    plt.xlabel('Prediction')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def generate_report(metrics_dict, df):
    """Generate the Markdown report content."""
    
    report_content = f"""# Model 5 Performance Analysis Report (1st Test, No Training)

## 1. Overview
- **Dataset Size:** {len(df)} pairs
- **Positive Samples (Sim):** {df['gt_binary'].sum()}
- **Negative Samples (Dissim):** {len(df) - df['gt_binary'].sum()}
- **Evaluation Strategy:** Analyzed performance across three decision boundaries (Low+, Medium+, High+).

## 2. Overall Performance Metrics

| Threshold Criteria | Accuracy | Precision | Recall | F1 Score |
| :--- | :---: | :---: | :---: | :---: |
"""
    
    for label, metrics in metrics_dict.items():
        report_content += f"| **{label}** | {metrics['Accuracy']:.4f} | {metrics['Precision']:.4f} | {metrics['Recall']:.4f} | {metrics['F1 Score']:.4f} |\n"

    report_content += """
---

## 3. Detailed Analysis by Threshold

"""

    for label, metrics in metrics_dict.items():
        cm = metrics['Confusion Matrix']
        tn, fp, fn, tp = cm.ravel()
        
        report_content += f"""### 3.{list(metrics_dict.keys()).index(label) + 1}. Criteria: {label}
- **Definition:** Risk Level `{label.replace('+', '')}` or higher is considered **Similar (Positive)**.
- **Confusion Matrix:**
    - **True Positives (Correctly Initialized Sim):** {tp}
    - **True Negatives (Correctly Identifed Dissim):** {tn}
    - **False Positives (Over-estimated Risk):** {fp}
    - **False Negatives (Under-estimated Risk):** {fn}

**Interpretation:**
"""
        if label == "Low+ (Low/Med/High)":
            report_content += "- Maximizes **Recall** (Safety). Good for initial screening to avoid missing any potential infringement.\n"
        elif label == "Medium+ (Med/High)":
            report_content += "- Balances Recall and Precision. Likely the most balanced operational point.\n"
        elif label == "High+ (High Only)":
            report_content += "- Maximizes **Precision**. Only flags cases with strong evidence (Dominant Part Rule active).\n"
        
        report_content += "\n"

    report_content += """## 4. Error Analysis (Failure Cases)

### 4.1. False Negatives (Missed Infringement) in 'Medium+'
Cases where the model predicted 'Safe/Low' but the actual ruling was 'Sim'.
"""
    # Analyze 'Medium+' False Negatives
    fn_cases = df[(df['gt_binary'] == 1) & (df['pred_medium_plus'] == 0)]
    if not fn_cases.empty:
        report_content += "| Case ID | Target | Cited | Reason (Model Output) | Note |\n|---|---|---|---|---|\n"
        for _, row in fn_cases.head(5).iterrows(): # Show top 5
            reason = str(row.get('judge_reason', 'N/A')).replace('\n', ' ')[:100] + "..."
            report_content += f"| {row['case_id']} | {row['target_text']} | {row['cited_text']} | {reason} | {row.get('note', '')} |\n"
    else:
        report_content += "No False Negatives found for Medium+ threshold.\n"

    report_content += """
### 4.2. False Positives (False Alarm) in 'Medium+'
Cases where the model predicted 'Medium/High' but the actual ruling was 'Dissim'.
"""
    # Analyze 'Medium+' False Positives
    fp_cases = df[(df['gt_binary'] == 0) & (df['pred_medium_plus'] == 1)]
    if not fp_cases.empty:
        report_content += "| Case ID | Target | Cited | Main Factor (User) | Logic Type |\n|---|---|---|---|---|\n"
        for _, row in fp_cases.head(5).iterrows():
            report_content += f"| {row['case_id']} | {row['target_text']} | {row['cited_text']} | {row.get('main_factor', '')} | {row.get('logic_type', '')} |\n"
    else:
        report_content += "No False Positives found for Medium+ threshold.\n"
        
    report_content += """
## 5. Conclusion & Recommendations
- **Summary:** The model performance varies significantly with the chosen threshold.
- **Recommendation:**
    - For a **conservative screening tool** (minimize misses), use **Low+** or **Medium+**.
    - For a **high-confidence alert system**, use **High+**.
"""

    return report_content

def main():
    print("Loading data...")
    df = load_data(INPUT_FILE)
    
    thresholds = {
        "Low+ (Low/Med/High)": df['pred_low_plus'],
        "Medium+ (Med/High)": df['pred_medium_plus'],
        "High+ (High Only)": df['pred_high_plus']
    }
    
    metrics_results = {}
    
    print("Calculating metrics...")
    for label, y_pred in thresholds.items():
        metrics = calculate_metrics(df['gt_binary'], y_pred)
        metrics_results[label] = metrics
        
        # Save confusion matrix plot
        filename = f"confusion_matrix_{label.split()[0].replace('+', '')}.png"
        plot_confusion_matrix(metrics['Confusion Matrix'], f"Confusion Matrix: {label}", filename)
        
    print("Generating report...")
    report_md = generate_report(metrics_results, df)
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
