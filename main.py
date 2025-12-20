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

# ==================== ALGORITMA LINEAR SEARCH (VERSI SINGKAT) ====================

def linear_search_iteratif(products: List[str], keyword: str, mode: str = "first") -> Tuple:
    """
    Linear Search versi iteratif
    Operasi dasar: perbandingan (comparisons)
    """
    comparisons = 0
    keyword_lower = keyword.lower()
    
    if mode == "first":
        # Cari pertama ditemukan
        for i in range(len(products)):
            comparisons += 1  # ⭐ OPERASI DASAR
            if keyword_lower in products[i].lower():
                return i, comparisons  # Found
        
        return -1, comparisons  # Not found
    
    else:  # mode == "all"
        # Cari semua produk
        found_indexes = []
        found_products = []
        
        for i in range(len(products)):
            comparisons += 1  # ⭐ OPERASI DASAR
            if keyword_lower in products[i].lower():
                found_indexes.append(i)
                found_products.append(products[i])
        
        return found_indexes, comparisons, found_products

def linear_search_rekursif(products: List[str], keyword: str, index: int = 0, comparisons: int = 0) -> Tuple[int, int]:
    """
    Linear Search versi rekursif
    Operasi dasar: perbandingan (comparisons)
    """
    # Base case: akhir array
    if index >= len(products):
        return -1, comparisons  # Not found
    
    comparisons += 1  # ⭐ OPERASI DASAR
    keyword_lower = keyword.lower()
    
    # Base case: ditemukan
    if keyword_lower in products[index].lower():
        return index, comparisons  # Found
    
    # Recursive case
    return linear_search_rekursif(products, keyword, index + 1, comparisons)

# ==================== GENERATOR DATA ====================

def generate_product_names(n: int, consistent: bool = False) -> List[str]:
    """
    Generate nama produk dummy untuk testing
    - consistent=True: hasil sama setiap kali (untuk demo/presentasi)
    - consistent=False: hasil random (untuk testing real)
    """
    categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                  'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
    brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
              'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
    adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                  'Portable', 'Professional', 'Advanced', 'Smart']
    
    # Gunakan seed tetap jika ingin konsisten
    if consistent:
        random.seed(42)  # Seed tetap untuk hasil yang sama
    
    products = []
    for i in range(n):
        category = random.choice(categories)
        brand = random.choice(brands)
        adjective = random.choice(adjectives)
        model = random.randint(1, 999)
        
        product = f"{brand} {category} {adjective} {model}"
        products.append(product)
    
    return products

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

