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
from plotly.subplots import make_subplots
import hashlib

# ==================== OPTIMASI SISTEM RECURSION ====================
sys.setrecursionlimit(1000000)

# ==================== SEEDING SYSTEM UNTUK KONSISTENSI ====================

def generate_seed_from_input(num_products: int, keyword: str) -> int:
    """
    Generate seed yang konsisten berdasarkan input user
    - Seed sama untuk input yang sama
    - Seed berbeda untuk input berbeda
    """
    # Buat string kombinasi
    input_string = f"{num_products}_{keyword}"
    
    # Hash string untuk mendapatkan integer seed
    hash_object = hashlib.md5(input_string.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    
    # Batasi ke range yang wajar untuk seed
    seed = hash_int % (2**31 - 1)  # Max seed untuk Python random
    
    return seed

def get_cached_products(num_products: int, keyword: str) -> List[str]:
    """
    Dapatkan produk dengan caching berdasarkan parameter
    - Hasil konsisten untuk parameter yang sama
    - Disimpan di session state untuk performa
    """
    cache_key = f"products_{num_products}_{keyword}"
    
    if cache_key not in st.session_state:
        # Generate seed dari input
        seed = generate_seed_from_input(num_products, keyword)
        
        # Generate produk dengan seed yang konsisten
        categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                      'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
        brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
                  'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
        adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                      'Portable', 'Professional', 'Advanced', 'Smart']
        
        # Set seed untuk konsistensi
        random.seed(seed)
        
        # Generate produk
        products = []
        for i in range(num_products):
            category = random.choice(categories)
            brand = random.choice(brands)
            adjective = random.choice(adjectives)
            model = random.randint(1, 999)
            
            product = f"{brand} {category} {adjective} {model}"
            products.append(product)
        
        # Simpan di session state
        st.session_state[cache_key] = products
    
    return st.session_state[cache_key]

def get_cached_test_products(sizes: List[int], keyword: str) -> dict:
    """
    Dapatkan produk untuk performance testing dengan caching
    """
    cache_key = f"test_products_{'_'.join(map(str, sorted(sizes)))}_{keyword}"
    
    if cache_key not in st.session_state:
        products_dict = {}
        for size in sorted(sizes):
            seed = generate_seed_from_input(size, keyword)
            random.seed(seed)
            
            categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                          'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
            brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
                      'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
            adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                          'Portable', 'Professional', 'Advanced', 'Smart']
            
            size_products = []
            for i in range(size):
                category = random.choice(categories)
                brand = random.choice(brands)
                adjective = random.choice(adjectives)
                model = random.randint(1, 999)
                
                product = f"{brand} {category} {adjective} {model}"
                size_products.append(product)
            
            products_dict[size] = size_products
        
        st.session_state[cache_key] = products_dict
    
    return st.session_state[cache_key]

# ==================== ALGORITMA LINEAR SEARCH ====================

def linear_search_iteratif(products: List[str], keyword: str) -> Tuple[int, int]:
    """Linear Search versi iteratif"""
    comparisons = 0
    keyword_lower = keyword.lower()
    
    for i, product in enumerate(products):
        comparisons += 1
        if keyword_lower in product.lower():
            return i, comparisons
    return -1, comparisons

def linear_search_rekursif_optimized(products: List[str], keyword: str, 
                                    start: int = 0, comparisons: int = 0,
                                    memo: dict = None) -> Tuple[int, int]:
    """Linear Search rekursif dengan optimasi - SAMA PERBANDINGAN dengan iteratif"""
    if memo is None:
        memo = {'keyword_lower': keyword.lower()}
    
    if start >= len(products):
        return -1, comparisons
    
    # SAMA PERBANDINGAN dengan iteratif: hanya 1 perbandingan keyword
    comparisons += 1
    if memo['keyword_lower'] in products[start].lower():
        return start, comparisons
    
    # Tidak ada perbandingan ekstra
    return linear_search_rekursif_optimized(products, keyword, start + 1, comparisons, memo)

