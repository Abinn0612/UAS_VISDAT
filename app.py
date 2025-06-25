# app.py
import streamlit as st
import pandas as pd
from visualisasi import prepare_data, generate_map, bar_chart, stacked_bar

# Load data
df = pd.read_csv("perguruanTinggiIndonesia.csv")
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])
df = prepare_data(df)

# Streamlit Layout
st.set_page_config(layout="wide")
st.title("📊 Dashboard Perguruan Tinggi Indonesia")

# Sidebar filter
st.sidebar.header("🔎 Filter Data Utama")
provinsi = st.sidebar.multiselect("Pilih Provinsi", df['Provinsi'].unique())
penyelenggara = st.sidebar.multiselect("Pilih Penyelenggara", df['Penyelenggara'].unique())
status = st.sidebar.multiselect("Pilih Status", df['Status'].unique())

filtered_df = df.copy()
if provinsi:
    filtered_df = filtered_df[filtered_df['Provinsi'].isin(provinsi)]
if penyelenggara:
    filtered_df = filtered_df[filtered_df['Penyelenggara'].isin(penyelenggara)]
if status:
    filtered_df = filtered_df[filtered_df['Status'].isin(status)]

# Statistik Ringkas
st.subheader("📌 Statistik Ringkas")
col1, col2, col3 = st.columns(3)
col1.metric("Jumlah Penguruan Tinggi", len(filtered_df))
col2.metric("Provinsi Tercakup", filtered_df['Provinsi'].nunique())
col3.markdown("Penyelenggara:  \n" + "<br>".join(filtered_df['Penyelenggara'].unique()), unsafe_allow_html=True)

# Map
st.pyplot(generate_map(df, filtered_df))

# Bar Chart
st.subheader("📍 Jumlah Perguruan Tinggi per Provinsi")
st.plotly_chart(bar_chart(filtered_df), use_container_width=True)

# Stacked Bar
st.subheader("📊 Perbandingan Dosen dan Mahasiswa (Stacked Bar Interaktif)")
st.plotly_chart(stacked_bar(filtered_df), use_container_width=True)

# Table dan Download
st.subheader("📄 Data Lengkap")
search_term = st.text_input("Cari Nama Perguruan Tinggi")
final_filtered_df = filtered_df.copy()
if search_term:
    final_filtered_df = final_filtered_df[final_filtered_df['Nama Perguruan Tinggi'].str.contains(search_term, case=False, na=False)]
st.dataframe(final_filtered_df.drop(columns=['geometry']))
st.download_button("📥 Download Data yang Difilter", final_filtered_df.drop(columns=['geometry']).to_csv(index=False), "filtered_data.csv", "text/csv")