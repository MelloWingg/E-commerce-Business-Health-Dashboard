
import pandas as pd

def calculate_retention(df):
    df['CohortMonth'] = df.groupby('CustomerID')['InvoiceDate'].transform('min').dt.to_period('M')
    
    current_year = df['InvoiceMonth'].dt.year
    current_month = df['InvoiceMonth'].dt.month

    cohort_year = df['CohortMonth'].dt.year
    cohort_month = df['CohortMonth'].dt.month

    year_diff = current_year - cohort_year
    month_diff = current_month - cohort_month

    df['CohortIndex'] = year_diff * 12 + month_diff + 1
    
    cohort_data = df.groupby(['CohortMonth','CohortIndex'])['CustomerID'].nunique().reset_index()
    
    cohort_matrix = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    cohort_sizes = cohort_matrix.iloc[:, 0]
    retention_matrix = cohort_matrix.divide(cohort_sizes,axis=0) * 100
    retention_matrix = retention_matrix.round(2)
    
    return retention_matrix

def calculate_aov(df):
    df_aov = df.groupby(['InvoiceMonth']).agg({'TotalSum' : sum ,'InvoiceNo' : 'nunique' })
    df_aov['AOV'] = (df_aov['TotalSum'] / df_aov['InvoiceNo']).round(2)
    
    return df_aov

def calculate_mau(df):
    df_mau = df.groupby(['InvoiceMonth'])['CustomerID'].nunique().reset_index()
    
    return df_mau

if __name__ == "__main__":
    # Логіка для тестування:
    # 1. Завантажити 'data/online_retail_clean.csv'
    # 2. Викликати по черзі всі три функції
    # 3. Вивести результати в термінал, щоб переконатися, що все працює
    input_path = "data/online_retail_clean.csv"

    df = pd.read_csv(input_path,parse_dates=['InvoiceDate', 'InvoiceMonth'])
    retention_matrix = calculate_retention(df)
    print(retention_matrix)
    df_aov = calculate_aov(df)
    print(df_aov)
    df_mau = calculate_mau(df)
    print(df_mau)

    pass
