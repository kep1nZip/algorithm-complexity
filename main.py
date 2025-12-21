import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple
import random
import sys
import numpy as np
import math
from functools import lru_cache

# ==================== OPTIMASI SISTEM RECURSION ====================
sys.setrecursionlimit(1000000)

# ==================== ALGORITMA LINEAR SEARCH ====================

def linear_search_iteratif(products: List[str], keyword: str, mode: str = "first") -> Tuple:
    """Linear Search versi iteratif dengan optimasi kecepatan"""
    comparisons = 0
    keyword_lower = keyword.lower()
    
    if mode == "first":
        for i, product in enumerate(products):
            comparisons += 1
            if keyword_lower in product.lower():
                return i, comparisons
        return -1, comparisons
    else:
        found_indexes = []
        found_products = []
        for i, product in enumerate(products):
            comparisons += 1
            if keyword_lower in product.lower():
                found_indexes.append(i)
                found_products.append(product)
        return found_indexes, comparisons, found_products

def linear_search_rekursif_optimized(products: List[str], keyword: str, 
                                    start: int = 0, comparisons: int = 0,
                                    memo: dict = None) -> Tuple[int, int]:
    """Linear Search rekursif dengan optimasi"""
    if memo is None:
        memo = {'keyword_lower': keyword.lower()}
    
    if start >= len(products):
        return -1, comparisons
    
    comparisons += 1
    if memo['keyword_lower'] in products[start].lower():
        return start, comparisons
    
    return linear_search_rekursif_optimized(products, keyword, start + 1, comparisons, memo)

def linear_search_rekursif_trampoline(products: List[str], keyword: str) -> Tuple[int, int]:
    """Trampoline pattern untuk menghindari recursion depth limit"""
    keyword_lower = keyword.lower()
    comparisons = 0
    
    def search_helper(index: int):
        nonlocal comparisons
        if index >= len(products):
            return -1, comparisons
        comparisons += 1
        if keyword_lower in products[index].lower():
            return index, comparisons
        return search_helper(index + 1)
    
    return search_helper(0)

# ==================== GENERATOR DATA ====================

@lru_cache(maxsize=5)
def generate_product_names_cached(n: int, seed: int = 42) -> List[str]:
    """Generate nama produk dengan caching"""
    categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                  'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
    brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
              'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
    adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                  'Portable', 'Professional', 'Advanced', 'Smart']
    
    random.seed(seed)
    return [
        f"{random.choice(brands)} {random.choice(categories)} {random.choice(adjectives)} {random.randint(1, 999)}"
        for _ in range(n)
    ]

def generate_product_names_fast(n: int, consistent: bool = False) -> List[str]:
    """Generate produk dengan performa tinggi"""
    if consistent:
        return generate_product_names_cached(n, 42)
    else:
        return generate_product_names_cached(n, random.randint(1, 1000000))

# ==================== METRIK ANALISIS COLUMN-BASED ====================

def calculate_efficiency_columns(iter_time: float, rek_time: float, 
                               iter_comps: int, rek_comps: int,
                               size: int) -> dict:
    """
    Hitung skor efisiensi untuk column visualization
    """
    scores = {}
    
    # 1. Kecepatan Score (dari speedup)
    if iter_time > 0 and rek_time > 0:
        speedup = rek_time / iter_time
        speed_score = min(100, speedup * 25)
    else:
        speed_score = 0
    scores['Kecepatan'] = round(speed_score, 1)
    
    # 2. Memori Efficiency
    if size > 0 and iter_comps > 0:
        memory_ratio = (rek_comps * 0.001) / (iter_comps * 0.0001)
        memory_score = max(0, 100 - (memory_ratio * 10))
    else:
        memory_score = 50
    scores['Memori'] = round(memory_score, 1)
    
    # 3. Stabilitas Score
    stability_score = 80
    if rek_comps > 10000:
        stability_score -= 20
    scores['Stabilitas'] = round(stability_score, 1)
    
    # 4. Simplicity Score
    scores['Kesederhanaan'] = 60.0
    
    # Total Score
    scores['Total'] = round(sum([scores['Kecepatan'] * 0.4,
                                 scores['Memori'] * 0.3,
                                 scores['Stabilitas'] * 0.2,
                                 scores['Kesederhanaan'] * 0.1]), 1)
    
    # Additional metrics for columns
    scores['Speedup'] = round(rek_time / iter_time, 2) if iter_time > 0 else 0
    scores['Time_Diff'] = round(abs(iter_time - rek_time), 4)
    scores['Ops_Iter'] = round(size / (iter_time / 1000) if iter_time > 0 else 0, 0)
    scores['Ops_Rek'] = round(size / (rek_time / 1000) if rek_time > 0 else 0, 0)
    
    return scores