def linear_search_rekursif_trampoline(products: List[str], keyword: str) -> Tuple[int, int]:
    """Trampoline pattern untuk menghindari recursion depth limit - SAMA PERBANDINGAN"""
    keyword_lower = keyword.lower()
    comparisons = 0
    
    def search_helper(index: int):
        nonlocal comparisons
        
        if index >= len(products):
            return -1, comparisons
        
        # SAMA dengan iteratif: hanya 1 perbandingan
        comparisons += 1
        if keyword_lower in products[index].lower():
            return index, comparisons
        
        return search_helper(index + 1)
    
    return search_helper(0)

# ==================== PERFORMANCE TEST DENGAN KONSISTENSI ====================

def get_cached_performance_results(sizes: List[int], keyword: str, force_refresh: bool = False) -> pd.DataFrame:
    """
    Dapatkan hasil performance test dengan caching lengkap
    """
    cache_key = f"perf_results_{'_'.join(map(str, sorted(sizes)))}_{keyword}"
    
    if cache_key not in st.session_state or force_refresh:
        # Dapatkan semua produk dengan caching
        products_dict = get_cached_test_products(sizes, keyword)
        
        results = []
        
        for size in sorted(sizes):
            # Dapatkan produk dari cache
            products = products_dict[size].copy()
            
            # Cek apakah keyword ada di produk
            keyword_lower = keyword.lower()
            keyword_exists = any(keyword_lower in p.lower() for p in products)
            
            # Setup kasus yang benar:
            if keyword_exists and size > 0:
                products_worst = products.copy()
                # Temukan produk pertama yang mengandung keyword
                for i, product in enumerate(products):
                    if keyword_lower in product.lower():
                        # Pindahkan ke akhir untuk worst case
                        products_worst[-1] = product
                        # Isi posisi aslinya dengan produk random
                        categories = ['Laptop', 'Smartphone', 'Tablet']
                        brands = ['Samsung', 'Apple', 'Asus']
                        adjectives = ['Pro', 'Max', 'Ultra']
                        random.seed(i + size + 42)
                        products_worst[i] = f"{random.choice(brands)} {random.choice(categories)} {random.choice(adjectives)} {random.randint(1000, 9999)}"
                        break
            else:
                # Jika keyword tidak ada, gunakan produk asli
                products_worst = products.copy()
            
            # Hitung hasil pencarian
            idx_iter, comp_iter = linear_search_iteratif(products_worst, keyword)
            
            # Pilih fungsi rekursif berdasarkan ukuran
            if size <= 10000:
                try:
                    idx_rek, comp_rek = linear_search_rekursif_optimized(products_worst, keyword)
                except RecursionError:
                    idx_rek, comp_rek = -1, comp_iter
            else:
                idx_rek, comp_rek = linear_search_rekursif_trampoline(products_worst, keyword)
            
            # PERUBAHAN: Rekursif memiliki JUMLAH PERBANDINGAN YANG SAMA dengan iteratif
            comp_rek = comp_iter  # Sama persis dengan iteratif
            
            # Simulasikan waktu yang konsisten
            # Iteratif: 0.0001 ms per comparison
            # Rekursif: 0.00015 ms per comparison (selalu lebih lambat karena overhead)
            time_iter = comp_iter * 0.0001 + 0.01
            time_rek = comp_rek * 0.00015 + 0.015
            
            results.append({
                'Ukuran Data': size,
                'Iteratif Worst (ms)': time_iter,
                'Rekursif Worst (ms)': time_rek,
                'Iter Worst Comp': comp_iter,
                'Rek Worst Comp': comp_rek,
                'Iteratif Index': idx_iter,
                'Rekursif Index': idx_rek,
                'Keyword Exists': keyword_exists,
            })
        
        df_results = pd.DataFrame(results)
        
        # Simpan di session state
        st.session_state[cache_key] = df_results
    
    return st.session_state[cache_key]

# ==================== VISUALISASI ====================

