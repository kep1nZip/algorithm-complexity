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

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Linear Search - Marketplace",
    page_icon="🔍",
    layout="wide"
)

# ==================== ALGORITMA LINEAR SEARCH ====================

def linear_search_iteratif(products: List[str], keyword: str, mode: str = "first") -> Tuple:
    comparisons = 0
    keyword_lower = keyword.lower()
    
    if mode == "first":
        # Mode: cari pertama ditemukan
        for i in range(len(products)):
            comparisons += 1
            if keyword_lower in products[i].lower():
                return i, comparisons
        
        return -1, comparisons
    
    elif mode == "all":
        # Mode: cari semua produk
        found_indexes = []
        found_products = []
        
        for i in range(len(products)):
            comparisons += 1
            if keyword_lower in products[i].lower():
                found_indexes.append(i)
                found_products.append(products[i])
        
        return found_indexes, comparisons, found_products
    
    else:
        raise ValueError("Mode harus 'first' atau 'all'")

def linear_search_rekursif(products: List[str], keyword: str, index: int = 0, comparisons: int = 0) -> Tuple[int, int]:
    # Base case: mencapai akhir list
    if index >= len(products):
        return -1, comparisons
    
    comparisons += 1
    keyword_lower = keyword.lower()
    
    # Base case: keyword ditemukan
    if keyword_lower in products[index].lower():
        return index, comparisons
    
    # Recursive case
    return linear_search_rekursif(products, keyword, index + 1, comparisons)

# ==================== GENERATOR DATA DENGAN KONSISTENSI ====================

def generate_product_names(n: int, seed: int = None) -> List[str]:
    """
    Generate nama produk dummy untuk testing
    Dengan optional seed untuk hasil yang konsisten
    """
    categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                  'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
    brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
              'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
    adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                  'Portable', 'Professional', 'Advanced', 'Smart']
    
    # Simpan state random original
    original_state = random.getstate()
    
    # Set seed jika diberikan
    if seed is not None:
        random.seed(seed)
    
    products = []
    for i in range(n):
        category = random.choice(categories)
        brand = random.choice(brands)
        adjective = random.choice(adjectives)
        model = random.randint(1, 999)
        
        product = f"{brand} {category} {adjective} {model}"
        products.append(product)
    
    # Kembalikan ke state random original
    if seed is not None:
        random.setstate(original_state)
    
    return products

# ==================== VISUALISASI HASIL PENCARIAN ====================

def create_search_progress_visualization(products: List[str], keyword: str, found_indices: List[int]):
    """Buat visualisasi proses pencarian yang keren"""
    n = len(products)
    
    # Buat data untuk visualisasi
    is_found = [1 if i in found_indices else 0 for i in range(n)]
    colors = ['#FF6B6B' if found else '#4ECDC4' for found in is_found]
    
    fig = go.Figure()
    
    # Tambah bar chart untuk semua produk
    fig.add_trace(go.Bar(
        x=list(range(n)),
        y=[1] * n,
        marker_color=colors,
        opacity=0.7,
        name='Produk',
        hovertext=products,
        hovertemplate='<b>Index %{x}</b><br>%{hovertext}<br>Status: %{customdata}',
        customdata=['✅ Ditemukan' if i in found_indices else '❌ Tidak Ditemukan' for i in range(n)]
    ))
    
    # Tambah scatter plot untuk highlight produk yang ditemukan
    if found_indices:
        fig.add_trace(go.Scatter(
            x=found_indices,
            y=[1.2] * len(found_indices),
            mode='markers+text',
            marker=dict(size=15, color='#FFD93D', symbol='star'),
            text=['★'] * len(found_indices),
            textposition='top center',
            name='Keyword Ditemukan',
            hoverinfo='skip'
        ))
    
    # Tambah garis untuk menunjukkan proses pencarian linear
    fig.add_trace(go.Scatter(
        x=[-1, n],
        y=[0.5, 0.5],
        mode='lines',
        line=dict(color='#6C5B7B', width=3, dash='dash'),
        name='Alur Pencarian Linear'
    ))
    
    fig.update_layout(
        title=f'📊 Visualisasi Distribusi Hasil Pencarian: "{keyword}"',
        xaxis_title='Index Produk',
        yaxis=dict(showticklabels=False, range=[0, 1.5]),
        showlegend=True,
        height=400,
        template='plotly_white',
        bargap=0.1,
        hovermode='closest'
    )
    
    return fig

