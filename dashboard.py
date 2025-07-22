import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Control de Seguimiento de Daños", 
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load and preprocess the Excel data"""
    df = pd.read_excel("reporte_danos.xlsx")
    
    # Clean executive names to remove trailing spaces
    df['Ejecutivo'] = df['Ejecutivo'].str.strip()
    
    # Convert date columns to datetime
    date_columns = ['FEnvío Cap', 'Carta cobertura', '30 Días Pres. Cliente', '69 Días Sol. Aseguradora', 
                   'Ejecutivo Fcap', 'Ejecutivo 5 días', 'Ejecutivo 30 días', 'Ejecutivo 69 días']
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def get_week_range(date):
    """Get the start and end of the week for a given date"""
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end

def format_date_spanish(date):
    """Convert date to Spanish format: '21 de julio'"""
    spanish_months = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
        5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
        9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }
    
    day = date.day
    month = spanish_months[date.month]
    return f"{day} de {month}"

def get_week_range_spanish(week_type):
    """Get week range formatted in Spanish based on week type"""
    today = datetime.now()
    current_week_start, current_week_end = get_week_range(today)
    past_week_start = current_week_start - timedelta(days=7)
    past_week_end = current_week_start - timedelta(days=1)
    
    if week_type == "Current Week":
        start_str = format_date_spanish(current_week_start)
        end_str = format_date_spanish(current_week_end)
        return f"{start_str} al {end_str}"
    elif week_type == "Past Week":
        start_str = format_date_spanish(past_week_start)
        end_str = format_date_spanish(past_week_end)
        return f"{start_str} al {end_str}"
    else:  # Both weeks
        start_str = format_date_spanish(past_week_start)
        end_str = format_date_spanish(current_week_end)
        return f"{start_str} al {end_str}"

def filter_by_week(df, week_type, base_column):
    """Filter dataframe by week type using specified base column"""
    today = datetime.now()
    current_week_start, current_week_end = get_week_range(today)
    past_week_start = current_week_start - timedelta(days=7)
    past_week_end = current_week_start - timedelta(days=1)
    
    if week_type == "Current Week":
        return df[(df[base_column] >= current_week_start) & (df[base_column] <= current_week_end)]
    elif week_type == "Past Week":
        return df[(df[base_column] >= past_week_start) & (df[base_column] <= past_week_end)]
    else:  # Both weeks
        return df[(df[base_column] >= past_week_start) & (df[base_column] <= current_week_end)]

def get_missing_dates(df, column_pairs):
    """Get records with missing dates in executive columns based on column pairs"""
    missing_data = []
    
    # Column mapping: base_column -> executive_column
    column_mapping = {
        'FEnvío Cap': 'Ejecutivo Fcap',
        'Carta cobertura': 'Ejecutivo 5 días',
        '30 Días Pres. Cliente': 'Ejecutivo 30 días',
        '69 Días Sol. Aseguradora': 'Ejecutivo 69 días'
    }
    
    for idx, row in df.iterrows():
        missing_actions = []
        base_columns_used = []
        
        for base_col, exec_col in column_pairs.items():
            if pd.isna(row[exec_col]):
                missing_actions.append(exec_col)
                base_columns_used.append(base_col)
        
        if missing_actions:
            # Calculate days of delay
            base_date = row[base_columns_used[0]] if base_columns_used else None
            today = datetime.now()
            
            if pd.isna(base_date):
                days_delay = "Sin fecha"
            else:
                days_delay = (today - base_date).days
            
            # Format base date for display
            if pd.isna(base_date):
                formatted_base_date = "Sin fecha"
            else:
                formatted_base_date = base_date.strftime('%d/%m/%Y') if pd.notnull(base_date) else "Sin fecha"
            
            missing_data.append({
                'ID': row['ID'],
                'Cliente': row['Cliente'],
                'Pólizas': row['Pólizas'],
                'Fecha Base': formatted_base_date,
                'SRamoNombre': row['SRamoNombre'],
                'Ejecutivo': row['Ejecutivo'],
                'Base Column': ', '.join(base_columns_used),
                'PrimaNeta': row['PrimaNeta'],
                'Días de Retraso': days_delay
            })
    
    return pd.DataFrame(missing_data)

def create_executive_summary(df):
    """Create executive performance summary"""
    summary = df.groupby('Ejecutivo').agg({
        'ID': 'count',
        'Cliente': 'nunique',
        'PrimaNeta': 'sum'
    }).round(2)
    
    summary.columns = ['Casos Pendientes', 'Clientes Únicos', 'Prima Neta Total']
    summary['Prima Neta Total'] = summary['Prima Neta Total'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
    
    return summary.sort_values('Casos Pendientes', ascending=False)

def main():
    # Load data first (needed for filters)
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return
    
    # Sidebar filters (moved before title to get week selection)
    st.sidebar.header("🔍 Filtros")
    
    # Week filter (moved up to be available for title)
    week_options = ["Current Week", "Past Week", "Both Weeks"]
    selected_week = st.sidebar.selectbox("📅 Período", week_options)
    
    # Executive filter
    executives = ['Todos'] + sorted(df['Ejecutivo'].dropna().unique().tolist())
    selected_executive = st.sidebar.selectbox("👤 Ejecutivo", executives)
    
    # Dynamic title based on week selection
    st.title("📊 Control de Seguimiento")
    week_range_text = get_week_range_spanish(selected_week)
    st.markdown(f"### {week_range_text}")
    st.markdown("Dashboard para monitoreo de fechas límite y acciones pendientes")
    
    # Show data loading success
    st.success(f"✅ Datos cargados: {len(df)} registros")
    
    # Action columns filter - show as pairs
    column_pairs = {
        'FEnvío Cap': 'Ejecutivo Fcap',
        'Carta cobertura': 'Ejecutivo 5 días',
        '30 Días Pres. Cliente': 'Ejecutivo 30 días',
        '69 Días Sol. Aseguradora': 'Ejecutivo 69 días'
    }
    
    selected_base_columns = st.sidebar.multiselect(
        "📋 Procesos a Monitorear", 
        list(column_pairs.keys()), 
        default=list(column_pairs.keys())
    )
    
    # Create the pairs dictionary for selected columns
    selected_pairs = {base: exec_col for base, exec_col in column_pairs.items() if base in selected_base_columns}
    
    if not selected_pairs:
        st.warning("⚠️ Selecciona al menos un proceso para monitorear")
        return
    
    # Filter data by combining all selected base columns
    all_filtered_dfs = []
    for base_col in selected_base_columns:
        week_filtered = filter_by_week(df, selected_week, base_col)
        if selected_executive != 'Todos':
            week_filtered = week_filtered[week_filtered['Ejecutivo'] == selected_executive]
        all_filtered_dfs.append(week_filtered)
    
    # Combine all filtered dataframes and remove duplicates
    if all_filtered_dfs:
        filtered_df = pd.concat(all_filtered_dfs).drop_duplicates(subset=['ID'])
    else:
        filtered_df = pd.DataFrame()
    
    # Get missing dates
    missing_df = get_missing_dates(filtered_df, selected_pairs)
    
    if missing_df.empty:
        st.success("🎉 ¡Excelente! No hay acciones pendientes para los filtros seleccionados")
        return
    
    # Executive Performance Summary
    st.subheader("👤 Resumen por Ejecutivo")
    executive_summary = create_executive_summary(missing_df)
    st.dataframe(executive_summary, use_container_width=True)
    
    # Detailed table
    st.subheader("📋 Detalle de Acciones Pendientes")
    
    # Search functionality
    search_term = st.text_input("🔍 Buscar por Cliente o Póliza")
    
    display_df = missing_df.copy()
    if search_term:
        mask = (display_df['Cliente'].str.contains(search_term, case=False, na=False) | 
                display_df['Pólizas'].str.contains(search_term, case=False, na=False))
        display_df = display_df[mask]
    
    # Priority highlighting with stronger colors for dark mode
    def highlight_priority(row):
        days_delay = row['Días de Retraso']
        
        if days_delay == "Sin fecha":
            return ['background-color: #dc3545; color: white'] * len(row)  # Strong red for no date
        
        if days_delay > 7:  # Overdue
            return ['background-color: #dc3545; color: white'] * len(row)  # Strong red
        elif days_delay > 3:  # Warning
            return ['background-color: #ffc107; color: black'] * len(row)  # Strong yellow
        else:  # OK
            return ['background-color: #28a745; color: white'] * len(row)  # Strong green
    
    styled_df = display_df.style.apply(highlight_priority, axis=1)
    st.dataframe(styled_df, use_container_width=True)
    
    # Legend (simplified, without title)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🔴 **Rojo**: Más de 7 días de retraso o sin fecha")
    
    with col2:
        st.markdown("🟡 **Amarillo**: 3-7 días de retraso")
    
    with col3:
        st.markdown("🟢 **Verde**: Menos de 3 días de retraso")
    
    # Export functionality
    if st.button("📥 Exportar a Excel"):
        output_file = f"reporte_pendientes_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        display_df.to_excel(output_file, index=False)
        st.success(f"✅ Archivo exportado: {output_file}")
    
    # Visualization - Pie chart by branch
    st.subheader("📊 Distribución por Ramo")
    branch_counts = missing_df.groupby('SRamoNombre')['ID'].count().reset_index()
    fig_pie = px.pie(
        branch_counts, 
        values='ID', 
        names='SRamoNombre',
        title="Distribución por Ramo"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

if __name__ == "__main__":
    main()