def calculate_all_metrics(df_results: pd.DataFrame) -> pd.DataFrame:
    """Hitung semua metrik untuk column visualization"""
    metrics_list = []
    
    for _, row in df_results.iterrows():
        if pd.isna(row['Iteratif Worst (ms)']) or pd.isna(row['Rekursif Worst (ms)']):
            continue
            
        size = row['Ukuran Data']
        iter_time = row['Iteratif Worst (ms)']
        rek_time = row['Rekursif Worst (ms)']
        iter_comps = row['Iter Worst Comp']
        rek_comps = row['Rek Worst Comp']
        
        # Calculate column metrics
        metrics = calculate_efficiency_columns(iter_time, rek_time, iter_comps, rek_comps, size)
        
        metrics_list.append({
            'Ukuran Data': size,
            'Waktu Iteratif (ms)': iter_time,
            'Waktu Rekursif (ms)': rek_time,
            'Perbandingan Iteratif': iter_comps,
            'Perbandingan Rekursif': rek_comps,
            'Speedup': metrics['Speedup'],
            'Selisih Waktu (ms)': metrics['Time_Diff'],
            'Ops/detik Iteratif': metrics['Ops_Iter'],
            'Ops/detik Rekursif': metrics['Ops_Rek'],
            'Skor Total': metrics['Total'],
            'Skor Kecepatan': metrics['Kecepatan'],
            'Skor Memori': metrics['Memori'],
            'Skor Stabilitas': metrics['Stabilitas'],
            'Skor Kesederhanaan': metrics['Kesederhanaan']
        })
    
    return pd.DataFrame(metrics_list)

# ==================== VISUALISASI COLUMN-BASED ====================