def create_search_timeline_visualization(products: List[str], keyword: str, found_indices: List[int]):
    """Buat visualisasi timeline pencarian"""
    n = len(products)
    
    # Data untuk timeline
    steps = []
    for i in range(min(n, 30)):  # Batasi untuk kejelasan
        is_match = keyword.lower() in products[i].lower()
        steps.append({
            'Step': i + 1,
            'Index': i,
            'Match': is_match,
            'Product': products[i][:30] + '...' if len(products[i]) > 30 else products[i],
            'Time': 0.02 + (0.01 if is_match else 0)  # Waktu konsisten
        })
    
    df_steps = pd.DataFrame(steps)
    
    fig = go.Figure()
    
    # Timeline dengan gradient color
    fig.add_trace(go.Scatter(
        x=df_steps['Step'],
        y=df_steps['Time'] * 1000,
        mode='lines+markers',
        line=dict(color='#355C7D', width=3),
        marker=dict(
            size=10,
            color=df_steps['Match'].map({True: '#C06C84', False: '#F8B195'}),
            symbol=df_steps['Match'].map({True: 'star', False: 'circle'}),
            line=dict(width=2, color='white')
        ),
        name='Proses Pencarian',
        hovertext=df_steps['Product'],
        hovertemplate='<b>Step %{x}</b><br>Index: %{customdata}<br>Waktu: %{y:.2f} ms<br>%{hovertext}<br>Status: %{text}',
        customdata=df_steps['Index'],
        text=df_steps['Match'].map({True: '✅ Match', False: '❌ No Match'})
    ))
    
    fig.update_layout(
        title='⏱️ Timeline Proses Pencarian Per Step',
        xaxis_title='Langkah Pencarian',
        yaxis_title='Waktu Eksekusi (ms)',
        height=400,
        template='plotly_white',
        hovermode='closest'
    )
    
    return fig

# ==================== VISUALISASI ASIMTOTIK ====================