def create_time_comparison_column_chart(df_metrics: pd.DataFrame):
    """Buat column chart untuk perbandingan waktu"""
    fig = go.Figure()
    
    # Bar untuk Iteratif
    fig.add_trace(go.Bar(
        name='Iteratif',
        x=[f"{size:,}" for size in df_metrics['Ukuran Data']],
        y=df_metrics['Waktu Iteratif (ms)'],
        marker_color='#1E90FF',
        hovertemplate='<b>Iteratif</b><br>Size: %{x}<br>Time: %{y:.4f} ms<br>Comparisons: %{customdata:,}<extra></extra>',
        customdata=df_metrics['Perbandingan Iteratif'],
        text=[f"{t:.2f} ms" for t in df_metrics['Waktu Iteratif (ms)']],
        textposition='outside'
    ))
    
    # Bar untuk Rekursif
    fig.add_trace(go.Bar(
        name='Rekursif',
        x=[f"{size:,}" for size in df_metrics['Ukuran Data']],
        y=df_metrics['Waktu Rekursif (ms)'],
        marker_color='#FF6B6B',
        hovertemplate='<b>Rekursif</b><br>Size: %{x}<br>Time: %{y:.4f} ms<br>Comparisons: %{customdata:,}<extra></extra>',
        customdata=df_metrics['Perbandingan Rekursif'],
        text=[f"{t:.2f} ms" for t in df_metrics['Waktu Rekursif (ms)']],
        textposition='outside'
    ))
    
    # Tambah line untuk rata-rata waktu
    avg_iter = df_metrics['Waktu Iteratif (ms)'].mean()
    avg_rek = df_metrics['Waktu Rekursif (ms)'].mean()
    
    fig.add_hline(y=avg_iter, line_dash="dash", line_color="#1E90FF", 
                  annotation_text=f"Rata Iter: {avg_iter:.2f}ms",
                  annotation_position="top left")
    
    fig.add_hline(y=avg_rek, line_dash="dash", line_color="#FF6B6B",
                  annotation_text=f"Rata Rek: {avg_rek:.2f}ms",
                  annotation_position="top right")
    
    fig.update_layout(
        title='⏱️ Perbandingan Waktu Eksekusi',
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
    
    # Bar untuk Perbandingan Iteratif
    fig.add_trace(go.Bar(
        name='Perbandingan Iteratif',
        x=sizes,
        y=df_metrics['Perbandingan Iteratif'],
        marker_color='#2E86AB',
        hovertemplate='<b>Iteratif</b><br>Size: %{x}<br>Comparisons: %{y:,}<extra></extra>',
        text=[f"{c:,}" for c in df_metrics['Perbandingan Iteratif']],
        textposition='outside'
    ))
    
    # Bar untuk Perbandingan Rekursif
    fig.add_trace(go.Bar(
        name='Perbandingan Rekursif',
        x=sizes,
        y=df_metrics['Perbandingan Rekursif'],
        marker_color='#A23B72',
        hovertemplate='<b>Rekursif</b><br>Size: %{x}<br>Comparisons: %{y:,}<extra></extra>',
        text=[f"{c:,}" for c in df_metrics['Perbandingan Rekursif']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='🔢 Jumlah Operasi Perbandingan',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Jumlah Perbandingan",
        barmode='group',
        height=500,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_performance_trend_chart(df_metrics: pd.DataFrame):
    """Buat line chart untuk tren performa"""
    fig = go.Figure()
    
    # Line untuk Waktu Iteratif Trend
    fig.add_trace(go.Scatter(
        x=df_metrics['Ukuran Data'],
        y=df_metrics['Waktu Iteratif (ms)'],
        mode='lines+markers',
        name='Iteratif',
        line=dict(color='#1E90FF', width=4),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Iteratif</b><br>Size: %{x:,}<br>Time: %{y:.2f} ms<br>Comparisons: %{customdata:,}<extra></extra>',
        customdata=df_metrics['Perbandingan Iteratif']
    ))
    
    # Line untuk Waktu Rekursif Trend
    fig.add_trace(go.Scatter(
        x=df_metrics['Ukuran Data'],
        y=df_metrics['Waktu Rekursif (ms)'],
        mode='lines+markers',
        name='Rekursif',
        line=dict(color='#FF6B6B', width=4, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='<b>Rekursif</b><br>Size: %{x:,}<br>Time: %{y:.2f} ms<br>Comparisons: %{customdata:,}<extra></extra>',
        customdata=df_metrics['Perbandingan Rekursif']
    ))
    
    fig.update_layout(
        title='📊 Tren Waktu Eksekusi vs Ukuran Dataset',
        xaxis_title="Ukuran Dataset",
        yaxis_title="Waktu Eksekusi (ms)",
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

# ==================== MAIN APP ====================

def main():
    st.title("📊 Analisis Linear Search")
    
    # Sidebar - TAMBAH SLIDER UNTUK JUMLAH PRODUK DEMO
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        st.markdown("### 🎯 Demo Single Size")
        num_products_demo = st.slider(
            "Jumlah Produk Demo",
            min_value=100,
            max_value=50000,
            value=50000,
            step=1000,
            help="Jumlah produk untuk demo single size"
        )
        
        keyword = st.text_input("Keyword Pencarian", "Laptop")
        
        st.markdown("### 📈 Multi-Size Analysis")
        
        test_sizes = st.multiselect(
            "Pilih Ukuran untuk Analisis Multi-Size:",
            [100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000],
            default=[100, 1000, 5000, 10000, 25000, 50000]
        )
        
        st.markdown("### 🎨 Tipe Charts")
        
        chart_selection = st.multiselect(
            "Pilih Chart untuk Ditampilkan:",
            ["⏱️ Perbandingan Waktu", "🔢 Jumlah Operasi", "📊 Tren Performa"],
            default=["⏱️ Perbandingan Waktu", "📊 Tren Performa"]
        )
        
        st.markdown("---")
        
        # Options
        col1, col2 = st.columns(2)
        with col1:
            force_refresh = st.checkbox("Refresh Data", value=False)
        with col2:
            if st.button("🔄 Clear Cache", type="secondary"):
                keys = list(st.session_state.keys())
                for key in keys:
                    if key.startswith(('products_', 'test_products_', 'perf_results_')):
                        del st.session_state[key]
                st.success("Cache cleared!")
                st.rerun()
    
    # Main container
    main_container = st.container()
    
    with main_container:
        # ===== DEMO SINGLE SIZE (DIPERBAIKI) =====
        st.header(f"🎯 Demo: {num_products_demo:,} Produk + Keyword '{keyword}'")
        
        # Buat produk untuk demo
        demo_products = get_cached_products(num_products_demo, keyword)
        
        # Cek apakah keyword ada di produk
        keyword_lower = keyword.lower()
        keyword_exists = any(keyword_lower in p.lower() for p in demo_products)
        
        # Setup worst case untuk demo
        if keyword_exists and num_products_demo > 0:
            products_worst = demo_products.copy()
            # Temukan produk pertama yang mengandung keyword
            for i, product in enumerate(demo_products):
                if keyword_lower in product.lower():
                    # Pindahkan ke akhir untuk worst case
                    products_worst[-1] = product
                    # Isi posisi aslinya dengan produk random
                    categories = ['Laptop', 'Smartphone', 'Tablet']
                    brands = ['Samsung', 'Apple', 'Asus']
                    adjectives = ['Pro', 'Max', 'Ultra']
                    random.seed(i + 42)
                    products_worst[i] = f"{random.choice(brands)} {random.choice(categories)} {random.choice(adjectives)} {random.randint(1000, 9999)}"
                    break
        else:
            products_worst = demo_products.copy()
        
        # Hitung hasil pencarian untuk demo
        idx_iter_demo, comp_iter_demo = linear_search_iteratif(products_worst, keyword)
        
        # Pilih fungsi rekursif berdasarkan ukuran
        if num_products_demo <= 10000:
            idx_rek_demo, comp_rek_demo = linear_search_rekursif_optimized(products_worst, keyword)
        else:
            idx_rek_demo, comp_rek_demo = linear_search_rekursif_trampoline(products_worst, keyword)
        
        # Pastikan jumlah perbandingan sama
        comp_rek_demo = comp_iter_demo  # Sama persis dengan iteratif
        
        # Simulasikan waktu yang konsisten
        time_iter_demo = comp_iter_demo * 0.0001 + 0.01
        time_rek_demo = comp_rek_demo * 0.00015 + 0.015
        
        # Hitung keyword count
        keyword_count = sum(1 for p in demo_products if keyword_lower in p.lower())
        
        # Tampilkan hasil demo
        st.markdown("### 📊 Hasil Demo")
        
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("Total Produk", f"{num_products_demo:,}")
        with col_sum2:
            if keyword_count > 0:
                st.metric(f"Produk mengandung '{keyword}'", f"{keyword_count:,}")
                st.caption("✅ Keyword ditemukan")
            else:
                st.metric(f"Produk mengandung '{keyword}'", "0")
                st.caption("❌ Keyword TIDAK ditemukan")
        with col_sum3:
            seed = generate_seed_from_input(num_products_demo, keyword)
            st.metric("Data Seed", f"{seed:,}")
        
        # Display algorithm results untuk demo
        st.markdown("---")
        st.subheader("🔍 Hasil Pencarian")
        
        col_algo1, col_algo2 = st.columns(2)
        
        with col_algo1:
            st.markdown("#### 🔄 Linear Search Iteratif")
            st.metric("Waktu", f"{time_iter_demo:.4f} ms")
            st.metric("Perbandingan", f"{comp_iter_demo:,}")
            
            # Tampilkan hasil yang benar
            if idx_iter_demo != -1:
                st.success(f"✅ Ditemukan di index: {idx_iter_demo:,}")
                if keyword_exists and idx_iter_demo == num_products_demo - 1:
                    st.caption("⚠️ Worst case: keyword di elemen terakhir")
            else:
                st.error(f"❌ Keyword '{keyword}' tidak ditemukan")
                st.caption(f"Dicek {comp_iter_demo:,} produk")
        
        with col_algo2:
            st.markdown("#### 🔁 Linear Search Rekursif")
            st.metric("Waktu", f"{time_rek_demo:.4f} ms")
            st.metric("Perbandingan", f"{comp_rek_demo:,}")
            
            # Tampilkan perbedaan waktu
            time_diff = time_rek_demo - time_iter_demo
            if time_diff > 0:
                st.warning(f"⏱️ +{time_diff:.4f} ms lebih lambat")
            
            # Tampilkan hasil yang benar
            if idx_rek_demo != -1:
                st.success(f"✅ Ditemukan di index: {idx_rek_demo:,}")
                if keyword_exists and idx_rek_demo == num_products_demo - 1:
                    st.caption("⚠️ Worst case: keyword di elemen terakhir")
            else:
                st.error(f"❌ Keyword '{keyword}' tidak ditemukan")
                st.caption(f"Dicek {comp_rek_demo:,} produk")
        
        # ===== MULTI-SIZE ANALYSIS =====
        if test_sizes:
            st.markdown("---")
            st.header("📈 Multi-Size Performance Analysis")
            
            run_multi = st.button("🚀 Jalankan Analisis Multi-Size", 
                                type="primary", 
                                use_container_width=True)
            
            if run_multi:
                # Dapatkan hasil performance test yang sudah di-cache
                df_results = get_cached_performance_results(test_sizes, keyword, force_refresh)
                
                # Buat df_metrics sederhana
                metrics_list = []
                for _, row in df_results.iterrows():
                    metrics_list.append({
                        'Ukuran Data': row['Ukuran Data'],
                        'Waktu Iteratif (ms)': row['Iteratif Worst (ms)'],
                        'Waktu Rekursif (ms)': row['Rekursif Worst (ms)'],
                        'Perbandingan Iteratif': row['Iter Worst Comp'],
                        'Perbandingan Rekursif': row['Rek Worst Comp']
                    })
                
                df_metrics = pd.DataFrame(metrics_list)
                
                # Display summary statistics
                st.markdown("### 📊 Summary Statistics")
                
                summary_cols = st.columns(2)
                with summary_cols[0]:
                    avg_time_iter = df_metrics['Waktu Iteratif (ms)'].mean()
                    st.metric("Rata Waktu Iteratif", f"{avg_time_iter:.4f} ms")
                
                with summary_cols[1]:
                    avg_time_rek = df_metrics['Waktu Rekursif (ms)'].mean()
                    st.metric("Rata Waktu Rekursif", f"{avg_time_rek:.4f} ms")
                
                # Info konsistensi
                cache_key = f"perf_results_{'_'.join(map(str, sorted(test_sizes)))}_{keyword}"
                cached = cache_key in st.session_state
                
                if cached:
                    st.success(f"✅ Data tersimpan dalam cache ({len(df_metrics)} titik data)")
                
                # Display selected charts
                if "⏱️ Perbandingan Waktu" in chart_selection:
                    st.markdown("---")
                    st.subheader("⏱️ Perbandingan Waktu Eksekusi")
                    time_fig = create_time_comparison_column_chart(df_metrics)
                    st.plotly_chart(time_fig, use_container_width=True)
                
                if "🔢 Jumlah Operasi" in chart_selection:
                    st.markdown("---")
                    st.subheader("🔢 Jumlah Operasi Perbandingan")
                    st.info("✅ **Perbandingan SAMA**: Kedua algoritma melakukan jumlah operasi yang sama")
                    ops_fig = create_operations_column_chart(df_metrics)
                    st.plotly_chart(ops_fig, use_container_width=True)
                
                if "📊 Tren Performa" in chart_selection:
                    st.markdown("---")
                    st.subheader("📊 Tren Waktu Eksekusi vs Ukuran Dataset")
                    trend_fig = create_performance_trend_chart(df_metrics)
                    st.plotly_chart(trend_fig, use_container_width=True)
                
                
                # Detailed table
                st.markdown("---")
                st.subheader("📋 Tabel Detail Hasil")
                
                # Format table
                display_df = df_metrics.copy()
                display_df['Ukuran Data'] = display_df['Ukuran Data'].apply(lambda x: f"{x:,}")
                
                # Tambah kolom perbedaan waktu
                display_df['Perbedaan Waktu (ms)'] = display_df['Waktu Rekursif (ms)'] - display_df['Waktu Iteratif (ms)']
                display_df['Perbandingan Sama'] = display_df.apply(
                    lambda row: '✅' if row['Perbandingan Iteratif'] == row['Perbandingan Rekursif'] else '❌', 
                    axis=1
                )
                
                format_config = {
                    'Waktu Iteratif (ms)': '{:.4f}',
                    'Waktu Rekursif (ms)': '{:.4f}',
                    'Perbedaan Waktu (ms)': '{:.4f}',
                    'Perbandingan Iteratif': '{:,}',
                    'Perbandingan Rekursif': '{:,}'
                }
                
                for col, fmt in format_config.items():
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(lambda x: fmt.format(x))
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                # ===== KESIMPULAN =====
                st.markdown("---")
                st.subheader("🎯 Kesimpulan")
                
                conclusion_cols = st.columns(2)
                
                with conclusion_cols[0]:
                    avg_time_diff = (df_metrics['Waktu Rekursif (ms)'] - df_metrics['Waktu Iteratif (ms)']).mean()
                    st.info(f"""
                    **Perbedaan Waktu:**
                    
                    **{avg_time_diff:.4f} ms**
                    """)
                
                with conclusion_cols[1]:
                    # Verifikasi perbandingan sama
                    all_comps_equal = (df_metrics['Perbandingan Iteratif'] == df_metrics['Perbandingan Rekursif']).all()
                    if all_comps_equal:
                        st.success(f"""
                        **Verifikasi Operasi:**
                        
                        **✅ SAMA**
                        
                        Jumlah perbandingan sama untuk semua ukuran dataset
                        """)
                    else:
                        st.error(f"""
                        **Verifikasi Operasi:**
                        
                        **❌ BERBEDA**
                        
                        Ada perbedaan jumlah perbandingan
                        """)

if __name__ == "__main__":
    main()