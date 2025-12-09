import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Tuple
import random
import sys

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Linear Search - Marketplace",
    page_icon="🔍",
    layout="wide"
)

# ==================== ALGORITMA LINEAR SEARCH ====================

def linear_search_iteratif(products: List[str], keyword: str) -> Tuple[int, int]:
    """
    Linear Search versi Iteratif
    Returns: (index, jumlah perbandingan)
    """
    comparisons = 0
    keyword_lower = keyword.lower()
    
    for i in range(len(products)):
        comparisons += 1
        if keyword_lower in products[i].lower():
            return i, comparisons
    
    return -1, comparisons

def linear_search_rekursif(products: List[str], keyword: str, index: int = 0, comparisons: int = 0) -> Tuple[int, int]:
    """
    Linear Search versi Rekursif
    Returns: (index, jumlah perbandingan)
    """
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

# ==================== GENERATOR DATA ====================

def generate_product_names(n: int) -> List[str]:
    """Generate nama produk dummy untuk testing"""
    categories = ['Laptop', 'Smartphone', 'Tablet', 'Headphone', 'Smartwatch', 
                  'Camera', 'Speaker', 'Monitor', 'Keyboard', 'Mouse']
    brands = ['Samsung', 'Apple', 'Asus', 'Lenovo', 'HP', 'Dell', 'Sony', 
              'Xiaomi', 'Oppo', 'Vivo', 'Logitech', 'JBL']
    adjectives = ['Pro', 'Max', 'Ultra', 'Premium', 'Gaming', 'Wireless', 
                  'Portable', 'Professional', 'Advanced', 'Smart']
    
    products = []
    for i in range(n):
        category = random.choice(categories)
        brand = random.choice(brands)
        adjective = random.choice(adjectives)
        model = random.randint(1, 999)
        
        product = f"{brand} {category} {adjective} {model}"
        products.append(product)
    
    return products

# ==================== FUNGSI PENGUJIAN ====================

def run_performance_test(sizes: List[int], keyword: str = "Gaming") -> pd.DataFrame:
    """Menjalankan pengujian performa pada berbagai ukuran dataset"""
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, size in enumerate(sizes):
        status_text.text(f"Testing ukuran data: {size:,} produk...")
        
        # Generate data
        products = generate_product_names(size)
        
        # Best case: keyword di awal
        products_best = products.copy()
        products_best[0] = f"Gaming Laptop Pro"
        
        # Worst case: keyword di akhir
        products_worst = products.copy()
        products_worst[-1] = f"Gaming Laptop Pro"
        
        # Average case: keyword di tengah
        products_avg = products.copy()
        products_avg[size // 2] = f"Gaming Laptop Pro"
        
        # Test Iteratif - Best Case
        start = time.perf_counter()
        idx_iter_best, comp_iter_best = linear_search_iteratif(products_best, keyword)
        time_iter_best = (time.perf_counter() - start) * 1000  # ms
        
        # Test Iteratif - Worst Case
        start = time.perf_counter()
        idx_iter_worst, comp_iter_worst = linear_search_iteratif(products_worst, keyword)
        time_iter_worst = (time.perf_counter() - start) * 1000
        
        # Test Iteratif - Average Case
        start = time.perf_counter()
        idx_iter_avg, comp_iter_avg = linear_search_iteratif(products_avg, keyword)
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
            'Rek Best Comp': comp_rek_best,
            'Rek Worst Comp': comp_rek_worst,
        })
        
        progress_bar.progress((idx + 1) / len(sizes))
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)

# ==================== VISUALISASI ====================