def create_time_comparison_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk perbandingan waktu"""
    fig = go.Figure()
    
    # Bar untuk Iteratif
    fig.add_trace(go.Bar(
        name='Iteratif',
        x=[f"{size:,}" for size in df_metrics['Ukuran Data']],
        y=df_metrics['Waktu Iteratif (ms)'],
        marker_color='#1E90FF',
        hovertemplate='<b>Iteratif</b><br>Size: %{x}<br>Time: %{y:.4f} ms<extra></extra>',
        text=[f"{t:.2f} ms" for t in df_metrics['Waktu Iteratif (ms)']],
        textposition='outside'
    ))
    
    # Bar untuk Rekursif
    fig.add_trace(go.Bar(
        name='Rekursif',
        x=[f"{size:,}" for size in df_metrics['Ukuran Data']],
        y=df_metrics['Waktu Rekursif (ms)'],
        marker_color='#FF6B6B',
        hovertemplate='<b>Rekursif</b><br>Size: %{x}<br>Time: %{y:.4f} ms<extra></extra>',
        text=[f"{t:.2f} ms" for t in df_metrics['Waktu Rekursif (ms)']],
        textposition='outside'
    ))
    
    # Tambah line untuk average
    avg_iter = df_metrics['Waktu Iteratif (ms)'].mean()
    avg_rek = df_metrics['Waktu Rekursif (ms)'].mean()
    
    fig.add_hline(y=avg_iter, line_dash="dash", line_color="#1E90FF", 
                  annotation_text=f"Avg Iter: {avg_iter:.2f}ms",
                  annotation_position="top left")
    
    fig.add_hline(y=avg_rek, line_dash="dash", line_color="#FF6B6B",
                  annotation_text=f"Avg Rek: {avg_rek:.2f}ms",
                  annotation_position="top right")
    
    fig.update_layout(
        title='⏱️ Perbandingan Waktu Eksekusi (Column Chart)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Waktu (ms)",
        barmode='group',
        height=500,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_operations_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk jumlah operasi"""
    fig = go.Figure()
    
    # Prepare data
    sizes = [f"{size:,}" for size in df_metrics['Ukuran Data']]
    
    # Bar untuk Perbandingan
    fig.add_trace(go.Bar(
        name='Perbandingan Iteratif',
        x=sizes,
        y=df_metrics['Perbandingan Iteratif'],
        marker_color='#2E86AB',
        hovertemplate='<b>Iteratif</b><br>Size: %{x}<br>Comparisons: %{y:,}<extra></extra>',
        text=[f"{c:,}" for c in df_metrics['Perbandingan Iteratif']],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Perbandingan Rekursif',
        x=sizes,
        y=df_metrics['Perbandingan Rekursif'],
        marker_color='#A23B72',
        hovertemplate='<b>Rekursif</b><br>Size: %{x}<br>Comparisons: %{y:,}<extra></extra>',
        text=[f"{c:,}" for c in df_metrics['Perbandingan Rekursif']],
        textposition='outside'
    ))
    
    # Tambah line untuk ideal O(n) line
    max_size = df_metrics['Ukuran Data'].max()
    fig.add_trace(go.Scatter(
        x=sizes,
        y=df_metrics['Ukuran Data'],
        mode='lines',
        name='Ideal O(n)',
        line=dict(color='#32CD32', width=3, dash='dot'),
        hovertemplate='Ideal O(n)<br>Size: %{x}<br>n = %{y:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🔢 Jumlah Operasi Perbandingan (Column Chart)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Jumlah Perbandingan",
        barmode='group',
        height=500,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_efficiency_score_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk skor efisiensi"""
    fig = go.Figure()
    
    # Prepare data - kita akan buat grouped bar untuk 5 skor berbeda
    sizes = [f"{size:,}" for size in df_metrics['Ukuran Data']]
    
    # Warna untuk setiap skor
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    
    # Skor Total
    fig.add_trace(go.Bar(
        name='Skor Total',
        x=sizes,
        y=df_metrics['Skor Total'],
        marker_color=colors[0],
        hovertemplate='<b>Total Score</b><br>Size: %{x}<br>Score: %{y:.1f}/100<extra></extra>',
        text=[f"{s:.1f}" for s in df_metrics['Skor Total']],
        textposition='outside'
    ))
    
    # Skor Kecepatan
    fig.add_trace(go.Bar(
        name='Skor Kecepatan',
        x=sizes,
        y=df_metrics['Skor Kecepatan'],
        marker_color=colors[1],
        hovertemplate='<b>Kecepatan Score</b><br>Size: %{x}<br>Score: %{y:.1f}<extra></extra>',
        text=[f"{s:.1f}" for s in df_metrics['Skor Kecepatan']],
        textposition='outside'
    ))
    
    # Skor Memori
    fig.add_trace(go.Bar(
        name='Skor Memori',
        x=sizes,
        y=df_metrics['Skor Memori'],
        marker_color=colors[2],
        hovertemplate='<b>Memory Score</b><br>Size: %{x}<br>Score: %{y:.1f}<extra></extra>',
        text=[f"{s:.1f}" for s in df_metrics['Skor Memori']],
        textposition='outside'
    ))
    
    # Skor Stabilitas
    fig.add_trace(go.Bar(
        name='Skor Stabilitas',
        x=sizes,
        y=df_metrics['Skor Stabilitas'],
        marker_color=colors[3],
        hovertemplate='<b>Stability Score</b><br>Size: %{x}<br>Score: %{y:.1f}<extra></extra>',
        text=[f"{s:.1f}" for s in df_metrics['Skor Stabilitas']],
        textposition='outside'
    ))
    
    # Skor Kesederhanaan
    fig.add_trace(go.Bar(
        name='Skor Kesederhanaan',
        x=sizes,
        y=df_metrics['Skor Kesederhanaan'],
        marker_color=colors[4],
        hovertemplate='<b>Simplicity Score</b><br>Size: %{x}<br>Score: %{y:.1f}<extra></extra>',
        text=[f"{s:.1f}" for s in df_metrics['Skor Kesederhanaan']],
        textposition='outside'
    ))
    
    # Tambah reference line untuk threshold
    fig.add_hline(y=70, line_dash="dash", line_color="green",
                  annotation_text="Good Threshold (70+)",
                  annotation_position="bottom left")
    
    fig.add_hline(y=50, line_dash="dot", line_color="orange",
                  annotation_text="Average Threshold (50)",
                  annotation_position="bottom right")
    
    fig.update_layout(
        title='🏆 Skor Efisiensi Multi-Dimensi (Column Chart)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Skor (0-100)",
        barmode='group',
        height=600,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_throughput_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk throughput (ops/detik)"""
    fig = go.Figure()
    
    sizes = [f"{size:,}" for size in df_metrics['Ukuran Data']]
    
    # Bar untuk Throughput Iteratif
    fig.add_trace(go.Bar(
        name='Throughput Iteratif',
        x=sizes,
        y=df_metrics['Ops/detik Iteratif'],
        marker_color='#1E90FF',
        hovertemplate='<b>Iteratif Throughput</b><br>Size: %{x}<br>Ops/detik: %{y:,.0f}<extra></extra>',
        text=[f"{o:,.0f}/s" for o in df_metrics['Ops/detik Iteratif']],
        textposition='outside'
    ))
    
    # Bar untuk Throughput Rekursif
    fig.add_trace(go.Bar(
        name='Throughput Rekursif',
        x=sizes,
        y=df_metrics['Ops/detik Rekursif'],
        marker_color='#FF6B6B',
        hovertemplate='<b>Rekursif Throughput</b><br>Size: %{x}<br>Ops/detik: %{y:,.0f}<extra></extra>',
        text=[f"{o:,.0f}/s" for o in df_metrics['Ops/detik Rekursif']],
        textposition='outside'
    ))
    
    # Calculate efficiency ratio
    efficiency_ratio = (df_metrics['Ops/detik Iteratif'] / df_metrics['Ops/detik Rekursif']).mean()
    
    fig.add_annotation(
        x=0.5, y=0.95, xref="paper", yref="paper",
        text=f"Efficiency Ratio: {efficiency_ratio:.2f}x",
        showarrow=False,
        font=dict(size=12, color="green")
    )
    
    fig.update_layout(
        title='⚡ Throughput (Operasi per Detik)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Operasi per Detik",
        barmode='group',
        height=500,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_speedup_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk speedup"""
    fig = go.Figure()
    
    sizes = [f"{size:,}" for size in df_metrics['Ukuran Data']]
    
    # Bar untuk Speedup
    fig.add_trace(go.Bar(
        name='Speedup (Iteratif/Rekursif)',
        x=sizes,
        y=df_metrics['Speedup'],
        marker_color='#32CD32',
        hovertemplate='<b>Speedup</b><br>Size: %{x}<br>Speedup: %{y:.2f}x<extra></extra>',
        text=[f"{s:.2f}x" for s in df_metrics['Speedup']],
        textposition='outside',
        marker=dict(
            color=df_metrics['Speedup'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Speedup")
        )
    ))
    
    # Tambah reference line
    fig.add_hline(y=1.0, line_dash="solid", line_color="red",
                  annotation_text="Break-even Point",
                  annotation_position="top right")
    
    fig.add_hline(y=df_metrics['Speedup'].mean(), line_dash="dash", line_color="blue",
                  annotation_text=f"Average: {df_metrics['Speedup'].mean():.2f}x",
                  annotation_position="bottom right")
    
    fig.update_layout(
        title='📈 Speedup Analysis (Iteratif vs Rekursif)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Speedup (x)",
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_performance_trend_chart(df_metrics: pd.DataFrame):
    """Buat line chart untuk tren performa (INI SATU-SATUNYA YANG LINE CHART)"""
    fig = go.Figure()
    
    # Line untuk Speedup Trend
    fig.add_trace(go.Scatter(
        x=df_metrics['Ukuran Data'],
        y=df_metrics['Speedup'],
        mode='lines+markers',
        name='Speedup Trend',
        line=dict(color='#32CD32', width=3),
        marker=dict(size=10),
        hovertemplate='<b>Speedup Trend</b><br>Size: %{x:,}<br>Speedup: %{y:.2f}x<extra></extra>'
    ))
    
    # Line untuk Total Score Trend
    fig.add_trace(go.Scatter(
        x=df_metrics['Ukuran Data'],
        y=df_metrics['Skor Total'],
        mode='lines+markers',
        name='Total Score Trend',
        line=dict(color='#FF6B6B', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='<b>Total Score Trend</b><br>Size: %{x:,}<br>Score: %{y:.1f}<extra></extra>',
        yaxis='y2'
    ))
    
    # Calculate trend lines
    if len(df_metrics) > 1:
        # Linear regression untuk speedup
        x = df_metrics['Ukuran Data'].values
        y_speedup = df_metrics['Speedup'].values
        coeffs_speedup = np.polyfit(x, y_speedup, 1)
        trend_speedup = np.poly1d(coeffs_speedup)
        
        fig.add_trace(go.Scatter(
            x=x,
            y=trend_speedup(x),
            mode='lines',
            name='Speedup Trend Line',
            line=dict(color='#32CD32', width=2, dash='dot'),
            hovertemplate='Trend Line<extra></extra>'
        ))
    
    fig.update_layout(
        title='📊 Tren Performa vs Ukuran Dataset (Line Chart)',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Speedup (x)",
        yaxis2=dict(
            title="Skor Total",
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        height=500,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_comparison_matrix(df_metrics: pd.DataFrame):
    """Buat matrix column chart untuk perbandingan semua metrik"""
    # Pilih 4 metrik utama untuk matrix
    metrics_to_show = ['Waktu Iteratif (ms)', 'Waktu Rekursif (ms)', 
                      'Speedup', 'Skor Total']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[f'📊 {metric}' for metric in metrics_to_show],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    sizes = [f"{size:,}" for size in df_metrics['Ukuran Data']]
    
    # Plot 1: Waktu Iteratif
    fig.add_trace(
        go.Bar(
            x=sizes,
            y=df_metrics['Waktu Iteratif (ms)'],
            name='Waktu Iteratif',
            marker_color='#1E90FF',
            hovertemplate='Size: %{x}<br>Time: %{y:.2f} ms<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Plot 2: Waktu Rekursif
    fig.add_trace(
        go.Bar(
            x=sizes,
            y=df_metrics['Waktu Rekursif (ms)'],
            name='Waktu Rekursif',
            marker_color='#FF6B6B',
            hovertemplate='Size: %{x}<br>Time: %{y:.2f} ms<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Plot 3: Speedup
    fig.add_trace(
        go.Bar(
            x=sizes,
            y=df_metrics['Speedup'],
            name='Speedup',
            marker_color='#32CD32',
            hovertemplate='Size: %{x}<br>Speedup: %{y:.2f}x<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Plot 4: Skor Total
    fig.add_trace(
        go.Bar(
            x=sizes,
            y=df_metrics['Skor Total'],
            name='Skor Total',
            marker_color='#FFA500',
            hovertemplate='Size: %{x}<br>Score: %{y:.1f}<extra></extra>'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title='🔍 Comparison Matrix: 4 Metrik Utama',
        height=700,
        template='plotly_white',
        showlegend=False,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_yaxes(title_text="Waktu (ms)", row=1, col=1)
    fig.update_yaxes(title_text="Waktu (ms)", row=1, col=2)
    fig.update_yaxes(title_text="Speedup (x)", row=2, col=1)
    fig.update_yaxes(title_text="Skor (0-100)", row=2, col=2)
    
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 12
    
    return fig

# ==================== PERFORMANCE TEST ====================

def run_performance_test_with_columns(sizes: List[int], keyword: str = "Gaming", 
                                     consistent: bool = False) -> pd.DataFrame:
    """Menjalankan pengujian performa untuk column visualization"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, size in enumerate(sorted(sizes)):
        status_text.text(f"Testing size {size:,}... ({idx+1}/{len(sizes)})")
        progress_bar.progress((idx + 1) / len(sizes))
        
        # Generate dataset
        products = generate_product_names_fast(size, consistent)
        
        # Setup worst case
        if size > 0:
            products_worst = products.copy()
            products_worst[-1] = f"Apple {keyword} MacBook Ultra 2024"
        else:
            products_worst = products
        
        # Test Iteratif
        start = time.perf_counter()
        idx_iter, comp_iter = linear_search_iteratif(products_worst, keyword, "first")
        time_iter = (time.perf_counter() - start) * 1000
        
        # Test Rekursif
        if size <= 10000:
            start = time.perf_counter()
            try:
                idx_rek, comp_rek = linear_search_rekursif_optimized(products_worst, keyword)
                time_rek = (time.perf_counter() - start) * 1000
            except RecursionError:
                time_rek = None
                comp_rek = None
        else:
            start = time.perf_counter()
            idx_rek, comp_rek = linear_search_rekursif_trampoline(products_worst, keyword)
            time_rek = (time.perf_counter() - start) * 1000
        
        results.append({
            'Ukuran Data': size,
            'Iteratif Worst (ms)': time_iter,
            'Rekursif Worst (ms)': time_rek,
            'Iter Worst Comp': comp_iter,
            'Rek Worst Comp': comp_rek,
        })
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

# ==================== MAIN APP ====================

def main():
    st.title("📊 Dashboard Analisis Linear Search - Column Visualization")
    st.markdown("### Semua Analisis Menggunakan Column Charts (Kecuali Tren)")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        num_products = st.slider(
            "Jumlah Produk Demo",
            min_value=100,
            max_value=50000,
            value=5000,
            step=1000
        )
        
        keyword = st.text_input("Keyword Pencarian", "Gaming")
        
        st.markdown("---")
        
        st.markdown("### 📈 Performance Testing")
        
        test_sizes = st.multiselect(
            "Pilih Ukuran untuk Analisis:",
            [100, 500, 1000, 2500, 5000, 10000, 25000, 50000],
            default=[100, 1000, 5000, 10000, 25000, 50000]
        )
        
        st.markdown("---")
        
        st.markdown("### 🎨 Tipe Column Charts")
        
        chart_selection = st.multiselect(
            "Pilih Chart untuk Ditampilkan:",
            ["⏱️ Perbandingan Waktu", "🔢 Jumlah Operasi", "🏆 Skor Efisiensi", 
             "⚡ Throughput", "📈 Speedup", "🔍 Comparison Matrix"],
            default=["⏱️ Perbandingan Waktu", "🏆 Skor Efisiensi", "📈 Speedup"]
        )
        
        st.markdown("---")
        
        st.info("""
        **📊 Visualization Strategy:**
        
        **Column Charts untuk:**
        - ⏱️ Perbandingan Waktu
        - 🔢 Jumlah Operasi
        - 🏆 Skor Efisiensi
        - ⚡ Throughput
        - 📈 Speedup
        
        **Line Chart HANYA untuk:**
        - 📊 Tren Performa
        """)
    
    # Main container
    main_container = st.container()
    
    with main_container:
        # ===== DEMO SINGLE SIZE =====
        st.header("🎯 Demo Single Size Analysis")
        
        if st.button(f"🚀 Analisis {num_products:,} Produk", type="primary", use_container_width=True):
            st.markdown("---")
            
            # Generate dataset
            with st.spinner(f"Generating {num_products:,} produk..."):
                products = generate_product_names_fast(num_products, consistent=True)
                products[-1] = f"Apple {keyword} MacBook Ultra 2024"
            
            # Run algorithms
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔄 Iteratif")
                start = time.perf_counter()
                idx_iter, comp_iter = linear_search_iteratif(products, keyword, "first")
                time_iter = (time.perf_counter() - start) * 1000
                
                st.metric("Waktu", f"{time_iter:.4f} ms")
                st.metric("Perbandingan", f"{comp_iter:,}")
                st.metric("Ops/detik", f"{num_products/(time_iter/1000):,.0f}")
            
            with col2:
                st.subheader("🔁 Rekursif")
                if num_products <= 10000:
                    func = linear_search_rekursif_optimized
                else:
                    func = linear_search_rekursif_trampoline
                
                start = time.perf_counter()
                idx_rek, comp_rek = func(products, keyword)
                time_rek = (time.perf_counter() - start) * 1000
                
                st.metric("Waktu", f"{time_rek:.4f} ms")
                st.metric("Perbandingan", f"{comp_rek:,}")
                st.metric("Ops/detik", f"{num_products/(time_rek/1000):,.0f}")
            
            # Calculate metrics
            metrics = calculate_efficiency_columns(time_iter, time_rek, comp_iter, comp_rek, num_products)
            
            # Display metrics in columns
            st.markdown("---")
            st.subheader("📊 Performance Metrics")
            
            metric_cols = st.columns(4)
            with metric_cols[0]:
                st.metric("Speedup", f"{metrics['Speedup']:.2f}x")
            with metric_cols[1]:
                st.metric("Skor Total", f"{metrics['Total']:.1f}/100")
            with metric_cols[2]:
                st.metric("Skor Kecepatan", f"{metrics['Kecepatan']:.1f}")
            with metric_cols[3]:
                st.metric("Skor Memori", f"{metrics['Memori']:.1f}")
        
        # ===== MULTI-SIZE ANALYSIS =====
        if test_sizes:
            st.markdown("---")
            st.header("📈 Multi-Size Performance Analysis")
            
            if st.button("🚀 Jalankan Analisis Multi-Size", type="primary", use_container_width=True):
                with st.spinner("Menjalankan analisis multi-size..."):
                    df_results = run_performance_test_with_columns(
                        sorted(test_sizes), 
                        keyword, 
                        consistent=True
                    )
                    
                    df_metrics = calculate_all_metrics(df_results)
                
                # Display summary stats
                st.markdown("### 📊 Summary Statistics")
                
                summary_cols = st.columns(4)
                with summary_cols[0]:
                    st.metric("Rata-rata Speedup", f"{df_metrics['Speedup'].mean():.2f}x")
                with summary_cols[1]:
                    st.metric("Skor Efisiensi Rata", f"{df_metrics['Skor Total'].mean():.1f}")
                with summary_cols[2]:
                    st.metric("Max Size Tested", f"{df_metrics['Ukuran Data'].max():,}")
                with summary_cols[3]:
                    st.metric("Total Tests", len(df_metrics))
                
                # Display selected charts
                if "⏱️ Perbandingan Waktu" in chart_selection:
                    st.markdown("---")
                    st.subheader("⏱️ Perbandingan Waktu Eksekusi")
                    time_fig = create_time_comparison_column_chart(df_metrics)
                    st.plotly_chart(time_fig, use_container_width=True)
                
                if "🔢 Jumlah Operasi" in chart_selection:
                    st.markdown("---")
                    st.subheader("🔢 Jumlah Operasi Perbandingan")
                    ops_fig = create_operations_column_chart(df_metrics)
                    st.plotly_chart(ops_fig, use_container_width=True)
                
                if "🏆 Skor Efisiensi" in chart_selection:
                    st.markdown("---")
                    st.subheader("🏆 Skor Efisiensi Multi-Dimensi")
                    score_fig = create_efficiency_score_column_chart(df_metrics)
                    st.plotly_chart(score_fig, use_container_width=True)
                
                if "⚡ Throughput" in chart_selection:
                    st.markdown("---")
                    st.subheader("⚡ Throughput (Operasi per Detik)")
                    throughput_fig = create_throughput_column_chart(df_metrics)
                    st.plotly_chart(throughput_fig, use_container_width=True)
                
                if "📈 Speedup" in chart_selection:
                    st.markdown("---")
                    st.subheader("📈 Speedup Analysis")
                    speedup_fig = create_speedup_column_chart(df_metrics)
                    st.plotly_chart(speedup_fig, use_container_width=True)
                
                if "🔍 Comparison Matrix" in chart_selection:
                    st.markdown("---")
                    st.subheader("🔍 Comparison Matrix: 4 Metrik Utama")
                    matrix_fig = create_comparison_matrix(df_metrics)
                    st.plotly_chart(matrix_fig, use_container_width=True)
                
                # TREN PERFORMANCE - SATU-SATUNYA LINE CHART
                st.markdown("---")
                st.subheader("📊 Tren Performa vs Ukuran Dataset")
                st.info("⚠️ **INI SATU-SATUNYA LINE CHART** - Menunjukkan trend performa")
                trend_fig = create_performance_trend_chart(df_metrics)
                st.plotly_chart(trend_fig, use_container_width=True)
                
                # Detailed metrics table
                st.markdown("---")
                st.subheader("📋 Detailed Metrics Table")
                
                # Format table for display
                display_df = df_metrics.copy()
                display_df['Ukuran Data'] = display_df['Ukuran Data'].apply(lambda x: f"{x:,}")
                
                format_config = {
                    'Waktu Iteratif (ms)': '{:.4f}',
                    'Waktu Rekursif (ms)': '{:.4f}',
                    'Speedup': '{:.2f}x',
                    'Ops/detik Iteratif': '{:,.0f}',
                    'Ops/detik Rekursif': '{:,.0f}',
                    'Skor Total': '{:.1f}',
                    'Skor Kecepatan': '{:.1f}',
                    'Skor Memori': '{:.1f}',
                    'Skor Stabilitas': '{:.1f}',
                    'Skor Kesederhanaan': '{:.1f}'
                }
                
                for col, fmt in format_config.items():
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: fmt.format(x))
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400
                )
                
                # Insights
                st.markdown("---")
                st.subheader("🔍 Insights & Recommendations")
                
                insight_cols = st.columns(3)
                
                with insight_cols[0]:
                    best_speedup = df_metrics['Speedup'].max()
                    best_size = df_metrics.loc[df_metrics['Speedup'].idxmax(), 'Ukuran Data']
                    st.success(f"**Best Speedup**\n\n{best_speedup:.2f}x\nat {best_size:,} products")
                
                with insight_cols[1]:
                    best_score = df_metrics['Skor Total'].max()
                    best_score_size = df_metrics.loc[df_metrics['Skor Total'].idxmax(), 'Ukuran Data']
                    st.info(f"**Best Efficiency**\n\nScore: {best_score:.1f}\nat {best_score_size:,} products")
                
                with insight_cols[2]:
                    avg_ops = df_metrics['Ops/detik Iteratif'].mean()
                    st.warning(f"**Avg Throughput**\n\n{avg_ops:,.0f} ops/sec\nIteratif lebih konsisten")
        
        # ===== PENJELASAN VISUALISASI =====
        st.markdown("---")
        st.header("📚 Column vs Line Visualization")
        
        with st.expander("🎯 Mengapa Column Charts Dominan?", expanded=True):
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.markdown("""
                **✅ Keunggulan Column Charts:**
                
                1. **Direct Comparison** - Mudah bandingkan nilai
                2. **Discrete Data** - Ukuran dataset diskrit
                3. **Exact Values** - Tinggi bar = nilai pasti
                4. **Grouping** - Bisa grup multiple series
                5. **Visual Impact** - Lebih eye-catching
                
                **🎯 Cocok untuk:**
                - Perbandingan 2+ algoritma
                - Data kategori/diskrit
                - Nilai absolut
                - Side-by-side comparison
                """)
            
            with col_exp2:
                st.markdown("""
                **📈 Kapan Pakai Line Chart?**
                
                1. **Trend Analysis** - Pola perubahan
                2. **Continuous Data** - Data berkelanjutan
                3. **Time Series** - Perubahan waktu
                4. **Regression** - Garis tren
                5. **Prediction** - Ekstrapolasi
                
                **⚠️ HANYA untuk Tren:**
                - Speedup trend
                - Score trend
                - Performance pattern
                - Growth analysis
                """)
            
            st.markdown("""
            **🎨 Design Principle:**  
            > "Use column charts for comparison, line charts for trends"
            
            **📊 Dashboard ini mengikuti prinsip:**
            1. **6 Column Charts** untuk perbandingan
            2. **1 Line Chart** untuk tren performa
            3. **Konsisten** dalam visualisasi
            4. **Intuitif** untuk interpretasi
            """)

if __name__ == "__main__":
    main()