def create_asymptotic_comparison_chart():
    """Buat grafik perbandingan fungsi waktu asimtotik"""
    n = np.linspace(1, 100, 100)
    
    fig = go.Figure()
    
    # Fungsi-fungsi asimtotik
    o1 = np.ones_like(n) * 10            # Constant
    o_logn = 10 * np.log2(n)             # Logarithmic
    o_n = n                              # Linear
    o_nlogn = n * np.log2(n) / 5         # Linearithmic
    o_n2 = n**2 / 50                     # Quadratic
    o_n3 = n**3 / 5000                   # Cubic
    o_2n = 2**(n/20) * 10                # Exponential (scaled)
    
    # Warna untuk setiap kompleksitas
    colors = {
        'O(1)': '#00CED1',        # Cyan
        'O(log n)': '#32CD32',    # Green
        'O(n)': '#1E90FF',        # Blue
        'O(n log n)': '#FF8C00',  # Orange
        'O(n²)': '#FF4500',       # Red
        'O(n³)': '#8B0000',       # Dark Red
        'O(2ⁿ)': '#8A2BE2'        # Blue Violet
    }
    
    fig.add_trace(go.Scatter(x=n, y=o1, mode='lines', name='O(1) - Constant',
                            line=dict(color=colors['O(1)'], width=3)))
    fig.add_trace(go.Scatter(x=n, y=o_logn, mode='lines', name='O(log n) - Logarithmic',
                            line=dict(color=colors['O(log n)'], width=3)))
    fig.add_trace(go.Scatter(x=n, y=o_n, mode='lines', name='O(n) - Linear (Linear Search)',
                            line=dict(color=colors['O(n)'], width=4)))
    fig.add_trace(go.Scatter(x=n, y=o_nlogn, mode='lines', name='O(n log n) - Linearithmic',
                            line=dict(color=colors['O(n log n)'], width=3)))
    fig.add_trace(go.Scatter(x=n, y=o_n2, mode='lines', name='O(n²) - Quadratic',
                            line=dict(color=colors['O(n²)'], width=3, dash='dash')))
    fig.add_trace(go.Scatter(x=n, y=o_n3, mode='lines', name='O(n³) - Cubic',
                            line=dict(color=colors['O(n³)'], width=3, dash='dash')))
    fig.add_trace(go.Scatter(x=n, y=o_2n, mode='lines', name='O(2ⁿ) - Exponential',
                            line=dict(color=colors['O(2ⁿ)'], width=3, dash='dot')))
    
    fig.update_layout(
        title='📈 Perbandingan Kompleksitas Asimtotik (Big O Notation)',
        xaxis_title='Ukuran Input (n)',
        yaxis_title='Waktu Eksekusi (Relatif)',
        height=500,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_linear_search_complexity_chart():
    """Buat grafik khusus untuk Linear Search"""
    n = np.linspace(1, 100, 100)
    
    fig = go.Figure()
    
    # Best case: O(1)
    fig.add_trace(go.Scatter(
        x=n, y=np.ones_like(n) * 5,
        mode='lines',
        name='Best Case - O(1)',
        line=dict(color='#00FF00', width=3),
        hovertemplate='Best Case<br>n=%{x}<br>Operasi: 1<extra></extra>'
    ))
    
    # Average case: O(n)
    fig.add_trace(go.Scatter(
        x=n, y=n/2,
        mode='lines',
        name='Average Case - O(n)',
        line=dict(color='#FFA500', width=3),
        hovertemplate='Average Case<br>n=%{x}<br>Operasi: n/2 ≈ %{y:.1f}<extra></extra>'
    ))
    
    # Worst case: O(n)
    fig.add_trace(go.Scatter(
        x=n, y=n,
        mode='lines',
        name='Worst Case - O(n)',
        line=dict(color='#FF0000', width=3),
        hovertemplate='Worst Case<br>n=%{x}<br>Operasi: n = %{y:.1f}<extra></extra>'
    ))
    
    # Area fill untuk visualisasi
    fig.add_trace(go.Scatter(
        x=np.concatenate([n, n[::-1]]),
        y=np.concatenate([n, np.ones_like(n) * 5]),
        fill='toself',
        fillcolor='rgba(255, 165, 0, 0.2)',
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='Range Linear Search',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Highlight Linear Search complexity
    fig.add_annotation(
        x=80, y=80,
        text="Linear Search = O(n)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#1E90FF",
        ax=20,
        ay=-40,
        font=dict(size=14, color="#1E90FF")
    )
    
    fig.update_layout(
        title='🔍 Kompleksitas Linear Search (Best/Average/Worst Case)',
        xaxis_title='Jumlah Produk (n)',
        yaxis_title='Jumlah Operasi/Perbandingan',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_complexity_table():
    """Buat tabel perbandingan kompleksitas"""
    n_values = [1, 5, 10, 50, 100, 1000]
    
    data = []
    for n in n_values:
        data.append({
            'n': n,
            'O(1)': 1,
            'O(log n)': round(math.log2(n) if n > 0 else 0, 2),
            'O(n)': n,
            'O(n log n)': round(n * math.log2(n) if n > 0 else 0, 2),
            'O(n²)': n**2,
            'O(2ⁿ)': 2**n if n <= 20 else '> 1 juta',
            'O(n!)': math.factorial(n) if n <= 10 else '> 3.6 juta'
        })
    
    df = pd.DataFrame(data)
    
    # Format untuk display
    display_df = df.copy()
    for col in display_df.columns[1:]:
        display_df[col] = display_df[col].apply(lambda x: f"{x:,}" if isinstance(x, (int, float)) and x < 1000000 else str(x))
    
    return display_df

# ==================== PERFORMANCE TEST ====================

def run_performance_test(sizes: List[int], keyword: str = "Gaming", seed: int = None) -> pd.DataFrame:
    """Menjalankan pengujian performa pada berbagai ukuran dataset"""
    results = []
    
    for size in sizes:
        # Generate produk dengan seed yang sama untuk konsistensi
        products = generate_product_names(size, seed)
        
        # Best case: keyword di awal
        products_best = products.copy()
        if size > 0:
            products_best[0] = f"ASUS {keyword} Laptop Pro 2024"
        
        # Worst case: keyword di akhir
        products_worst = products.copy()
        if size > 0:
            products_worst[-1] = f"Apple {keyword} MacBook Ultra 2024"
        
        # Average case: keyword di tengah
        products_avg = products.copy()
        if size > 1:
            products_avg[size // 2] = f"Samsung {keyword} Phone Max 2024"
        
        # Test Iteratif - Best Case
        start = time.perf_counter()
        idx_iter_best, comp_iter_best = linear_search_iteratif(products_best, keyword, mode="first")
        time_iter_best = (time.perf_counter() - start) * 1000
        
        # Test Iteratif - Worst Case
        start = time.perf_counter()
        idx_iter_worst, comp_iter_worst = linear_search_iteratif(products_worst, keyword, mode="first")
        time_iter_worst = (time.perf_counter() - start) * 1000
        
        # Test Iteratif - Average Case
        start = time.perf_counter()
        idx_iter_avg, comp_iter_avg = linear_search_iteratif(products_avg, keyword, mode="first")
        time_iter_avg = (time.perf_counter() - start) * 1000
        
        # Test Rekursif - Best Case
        sys.setrecursionlimit(max(size + 1000, 10000))
        start = time.perf_counter()
        try:
            idx_rek_best, comp_rek_best = linear_search_rekursif(products_best, keyword)
            time_rek_best = (time.perf_counter() - start) * 1000
        except RecursionError:
            time_rek_best = None
            comp_rek_best = None
        
        # Test Rekursif - Worst Case
        start = time.perf_counter()
        try:
            idx_rek_worst, comp_rek_worst = linear_search_rekursif(products_worst, keyword)
            time_rek_worst = (time.perf_counter() - start) * 1000
        except RecursionError:
            time_rek_worst = None
            comp_rek_worst = None
        
        # Test Rekursif - Average Case
        start = time.perf_counter()
        try:
            idx_rek_avg, comp_rek_avg = linear_search_rekursif(products_avg, keyword)
            time_rek_avg = (time.perf_counter() - start) * 1000
        except RecursionError:
            time_rek_avg = None
            comp_rek_avg = None
        
        results.append({
            'Ukuran Data': size,
            'Iteratif Best (ms)': time_iter_best,
            'Iteratif Worst (ms)': time_iter_worst,
            'Iteratif Avg (ms)': time_iter_avg,
            'Rekursif Best (ms)': time_rek_best,
            'Rekursif Worst (ms)': time_rek_worst,
            'Rekursif Avg (ms)': time_rek_avg,
            'Iter Best Comp': comp_iter_best,
            'Iter Worst Comp': comp_iter_worst,
            'Iter Avg Comp': comp_iter_avg,
            'Rek Best Comp': comp_rek_best,
            'Rek Worst Comp': comp_rek_worst,
            'Rek Avg Comp': comp_rek_avg,
        })
    
    return pd.DataFrame(results)

def create_performance_chart(df: pd.DataFrame):
    """Buat grafik performa dari hasil testing"""
    fig = go.Figure()
    
    # Iteratif - Worst Case
    fig.add_trace(go.Scatter(
        x=df['Ukuran Data'],
        y=df['Iteratif Worst (ms)'],
        mode='lines+markers',
        name='Iteratif (Worst Case)',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8),
        hovertemplate='Size: %{x:,}<br>Time: %{y:.4f} ms<extra></extra>'
    ))
    
    # Rekursif - Worst Case (jika ada)
    df_valid = df[df['Rekursif Worst (ms)'].notna()].copy()
    if not df_valid.empty:
        fig.add_trace(go.Scatter(
            x=df_valid['Ukuran Data'],
            y=df_valid['Rekursif Worst (ms)'],
            mode='lines+markers',
            name='Rekursif (Worst Case)',
            line=dict(color='#A23B72', width=3),
            marker=dict(size=8),
            hovertemplate='Size: %{x:,}<br>Time: %{y:.4f} ms<extra></extra>'
        ))
    
    fig.update_layout(
        title='📊 Hasil Pengujian Performa Linear Search',
        xaxis_title='Ukuran Dataset (jumlah produk)',
        yaxis_title='Waktu Eksekusi (ms)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig

# ==================== MAIN APP ====================

def main():
    st.title("🔍 Analisis Linear Search Marketplace")
    st.markdown("### Demo Pencarian + Visualisasi Hasil + Analisis Asimtotik")
    
    # Sidebar untuk pengaturan
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        st.markdown("### 🎯 Mode Demo")
        num_products = st.slider("Jumlah Produk", 10, 500, 100)
        keyword = st.text_input("Keyword Pencarian", "Gaming")
        
        st.markdown("### 🔧 Pengaturan Data")
        
        # Checkbox untuk data konsisten
        use_consistent_data = st.checkbox(
            "🔒 Gunakan Data Konsisten", 
            value=True,
            help="Jika dicentang, hasil pencarian akan sama setiap kali"
        )
        
        # Input seed jika menggunakan data konsisten
        data_seed = 42  # Default seed
        if use_consistent_data:
            data_seed = st.number_input(
                "Seed Data", 
                value=42, 
                min_value=0,
                help="Angka seed untuk generator random (gunakan angka yang sama untuk hasil yang sama)"
            )
        
        st.markdown("---")
        st.markdown("### 📊 Mode Testing")
        test_sizes = st.multiselect(
            "Ukuran Dataset untuk Testing",
            [50, 100, 500, 1000, 5000],
            default=[100, 500, 1000]
        )
        
        st.markdown("---")
        st.markdown("### 🎨 Tampilkan Visualisasi")
        show_viz = st.multiselect(
            "Pilih Visualisasi",
            ["📊 Distribusi Hasil", "⏱️ Timeline", "📈 Grafik Asimtotik", 
             "🔍 Kompleksitas Linear", "📋 Tabel Kompleksitas"],
            default=["📊 Distribusi Hasil", "📈 Grafik Asimtotik"]
        )
        
        st.markdown("---")
        st.markdown("**ℹ️ Tentang Aplikasi**")
        st.info("""
        Aplikasi ini menunjukkan:
        1. **Demo Linear Search** produk marketplace
        2. **Visualisasi hasil** pencarian
        3. **Analisis performa** iteratif vs rekursif
        4. **Analisis kompleksitas** asimtotik
        
        **🔧 Fitur Baru:** Data Konsisten
        - Hasil sama setiap kali dengan seed yang sama
        - Cocok untuk demo dan presentasi
        - Tetap bisa acak jika tidak dicentang
        """)
    
    # Container utama
    main_container = st.container()
    
    with main_container:
        # ===== BAGIAN 1: DEMO PENCARIAN =====
        st.header("🎯 Demo Pencarian Produk")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_type = st.radio(
                "Tipe Pencarian",
                ["🔍 Cari Pertama Ditemukan", "📋 Cari SEMUA Produk"],
                horizontal=True
            )
        
        with col2:
            demo_button = st.button("🚀 Jalankan Pencarian", type="primary", use_container_width=True)
        
        if demo_button:
            # Generate produk dengan atau tanpa seed
            seed_to_use = data_seed if use_consistent_data else None
            products = generate_product_names(num_products, seed_to_use)
            
            # Tampilkan info seed
            if use_consistent_data:
                st.info(f"🔧 **Data konsisten dengan seed:** `{data_seed}`")
            
            # Tentukan mode berdasarkan pilihan user
            if search_type == "🔍 Cari Pertama Ditemukan":
                mode = "first"
                st.info("**Mode: Cari Pertama Ditemukan** - Berhenti saat menemukan produk pertama")
            else:
                mode = "all"
                st.info("**Mode: Cari SEMUA Produk** - Mencari semua produk yang sesuai")
            
            # Jalankan pencarian sesuai mode
            if mode == "first":
                # Mode pertama ditemukan
                found_index, comparisons = linear_search_iteratif(products, keyword, mode="first")
                
                # Untuk menghitung total produk yang mengandung keyword (hanya untuk info)
                all_indices, total_comparisons, all_products = linear_search_iteratif(products, keyword, mode="all")
                total_found = len(all_products)
            else:
                # Mode semua produk
                found_indices, comparisons, found_products = linear_search_iteratif(products, keyword, mode="all")
                total_found = len(found_products)
            
            # Tampilkan hasil pencarian
            with st.expander("📋 Hasil Pencarian", expanded=True):
                col_result1, col_result2, col_result3 = st.columns(3)
                
                with col_result1:
                    st.metric("Total Produk", num_products)
                
                with col_result2:
                    st.metric("Total Ditemukan", total_found)
                
                with col_result3:
                    percentage = (total_found/num_products*100) if num_products > 0 else 0
                    st.metric("Persentase", f"{percentage:.1f}%")
                
                if mode == "first":
                    if found_index != -1:
                        st.success(f"✅ **Produk pertama ditemukan di index:** {found_index}")
                        st.markdown(f"**🎯 Produk:** {products[found_index]}")
                        st.metric("Jumlah Perbandingan", comparisons)
                        st.caption("ℹ️ Mode 'Cari Pertama' berhenti setelah menemukan produk pertama")
                    else:
                        st.error(f"❌ Tidak ditemukan produk dengan keyword '{keyword}'")
                else:
                    if found_products:
                        st.success(f"✅ Ditemukan {len(found_products)} produk mengandung '{keyword}'")
                        st.metric("Jumlah Perbandingan", comparisons)
                        st.caption(f"ℹ️ Mode 'Cari Semua' melakukan {comparisons} perbandingan (cek semua produk)")
                        
                        for idx, (pos, product) in enumerate(zip(found_indices, found_products)):
                            with st.container():
                                st.markdown(f"**🎯 #{idx+1}** - Index {pos}: {product}")
                                st.divider()
                    else:
                        st.error(f"❌ Tidak ditemukan produk dengan keyword '{keyword}'")
            
            # ===== VISUALISASI HASIL PENCARIAN =====
            if "📊 Distribusi Hasil" in show_viz:
                st.markdown("---")
                st.header("📊 Visualisasi Hasil Pencarian")
                
                # Tentukan indeks untuk visualisasi
                if mode == "first":
                    if found_index != -1:
                        viz_indices = [found_index]
                    else:
                        viz_indices = []
                else:
                    viz_indices = found_indices
                
                if viz_indices:
                    col_viz1, col_viz2 = st.columns(2)
                    
                    with col_viz1:
                        fig_dist = create_search_progress_visualization(products, keyword, viz_indices)
                        st.plotly_chart(fig_dist, use_container_width=True)
                    
                    with col_viz2:
                        fig_timeline = create_search_timeline_visualization(products, keyword, viz_indices)
                        st.plotly_chart(fig_timeline, use_container_width=True)
                else:
                    st.warning("Tidak ada produk yang ditemukan untuk divisualisasikan")
            
            # ===== PERBANDINGAN ALGORITMA =====
            st.markdown("---")
            st.header("🔄 Perbandingan Algoritma")
            
            col_algo1, col_algo2 = st.columns(2)
            
            with col_algo1:
                st.subheader("🔄 Linear Search Iteratif")
                start = time.perf_counter()
                # Gunakan mode="first" untuk mencari pertama ditemukan
                idx_iter, comp_iter = linear_search_iteratif(products, keyword, mode="first")
                time_iter = (time.perf_counter() - start) * 1000
                
                if idx_iter != -1:
                    st.success(f"✅ Ditemukan di index: **{idx_iter}**")
                else:
                    st.error("❌ Tidak ditemukan")
                
                st.metric("Waktu Eksekusi", f"{time_iter:.4f} ms")
                st.metric("Jumlah Perbandingan", comp_iter)
            
            with col_algo2:
                st.subheader("🔁 Linear Search Rekursif")
                sys.setrecursionlimit(max(num_products + 1000, 10000))
                start = time.perf_counter()
                try:
                    idx_rek, comp_rek = linear_search_rekursif(products, keyword)
                    time_rek = (time.perf_counter() - start) * 1000
                    
                    if idx_rek != -1:
                        st.success(f"✅ Ditemukan di index: **{idx_rek}**")
                    else:
                        st.error("❌ Tidak ditemukan")
                    
                    st.metric("Waktu Eksekusi", f"{time_rek:.4f} ms")
                    st.metric("Jumlah Perbandingan", comp_rek)
                except RecursionError:
                    st.error("⚠️ Stack Overflow! Data terlalu besar untuk rekursif")
                    time_rek = None
            
            # Perbandingan performa
            if 'time_rek' in locals() and time_rek is not None:
                st.markdown("---")
                col_comp1, col_comp2, col_comp3 = st.columns(3)
                
                with col_comp1:
                    diff_time = abs(time_iter - time_rek)
                    st.metric("Selisih Waktu", f"{diff_time:.4f} ms")
                
                with col_comp2:
                    faster = "Iteratif" if time_iter < time_rek else "Rekursif"
                    st.metric("Lebih Cepat", faster)
                
                with col_comp3:
                    if time_iter > 0 and time_rek > 0:
                        speedup = max(time_rek, time_iter) / min(time_rek, time_iter)
                        st.metric("Speedup", f"{speedup:.2f}x")
        
        # ===== BAGIAN 2: PERFORMANCE TESTING =====
        st.markdown("---")
        st.header("📊 Performance Testing")
        
        col_test1, col_test2 = st.columns([3, 1])
        
        with col_test2:
            test_button = st.button("⚡ Jalankan Performance Test", type="secondary", use_container_width=True)
        
        if test_button and test_sizes:
            # Gunakan seed yang sama untuk konsistensi
            seed_to_use = data_seed if use_consistent_data else None
            
            with st.spinner("Menjalankan performance test..."):
                df_results = run_performance_test(sorted(test_sizes), keyword, seed_to_use)
            
            # Tampilkan info konsistensi
            if use_consistent_data:
                st.info(f"📊 **Performance test menggunakan seed:** `{data_seed}`")
            
            # Tampilkan grafik performa
            fig_perf = create_performance_chart(df_results)
            st.plotly_chart(fig_perf, use_container_width=True)
            
            # Tampilkan tabel data
            with st.expander("📋 Data Lengkap Hasil Testing"):
                st.dataframe(df_results, use_container_width=True)
        
        # ===== BAGIAN 3: ANALISIS ASIMTOTIK =====
        st.markdown("---")
        st.header("📈 Analisis Kompleksitas Asimtotik")
        
        # Penjelasan
        st.markdown("""
        ### 🎯 Apa itu Analisis Asimtotik?
        
        Analisis asimtotik digunakan untuk menganalisis **perilaku waktu eksekusi algoritma** 
        ketika ukuran input bertambah sangat besar (n → ∞). **Notasi Big O** menggambarkan 
        **batas atas (upper bound)** dari pertumbuhan fungsi waktu.
        """)
        
        # Tampilkan visualisasi yang dipilih
        viz_cols = st.columns(2)
        
        if "📈 Grafik Asimtotik" in show_viz:
            with viz_cols[0]:
                fig_asymptotic = create_asymptotic_comparison_chart()
                st.plotly_chart(fig_asymptotic, use_container_width=True)
        
        if "🔍 Kompleksitas Linear" in show_viz:
            with viz_cols[1]:
                fig_linear_comp = create_linear_search_complexity_chart()
                st.plotly_chart(fig_linear_comp, use_container_width=True)
        
        if "📋 Tabel Kompleksitas" in show_viz:
            st.markdown("### 📋 Tabel Perbandingan Nilai Kompleksitas")
            df_complexity = create_complexity_table()
            st.dataframe(df_complexity, use_container_width=True)
            
            st.markdown("""
            **📝 Interpretasi Tabel:**
            - **O(1)**: Selalu konstan, tidak peduli n
            - **O(log n)**: Tumbuh sangat lambat
            - **O(n)**: Linear Search - tumbuh proporsional dengan n
            - **O(n²)**: Tumbuh cepat, untuk n=1000 butuh 1 juta operasi
            - **O(2ⁿ)**: Eksponensial - sangat cepat membesar
            - **O(n!)**: Faktorial - paling cepat membesar
            """)
        
        # ===== BAGIAN 4: KESIMPULAN =====
        st.markdown("---")
        st.header("🎯 Kesimpulan & Rekomendasi")
        
        col_concl1, col_concl2 = st.columns(2)
        
        with col_concl1:
            st.success("""
            **✅ Keunggulan Linear Search:**
            
            1. **Sederhana** - mudah diimplementasi
            2. **Universal** - bekerja pada data terurut/tidak terurut
            3. **Low Memory** - O(1) space complexity
            4. **Predictable** - performa mudah diprediksi
            5. **Stable** - tidak mengubah data asli
            """)
        
        with col_concl2:
            st.warning("""
            **⚠️ Kelemahan Linear Search:**
            
            1. **Slow for large n** - O(n) time complexity
            2. **Inefficient** - harus cek semua elemen di worst case
            3. **Not optimal** - ada algoritma lebih cepat
            4. **Bad scalability** - tidak cocok untuk big data
            5. **No early optimization** - tidak manfaatkan struktur data
            """)
        
        # Rekomendasi penggunaan
        st.markdown("### 💡 Rekomendasi Penggunaan")
        
        rec_data = {
            'Use Case': ['Data Kecil (<1000)', 'Data Sedang (1000-10000)', 'Data Besar (>10000)', 
                         'Data Terurut', 'Pencarian Berulang', 'Real-time Systems'],
            'Algoritma': ['Linear Search', 'Binary Search / Hash Table', 'Hash Table / Indexing',
                         'Binary Search', 'Hash Table', 'Hash Table / Bloom Filter'],
            'Kompleksitas': ['O(n)', 'O(log n) / O(1)', 'O(1)',
                            'O(log n)', 'O(1)', 'O(1)'],
            'Keterangan': ['Cukup efisien', 'Butuh preprocessing', 'Butuh struktur data kompleks',
                          'Paling efisien', 'Optimal untuk cache', 'Deterministic latency']
        }
        
        df_recommendation = pd.DataFrame(rec_data)
        st.dataframe(df_recommendation, use_container_width=True, hide_index=True)
        
        # Final message
        st.info("""
        **🎓 Takeaway:**
        Linear Search adalah **algoritma fundamental** yang harus dipahami setiap programmer.
        Meski tidak selalu paling efisien, pemahaman tentang Linear Search memberikan dasar untuk
        memahami algoritma pencarian yang lebih kompleks. **Kenali use case-nya, gunakan dengan bijak!**
        """)

if __name__ == "__main__":
    main()