def create_time_comparison_chart(df: pd.DataFrame, case: str = "Worst"):
    """Membuat grafik perbandingan waktu eksekusi"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Ukuran Data'],
        y=df[f'Iteratif {case} (ms)'],
        mode='lines+markers',
        name=f'Iteratif ({case} Case)',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8)
    ))
    
    # Filter data rekursif yang valid (tidak None)
    df_valid = df[df[f'Rekursif {case} (ms)'].notna()].copy()
    
    if not df_valid.empty:
        fig.add_trace(go.Scatter(
            x=df_valid['Ukuran Data'],
            y=df_valid[f'Rekursif {case} (ms)'],
            mode='lines+markers',
            name=f'Rekursif ({case} Case)',
            line=dict(color='#A23B72', width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title=f'Perbandingan Waktu Eksekusi - {case} Case',
        xaxis_title='Ukuran Dataset (jumlah produk)',
        yaxis_title='Waktu Eksekusi (ms)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig

def create_comparison_count_chart(df: pd.DataFrame):
    """Membuat grafik jumlah perbandingan"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Ukuran Data'],
        y=df['Iter Best Comp'],
        mode='lines+markers',
        name='Iteratif (Best)',
        line=dict(dash='dot')
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Ukuran Data'],
        y=df['Iter Worst Comp'],
        mode='lines+markers',
        name='Iteratif (Worst)',
        line=dict(color='#2E86AB', width=3)
    ))
    
    # Filter data rekursif yang valid
    df_valid = df[df['Rek Worst Comp'].notna()].copy()
    
    if not df_valid.empty:
        fig.add_trace(go.Scatter(
            x=df_valid['Ukuran Data'],
            y=df_valid['Rek Worst Comp'],
            mode='lines+markers',
            name='Rekursif (Worst)',
            line=dict(color='#A23B72', width=3)
        ))
    
    fig.update_layout(
        title='Jumlah Perbandingan String',
        xaxis_title='Ukuran Dataset',
        yaxis_title='Jumlah Perbandingan',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig

# ==================== MAIN APP ====================

def main():
    st.title("🔍 Analisis Kompleksitas Linear Search")
    st.markdown("### Perbandingan Iteratif vs Rekursif pada Pencarian Produk Marketplace")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        mode = st.radio(
            "Pilih Mode:",
            ["🎯 Demo Pencarian", "📊 Analisis Performa"]
        )
        
        st.markdown("---")
        st.markdown("**Tentang Aplikasi**")
        st.info("""
        Aplikasi ini menganalisis perbandingan kompleksitas waktu 
        antara Linear Search Iteratif dan Rekursif pada sistem 
        pencarian produk marketplace.
        """)
    
    # Mode 1: Demo Pencarian
    if mode == "🎯 Demo Pencarian":
        st.header("Demo Pencarian Produk")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            num_products = st.slider("Jumlah Produk", 10, 1000, 100)
            keyword = st.text_input("Keyword Pencarian", "Gaming")
        
        with col2:
            st.metric("Total Produk", f"{num_products:,}")
            search_button = st.button("🔍 Cari Produk", type="primary", use_container_width=True)
        
        if search_button:
            # Generate produk
            products = generate_product_names(num_products)
            
            # Sisipkan produk yang mengandung keyword di posisi random
            insert_pos = random.randint(0, len(products) - 1)
            products[insert_pos] = f"Samsung Gaming Laptop Ultra 2024"
            
            # Tampilkan beberapa produk
            with st.expander("📦 Lihat Sample Produk (10 pertama)"):
                for i, p in enumerate(products[:10]):
                    st.text(f"{i+1}. {p}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔄 Linear Search Iteratif")
                start = time.perf_counter()
                idx_iter, comp_iter = linear_search_iteratif(products, keyword)
                time_iter = (time.perf_counter() - start) * 1000
                
                if idx_iter != -1:
                    st.success(f"✅ Ditemukan di index: **{idx_iter}**")
                    st.info(f"Produk: {products[idx_iter]}")
                else:
                    st.error("❌ Tidak ditemukan")
                
                st.metric("Waktu Eksekusi", f"{time_iter:.4f} ms")
                st.metric("Jumlah Perbandingan", comp_iter)
            
            with col2:
                st.subheader("🔁 Linear Search Rekursif")
                start = time.perf_counter()
                try:
                    idx_rek, comp_rek = linear_search_rekursif(products, keyword)
                    time_rek = (time.perf_counter() - start) * 1000
                    
                    if idx_rek != -1:
                        st.success(f"✅ Ditemukan di index: **{idx_rek}**")
                        st.info(f"Produk: {products[idx_rek]}")
                    else:
                        st.error("❌ Tidak ditemukan")
                    
                    st.metric("Waktu Eksekusi", f"{time_rek:.4f} ms")
                    st.metric("Jumlah Perbandingan", comp_rek)
                except RecursionError:
                    st.error("⚠️ Stack Overflow! Data terlalu besar untuk rekursif")
            
            # Perbandingan
            st.markdown("---")
            st.subheader("📊 Perbandingan")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                diff_time = abs(time_iter - time_rek) if 'time_rek' in locals() else 0
                st.metric("Selisih Waktu", f"{diff_time:.4f} ms")
            
            with col2:
                faster = "Iteratif" if time_iter < time_rek else "Rekursif" if 'time_rek' in locals() else "Iteratif"
                st.metric("Lebih Cepat", faster)
            
            with col3:
                speedup = (time_rek / time_iter) if 'time_rek' in locals() and time_iter > 0 else 1
                st.metric("Speedup", f"{speedup:.2f}x")
    
    # Mode 2: Analisis Performa
    else:
        st.header("Analisis Performa Algoritma")
        
        st.markdown("""
        Pengujian akan dilakukan pada berbagai ukuran dataset untuk menganalisis 
        kompleksitas waktu dalam kondisi **Best Case**, **Worst Case**, dan **Average Case**.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_sizes = st.multiselect(
                "Pilih Ukuran Dataset untuk Testing",
                [100, 500, 1000, 5000, 10000, 50000, 100000],
                default=[100, 1000, 5000, 10000]
            )
        
        with col2:
            keyword_test = st.text_input("Keyword untuk Testing", "Gaming")
        
        run_test = st.button("🚀 Jalankan Pengujian", type="primary", use_container_width=True)
        
        if run_test and test_sizes:
            st.markdown("---")
            st.subheader("⏳ Proses Pengujian...")
            
            # Run test
            df_results = run_performance_test(sorted(test_sizes), keyword_test)
            
            # Simpan hasil ke session state
            st.session_state['test_results'] = df_results
            
            st.success("✅ Pengujian Selesai!")
        
        # Tampilkan hasil jika ada
        if 'test_results' in st.session_state:
            df = st.session_state['test_results']
            
            st.markdown("---")
            st.subheader("📈 Hasil Analisis")
            
            # Tabs untuk berbagai visualisasi
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Worst Case", 
                "📊 Average Case", 
                "📊 Best Case", 
                "📋 Data Lengkap"
            ])
            
            with tab1:
                st.plotly_chart(create_time_comparison_chart(df, "Worst"), use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**💡 Insight Worst Case:**")
                    st.write("- Keyword ditemukan di posisi terakhir")
                    st.write("- Algoritma harus memeriksa semua elemen")
                    st.write("- Kompleksitas: O(n)")
                
                with col2:
                    if not df[df['Rekursif Worst (ms)'].notna()].empty:
                        avg_diff = (df['Rekursif Worst (ms)'] - df['Iteratif Worst (ms)']).mean()
                        st.metric("Rata-rata Selisih Waktu", f"{avg_diff:.4f} ms", 
                                 "Rekursif lebih lambat" if avg_diff > 0 else "Rekursif lebih cepat")
            
            with tab2:
                st.plotly_chart(create_time_comparison_chart(df, "Avg"), use_container_width=True)
                
                st.markdown("**💡 Insight Average Case:**")
                st.write("- Keyword ditemukan di posisi tengah")
                st.write("- Memeriksa sekitar n/2 elemen")
                st.write("- Kompleksitas tetap O(n)")
            
            with tab3:
                st.plotly_chart(create_time_comparison_chart(df, "Best"), use_container_width=True)
                
                st.markdown("**💡 Insight Best Case:**")
                st.write("- Keyword ditemukan di posisi pertama")
                st.write("- Hanya 1 kali perbandingan")
                st.write("- Kompleksitas: O(1)")
            
            with tab4:
                st.plotly_chart(create_comparison_count_chart(df), use_container_width=True)
                
                st.markdown("### Tabel Data Lengkap")
                st.dataframe(df, use_container_width=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name="linear_search_analysis.csv",
                    mime="text/csv"
                )
            
            # Kesimpulan
            st.markdown("---")
            st.subheader("📝 Kesimpulan Analisis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Keunggulan Iteratif:**")
                st.write("- Lebih cepat dalam eksekusi")
                st.write("- Efisien memori O(1)")
                st.write("- Tidak ada risiko stack overflow")
                st.write("- Cocok untuk dataset besar")
            
            with col2:
                st.markdown("**⚠️ Kelemahan Rekursif:**")
                st.write("- Overhead pemanggilan fungsi")
                st.write("- Memori stack O(n)")
                st.write("- Risiko stack overflow")
                st.write("- Lebih lambat untuk data besar")

if __name__ == "__main__":
    main()