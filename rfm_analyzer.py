import pandas as pd

def score_frequency(x):
    if x == 1:
        return 1
    elif x == 2:
        return 2
    elif x == 3:
        return 3
    elif x == 4:
        return 4
    else:
        return 5
    
def calculate_rfm(df):
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days= 1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate' : max,
        'InvoiceNo': 'nunique',
        'TotalSum' : sum
        }).reset_index()

    rfm.columns = ['CustomerID', 'MaxInvoiceDate', 'Frequency', 'Monetary']
    
    rfm['Recency'] = (snapshot_date - rfm['MaxInvoiceDate']).dt.days
    
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1])
    rfm['F_Score'] = rfm['Frequency'].apply(score_frequency)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
    rfm['RFM_Cell'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['RFM_Score'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
    
    rfm['Segment'] = pd.cut(rfm['RFM_Score'],
                        bins=[2,5,8,11,15],
                        labels=['Lost', 'At Risk', 'Loyal', 'Champions'])

    return rfm

if __name__ == "__main__":

    input_path = "data/online_retail_clean.csv"

    df = pd.read_csv(input_path,parse_dates=['InvoiceDate', 'InvoiceMonth'])
    
    print("--- Розрахунок RFM-сегментації ---")
    rfm_result = calculate_rfm(df)
    print(rfm_result.head())
    print("\nРозподіл клієнтів по сегментах:")
    print(rfm_result['Segment'].value_counts())