def run_performance_test(sizes: List[int], keyword: str = "Gaming", consistent: bool = False) -> pd.DataFrame:
    """Menjalankan pengujian performa pada berbagai ukuran dataset"""
    results = []
    
    for size in sizes:
        # Generate produk
        products = generate_product_names(size, consistent)
        
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
    st.markdown("### Demo Pencarian + Analisis Asimtotik + Performance Testing")
    
    # Sidebar untuk pengaturan
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        st.markdown("### 🎯 Mode Demo")
        num_products = st.slider("Jumlah Produk", 10, 500, 100)
        keyword = st.text_input("Keyword Pencarian", "Gaming")
        
        st.markdown("### 🔧 Tipe Data")
        
        # Pilihan sederhana untuk tipe data
        data_type = st.radio(
            "Pilih Tipe Data:",
            ["🎲 Data Random (Realistic)", "🔒 Data Konsisten (Presentasi)"],
            help="""
            🎲 Data Random: Hasil berbeda setiap kali (seperti dunia nyata)
            🔒 Data Konsisten: Hasil sama setiap kali (cocok untuk demo/kelas)
            """
        )
        
        use_consistent_data = (data_type == "🔒 Data Konsisten (Presentasi)")
        
        st.markdown("---")
        
        st.markdown("### 📊 Performance Testing")
        
        test_sizes = st.multiselect(
            "Pilih Ukuran Dataset untuk Testing:",
            [10, 50, 100, 500, 1000, 5000],
            default=[10, 50, 100, 500, 1000],
            help="Performance test otomatis berjalan dengan ukuran ini"
        )
        
        st.markdown("---")
        st.markdown("### 🎨 Tampilkan Visualisasi")
        show_viz = st.multiselect(
            "Pilih Visualisasi:",
            ["📈 Grafik Asimtotik", "🔍 Kompleksitas Linear", "📋 Tabel Kompleksitas"],
            default=["📈 Grafik Asimtotik", "🔍 Kompleksitas Linear"]
        )
        
        st.markdown("---")
        st.markdown("**ℹ️ Tentang Aplikasi**")
        st.info("""
        **🔍 Fitur Utama:**
        1. **Demo Linear Search** - Cari produk marketplace
        2. **Performance Testing** - Otomatis berjalan
        3. **Analisis Asimtotik** - Visualisasi Big O
        
        **⚡ Operasi Dasar:** 
        - `comparisons += 1` (perbandingan)
        - Dilakukan 1 sampai n kali
        - Menentukan kompleksitas O(n)
        """)
    
    # Container utama
    main_container = st.container()
    
    with main_container:
        # ===== BAGIAN 1: DEMO PENCARIAN =====
        st.header("🎯 Demo Pencarian Produk")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_type = st.radio(
                "Tipe Pencarian:",
                ["🔍 Cari Pertama Ditemukan", "📋 Cari SEMUA Produk"],
                horizontal=True
            )
        
        with col2:
            demo_button = st.button("🚀 Jalankan Demo", type="primary", use_container_width=True)
        
        # State untuk melacak apakah demo telah dijalankan
        demo_run = False
        
        if demo_button:
            demo_run = True
            
            # ===== DEMO PENCARIAN =====
            st.markdown("---")
            st.subheader("📋 Hasil Pencarian")
            
            # Tampilkan info tipe data
            if use_consistent_data:
                st.info("🔧 **Mode Data:** Konsisten (hasil sama setiap kali - cocok untuk presentasi)")
            else:
                st.info("🎲 **Mode Data:** Random (hasil berbeda setiap kali - seperti dunia nyata)")
            
            # Generate produk
            products = generate_product_names(num_products, use_consistent_data)
            
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
            with st.expander("📊 Detail Hasil Pencarian", expanded=True):
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
            
            # ===== PENJELASAN OPERASI DASAR =====
            st.markdown("---")
            st.header("⚡ Analisis Operasi Dasar")
            
            col_expl1, col_expl2 = st.columns(2)
            
            with col_expl1:
                st.markdown("### 🎯 Operasi Dasar: PERBANDINGAN")
                st.code("""
# Linear Search Iteratif
for i in range(len(products)):
    comparisons += 1          # ⭐ OPERASI DASAR
    if keyword in products[i]:
        return i              # Found
    
# Linear Search Rekursif
if index >= len(products):
    return -1                 # Not found
    
comparisons += 1              # ⭐ OPERASI DASAR
if keyword in products[index]:
    return index              # Found
                """, language="python")
            
            with col_expl2:
                st.markdown("### 📊 Analisis Kompleksitas")
                
                cases_data = {
                    'Kasus': ['Best Case', 'Average Case', 'Worst Case'],
                    'Perbandingan': [1, f"n/2 = {num_products//2}", f"n = {num_products}"],
                    'Big O': ['O(1)', 'O(n)', 'O(n)'],
                    'Deskripsi': [
                        'Keyword ditemukan di elemen pertama',
                        'Keyword ditemukan di tengah array',
                        'Keyword tidak ada atau di elemen terakhir'
                    ]
                }
                
                df_cases = pd.DataFrame(cases_data)
                st.dataframe(df_cases, use_container_width=True, hide_index=True)
        
        # ===== BAGIAN 2: PERFORMANCE TESTING (OTOMATIS) =====
        if demo_run and test_sizes:
            st.markdown("---")
            st.header("📊 Performance Testing (Auto-run)")
            
            # Jalankan performance test otomatis
            with st.spinner(f"Menjalankan performance test pada {len(test_sizes)} ukuran dataset..."):
                df_results = run_performance_test(sorted(test_sizes), keyword, use_consistent_data)
            
            # Tampilkan info
            st.success(f"✅ Performance test selesai! Menguji {len(test_sizes)} ukuran dataset")
            
            # Tampilkan grafik performa
            fig_perf = create_performance_chart(df_results)
            st.plotly_chart(fig_perf, use_container_width=True)
            
            # Tampilkan insights
            st.markdown("### 🔍 Insights dari Hasil Testing:")
            
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                # Analisis iteratif
                if len(df_results) > 1:
                    first_time = df_results.iloc[0]['Iteratif Worst (ms)']
                    last_time = df_results.iloc[-1]['Iteratif Worst (ms)']
                    growth_factor = last_time / first_time if first_time > 0 else 0
                    
                    st.metric(
                        "Pertumbuhan Waktu (Iteratif)",
                        f"{growth_factor:.1f}x",
                        help=f"Dari {df_results.iloc[0]['Ukuran Data']} ke {df_results.iloc[-1]['Ukuran Data']} produk"
                    )
            
            with insights_col2:
                # Analisis rekursif
                rek_times = df_results['Rekursif Worst (ms)'].dropna()
                if len(rek_times) > 1:
                    st.metric(
                        "Rekursif Berhasil",
                        f"{len(rek_times)}/{len(df_results)} ukuran",
                        help="Jumlah ukuran data yang berhasil diuji dengan rekursif"
                    )
            
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
        
        **⚡ Operasi Dasar Linear Search:**
        - `comparisons += 1` (perbandingan)
        - Dilakukan 1 sampai n kali
        - Menentukan kompleksitas O(n)
        """)
        
        # Tampilkan visualisasi yang dipilih
        if show_viz:
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
        
        # ===== BAGIAN 4: KESIMPULAN =====
        st.markdown("---")
        st.header("🎯 Kesimpulan & Rekomendasi")
        
        col_concl1, col_concl2 = st.columns(2)
        
        with col_concl1:
            st.success("""
            **✅ Keunggulan Linear Search:**
            
            1. **Sederhana** - mudah diimplementasi
            2. **Universal** - bekerja pada data terurut/tidak terurut
            3. **Operasi Dasar** - hanya perbandingan
            4. **Predictable** - O(1) sampai O(n)
            5. **Stable** - tidak mengubah data asli
            """)
        
        with col_concl2:
            st.warning("""
            **⚠️ Kelemahan Linear Search:**
            
            1. **Slow for large n** - O(n) time complexity
            2. **Inefficient** - harus cek semua elemen di worst case
            3. **Operasi Berulang** - n kali perbandingan
            4. **Not scalable** - tidak cocok untuk big data
            5. **Linear Growth** - waktu tumbuh proporsional dengan n
            """)
        
        # Rekomendasi penggunaan
        st.markdown("### 💡 Rekomendasi Penggunaan")
        
        rec_data = {
            'Use Case': ['Data Kecil (<1000)', 'Data Sedang (1000-10000)', 'Data Besar (>10000)', 
                         'Data Terurut', 'Pencarian Berulang'],
            'Algoritma': ['Linear Search', 'Binary Search / Hash Table', 'Hash Table / Indexing',
                         'Binary Search', 'Hash Table'],
            'Operasi Dasar': ['Perbandingan', 'Perbandingan / Hash', 'Hash',
                            'Perbandingan', 'Hash'],
            'Kompleksitas': ['O(n)', 'O(log n) / O(1)', 'O(1)',
                            'O(log n)', 'O(1)']
        }
        
        df_recommendation = pd.DataFrame(rec_data)
        st.dataframe(df_recommendation, use_container_width=True, hide_index=True)
        
        # Final message
        st.info("""
        **🎓 Takeaway:**
        Linear Search adalah **algoritma fundamental** dengan operasi dasar **perbandingan**.
        
        **📊 Performance Testing** menunjukkan:
        - Waktu eksekusi tumbuh linear dengan ukuran data
        - Iteratif lebih stabil untuk data besar
        - Rekursif berisiko stack overflow
        
        **Pahami operasi dasarnya, pilih algoritma sesuai kebutuhan!**
        """)

if __name__ == "__main__":
    main()