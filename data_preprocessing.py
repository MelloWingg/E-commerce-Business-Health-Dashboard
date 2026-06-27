import pandas as pd

def clean_data(file_path):
    print("починаємо очищення даних...")

    df = pd.read_excel(file_path)

    df_clean = df.dropna(subset=['CustomerID'])
    df_clean = df_clean.drop_duplicates()
    df_clean = df_clean[df_clean['UnitPrice']>0]
    df_clean = df_clean[df_clean['Quantity']>0]

    df_clean['TotalSum'] = df_clean['UnitPrice'] * df_clean['Quantity']
    df_clean['InvoiceMonth'] = df_clean['InvoiceDate'].dt.to_period('M')

    print("Очищення завершено успішно!")

    return df_clean

if __name__ == "__main__":
    # Цей код спрацює ТІЛЬКИ коли ти запустиш файл напряму.
    # Вказуємо шлях до твого завантаженого файлу
    input_path = "data/Online_Retail.xlsx" 
    output_path = "data/online_retail_clean.csv"
    
    # Викликаємо нашу функцію
    cleaned_df = clean_data(input_path)
    
    # Зберігаємо результат
    cleaned_df.to_csv(output_path, index=False)
    print(f"Чисті дані збережено у {output_path}")