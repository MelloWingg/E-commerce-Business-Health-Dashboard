import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from metrics_calculator import calculate_retention, calculate_aov, calculate_mau
from rfm_analyzer import calculate_rfm

# Налаштування сторінки Streamlit
st.set_page_config(page_title="E-commerce Business Health Dashboard", layout="wide")

st.title("E-commerce Business Health Dashboard")

# Кешування даних, щоб додаток не гальмував при кожному кліку
@st.cache_data
def load_data():
    df = pd.read_csv("data/online_retail_clean.csv", parse_dates=['InvoiceDate', 'InvoiceMonth'])
    return df

df = load_data()

# Навігація в бічному меню
page = st.sidebar.selectbox("Оберіть розділ:", ["Загальні метрики", "RFM Сегментація"])

if page == "Загальні метрики":
    st.header("Основні показники бізнесу")
    
    # 1. Рахуємо метрики через твої функції
    df_mau = calculate_mau(df)
    df_aov = calculate_aov(df)
    
    # 2. Створюємо дві колонки на інтерфейсі
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Щомісячна активність користувачів (MAU)")
        # Тюнінгуємо датафрейм для графіка (робимо місяць індексом)
        mau_chart_data = df_mau.set_index('InvoiceMonth')['CustomerID']
        st.line_chart(mau_chart_data)
        
    with col2:
        st.subheader("Середній чек замовлення (AOV)")
        # Робимо місяць індексом для AOV
        aov_chart_data = df_aov['AOV'] # df_aov вже має InvoiceMonth як індекс після groupby
        st.line_chart(aov_chart_data)

    st.subheader("Когортний аналіз (Retention Rate %)")
    retention_matrix = calculate_retention(df)
    
    # Конвертуємо індекс у текст для коректного відображення на графіку
    retention_matrix.index = retention_matrix.index.astype(str)
    
    # Створюємо фігуру matplotlib
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Малюємо heatmap за допомогою seaborn
    sns.heatmap(
        retention_matrix, 
        annot=True,          # Показувати цифри у клітинках
        fmt=".1f",           # Формат чисел (один знак після коми)
        cmap="YlGnBu",       # Гарна кольорова гама (жовтий-зелений-синій)
        vmax=50,             # Максимум для насиченості кольору (оскільки після 1-го місяця у нас цифри ~30-40%)
        ax=ax
    )
    
    # Передаємо фігуру в Streamlit
    st.pyplot(fig)

elif page == "RFM Сегментація":
    st.header("🎯 Сегментація клієнтів (RFM)")
    
    # 1. Рахуємо RFM
    rfm_df = calculate_rfm(df)
    
    # 2. Рахуємо кількість клієнтів у кожному сегменті
    segment_counts = rfm_df['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Сегмент', 'Кількість клієнтів']
    
    # 3. Відображаємо графік розподілу
    st.subheader("Розподіл клієнтів за сегментами")
    # Перетворюємо для зручності виведення на графік
    st.bar_chart(data=segment_counts, x='Сегмент', y='Кількість клієнтів')
    
    st.markdown("---")
    
    # 4. Створюємо інструмент для завантаження списків клієнтів
    st.subheader("📥 Вивантаження списків для маркетингу")
    st.write("Оберіть сегмент клієнтів або 'Усі користувачі', щоб переглянути їх та завантажити список:")
    
    # Додаємо "Усі користувачі" на початок списку опцій
    options = ['Усі користувачі', 'Champions', 'Loyal', 'At Risk', 'Lost']
    selected_segment = st.selectbox("Оберіть сегмент або повний список:", options)
    
    # Логіка фільтрації: якщо обрано "Усі користувачі", беремо всю таблицю, інакше — фільтруємо
    if selected_segment == 'Усі користувачі':
        filtered_df = rfm_df[['CustomerID', 'Recency', 'Frequency', 'Monetary', 'RFM_Cell', 'Segment']]
        file_name_output = "rfm_all_users.csv"
        button_label = "Завантажити список усіх користувачів в CSV"
    else:
        filtered_df = rfm_df[rfm_df['Segment'] == selected_segment][['CustomerID', 'Recency', 'Frequency', 'Monetary', 'RFM_Cell']]
        file_name_output = f"rfm_{selected_segment.lower()}.csv"
        button_label = f"Завантажити список {selected_segment} в CSV"
    
    # Показуємо прев'ю таблиці (перші 100 рядків)
    st.dataframe(filtered_df.head(100), use_container_width=True)
    
    # Кнопка для завантаження відфільтрованого або повного списку
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=button_label,
        data=csv_data,
        file_name=file_name_output,
        mime="text/csv"
    )