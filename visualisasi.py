# visualisasi.py
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt
import plotly.express as px
import plotly.graph_objects as go

def prepare_data(df):
    df.rename(columns={
        "Rasio": "Rasio 2017",
        "Rasio.1": "Rasio 2018",
        "Dosen": "Dosen 2017",
        "Dosen.1": "Dosen 2018",
        "Mhs": "Mahasiswa 2017",
        "Mhs.1": "Mahasiswa 2018",
        "Nama Prodi": "Nama Perguruan Tinggi",
        "ID_x": "Id Perguruan Tinggi",
        "ID_y": "Id Geometry",
        "kode": "Kode",
        "SUMBER": "Sumber"
    }, inplace=True)
    df['geometry'] = df['geometry'].apply(wkt.loads)
    return df

def generate_map(df, filtered_df):
    frekuensi_prodi = filtered_df.groupby('Provinsi').size().reset_index(name='Jumlah Perguruan Tinggi')
    frekuensi_prodi['Persentase'] = (frekuensi_prodi['Jumlah Perguruan Tinggi'] / frekuensi_prodi['Jumlah Perguruan Tinggi'].sum()) * 100
    df_all_geo = df.drop_duplicates(subset='Provinsi')[['Provinsi', 'geometry']]
    df_freq = df_all_geo.merge(frekuensi_prodi, on='Provinsi', how='left')
    df_freq['Persentase'] = df_freq['Persentase'].fillna(0)
    gdf_freq = gpd.GeoDataFrame(df_freq, geometry='geometry')

    frekuensi_global = df.groupby('Provinsi').size().reset_index(name='Jumlah Perguruan Tinggi')
    frekuensi_global['Persentase'] = (frekuensi_global['Jumlah Perguruan Tinggi'] / frekuensi_global['Jumlah Perguruan Tinggi'].sum()) * 100
    min_persen = frekuensi_global['Persentase'].min()
    max_persen = frekuensi_global['Persentase'].max()

    fig, ax = plt.subplots(figsize=(20, 12))
    gdf_freq.plot(
        column='Persentase',
        cmap='Greens',
        linewidth=0.8,
        edgecolor='0.8',
        legend=True,
        ax=ax,
        vmin=min_persen,
        vmax=max_persen,
        legend_kwds={
            'label': "Persentase Jumlah Perguruan Tinggi (%)",
            'orientation': "vertical",
            'shrink': 0.6,
            'aspect': 20
        }
    )
    for idx, row in gdf_freq.iterrows():
        if row['geometry'].centroid.is_empty:
            continue
        plt.annotate(
            text=row['Provinsi'],
            xy=(row['geometry'].centroid.x, row['geometry'].centroid.y),
            ha='center',
            fontsize=8,
            color='black'
        )

    ax.set_title("Sebaran Persentase Perguruan Tinggi per Provinsi", fontsize=20)
    ax.axis('off')
    plt.tight_layout()
    return fig

def bar_chart(filtered_df):
    pt_per_prov = filtered_df['Provinsi'].value_counts().reset_index()
    pt_per_prov.columns = ['Provinsi', 'Jumlah Perguruan Tinggi']
    fig = px.bar(pt_per_prov, x='Provinsi', y='Jumlah Perguruan Tinggi', color='Jumlah Perguruan Tinggi',
                 title="Jumlah Perguruan Tinggi per Provinsi")
    return fig

def stacked_bar(df):
    df_plot = df[['Provinsi', 'Dosen 2017', 'Mahasiswa 2017', 'Dosen 2018', 'Mahasiswa 2018']].copy()
    if df_plot.empty:
        return go.Figure().update_layout(title="Tidak ada data untuk ditampilkan")
    
    df_grouped = df_plot.groupby('Provinsi').sum().reset_index()
    df_grouped['Total'] = df_grouped[['Dosen 2017', 'Mahasiswa 2017', 'Dosen 2018', 'Mahasiswa 2018']].sum(axis=1)
    df_grouped = df_grouped.sort_values('Total', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_grouped['Provinsi'], y=df_grouped['Dosen 2017'], name='Dosen 2017', marker_color='#1f77b4'))
    fig.add_trace(go.Bar(x=df_grouped['Provinsi'], y=df_grouped['Mahasiswa 2017'], name='Mahasiswa 2017', marker_color='#aec7e8'))
    fig.add_trace(go.Bar(x=df_grouped['Provinsi'], y=df_grouped['Dosen 2018'], name='Dosen 2018', marker_color='#ff7f0e'))
    fig.add_trace(go.Bar(x=df_grouped['Provinsi'], y=df_grouped['Mahasiswa 2018'], name='Mahasiswa 2018', marker_color='#ffbb78'))

    fig.update_layout(
        barmode='stack',
        title='📚 Perbandingan Jumlah Dosen dan Mahasiswa per Provinsi (2017 & 2018)',
        xaxis_title='Provinsi',
        yaxis_title='Jumlah',
        legend_title='Kategori',
        height=600
    )
    return fig

