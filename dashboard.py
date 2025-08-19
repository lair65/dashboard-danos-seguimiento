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

def get_period_range_spanish(period_type):
    """Get period range formatted in Spanish based on period type"""
    today = datetime.now()
    current_week_start, current_week_end = get_week_range(today)
    
    if period_type == "Semana en Curso":
        start_str = format_date_spanish(current_week_start)
        end_str = format_date_spanish(current_week_end)
        return f"{start_str} al {end_str}"
    elif period_type == "Semana Pasada":
        past_week_start = current_week_start - timedelta(days=7)
        past_week_end = current_week_start - timedelta(days=1)
        start_str = format_date_spanish(past_week_start)
        end_str = format_date_spanish(past_week_end)
        return f"{start_str} al {end_str}"
    elif period_type == "1 Semana Adelante":
        future_week_start = current_week_end + timedelta(days=1)
        future_week_end = future_week_start + timedelta(days=6)
        start_str = format_date_spanish(future_week_start)
        end_str = format_date_spanish(future_week_end)
        return f"{start_str} al {end_str}"
    elif period_type == "2 Semanas Pasadas":
        two_weeks_past_start = current_week_start - timedelta(days=14)
        two_weeks_past_end = current_week_start - timedelta(days=1)
        start_str = format_date_spanish(two_weeks_past_start)
        end_str = format_date_spanish(two_weeks_past_end)
        return f"{start_str} al {end_str}"
    elif period_type == "2 Semanas Adelante":
        two_weeks_future_start = current_week_end + timedelta(days=1)
        two_weeks_future_end = current_week_end + timedelta(days=14)
        start_str = format_date_spanish(two_weeks_future_start)
        end_str = format_date_spanish(two_weeks_future_end)
        return f"{start_str} al {end_str}"
    elif period_type == "Mes Pasado":
        last_month = today.replace(day=1) - timedelta(days=1)
        month_start = last_month.replace(day=1)
        start_str = format_date_spanish(month_start)
        end_str = format_date_spanish(last_month)
        return f"{start_str} al {end_str}"
    elif period_type == "Mes Actual":
        month_start = today.replace(day=1)
        next_month = month_start + timedelta(days=32)
        month_end = next_month.replace(day=1) - timedelta(days=1)
        start_str = format_date_spanish(month_start)
        end_str = format_date_spanish(month_end)
        return f"{start_str} al {end_str}"
    elif period_type == "1 Mes Adelante":
        next_month_start = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        month_after = next_month_start + timedelta(days=32)
        next_month_end = month_after.replace(day=1) - timedelta(days=1)
        start_str = format_date_spanish(next_month_start)
        end_str = format_date_spanish(next_month_end)
        return f"{start_str} al {end_str}"
    else:  # Both weeks (legacy)
        past_week_start = current_week_start - timedelta(days=7)
        start_str = format_date_spanish(past_week_start)
        end_str = format_date_spanish(current_week_end)
        return f"{start_str} al {end_str}"

def filter_by_period(df, period_type, base_column):
    """Filter dataframe by period type using specified base column"""
    today = datetime.now()
    current_week_start, current_week_end = get_week_range(today)
    
    if period_type == "Semana en Curso":
        start_date, end_date = current_week_start, current_week_end
    elif period_type == "Semana Pasada":
        start_date = current_week_start - timedelta(days=7)
        end_date = current_week_start - timedelta(days=1)
    elif period_type == "1 Semana Adelante":
        start_date = current_week_end + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
    elif period_type == "2 Semanas Pasadas":
        start_date = current_week_start - timedelta(days=14)
        end_date = current_week_start - timedelta(days=1)
    elif period_type == "2 Semanas Adelante":
        start_date = current_week_end + timedelta(days=1)
        end_date = current_week_end + timedelta(days=14)
    elif period_type == "Mes Pasado":
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month
    elif period_type == "Mes Actual":
        start_date = today.replace(day=1)
        next_month = start_date + timedelta(days=32)
        end_date = next_month.replace(day=1) - timedelta(days=1)
    elif period_type == "1 Mes Adelante":
        start_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        month_after = start_date + timedelta(days=32)
        end_date = month_after.replace(day=1) - timedelta(days=1)
    else:  # Both weeks (legacy)
        start_date = current_week_start - timedelta(days=7)
        end_date = current_week_end
    
    return df[(df[base_column] >= start_date) & (df[base_column] <= end_date)]

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
    # Create a copy and convert PrimaNeta back to numeric for aggregation
    df_copy = df.copy()
    df_copy['PrimaNeta_numeric'] = df_copy['PrimaNeta'].str.replace('$', '').str.replace(',', '').astype(float)
    
    summary = df_copy.groupby('Ejecutivo').agg({
        'ID': 'count',
        'Cliente': 'nunique',
        'PrimaNeta_numeric': 'sum'
    }).round(2)
    
    summary.columns = ['Casos Pendientes', 'Clientes Únicos', 'Prima Neta Total']
    summary['Prima Neta Total'] = summary['Prima Neta Total'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
    
    return summary.sort_values('Casos Pendientes', ascending=False)

def get_all_records_for_process(df, base_column, exec_column, selected_period, selected_executive):
    """Get ALL records for a specific process with color coding"""
    # Filter by period
    period_filtered = filter_by_period(df, selected_period, base_column)
    
    # Filter by executive if selected
    if selected_executive != 'Todos':
        period_filtered = period_filtered[period_filtered['Ejecutivo'] == selected_executive]
    
    if period_filtered.empty:
        return pd.DataFrame()
    
    # Process ALL records (not just missing ones)
    today = datetime.now().date()  # Use date only, ignore time
    processed_data = []
    
    for idx, row in period_filtered.iterrows():
        base_date = row[base_column]
        exec_date = row[exec_column]
        
        # Calculate status and color coding
        if pd.notna(exec_date):
            # Green: Has executive action date
            status = "Completado"
            color_priority = "green"
            formatted_exec_date = exec_date.strftime('%d/%m/%Y')
        else:
            # No executive action date
            if pd.isna(base_date):
                # Red: No base date available
                status = "Sin fecha base"
                color_priority = "red"
                formatted_exec_date = "Sin acción"
            else:
                # Calculate days until deadline (using date only)
                days_until_deadline = (base_date.date() - today).days
                
                if days_until_deadline > 1:
                    # Yellow: 3+ days remaining
                    status = f"{days_until_deadline} días restantes"
                    color_priority = "yellow"
                else:
                    # Red: Deadline today or overdue
                    if days_until_deadline <= 0:
                        status = f"{abs(days_until_deadline)} días vencido"
                    else:
                        status = "Vence hoy" if days_until_deadline == 0 else f"{days_until_deadline} día(s) restante(s)"
                    color_priority = "red"
                
                formatted_exec_date = "Pendiente"
        
        # Format base date
        formatted_base_date = base_date.strftime('%d/%m/%Y') if pd.notna(base_date) else "Sin fecha"
        
        # Format PrimaNeta with currency
        formatted_prima = f"${row['PrimaNeta']:,.2f}" if pd.notna(row['PrimaNeta']) else "$0.00"
        
        processed_data.append({
            'ID': row['ID'],
            'Cliente': row['Cliente'],
            'Pólizas': row['Pólizas'],
            'Fecha Base': formatted_base_date,
            'Fecha Ejecutivo': formatted_exec_date,
            'Ejecutivo': row['Ejecutivo'],
            'SRamoNombre': row['SRamoNombre'],
            'Status': status,
            'PrimaNeta': formatted_prima,
            'Color Priority': color_priority
        })
    
    return pd.DataFrame(processed_data)


def get_simple_counter(total_count):
    """Get simple counter without emojis or colors"""
    return f"{total_count} registros"

def main():
    # Custom CSS for better dropdown styling
    st.markdown("""
    <style>
    /* Force dark theme for all dropdowns */
    .stSelectbox > div > div > div {
        background-color: #2c3642 !important;
        border: 1px solid #3d4a56 !important;
        border-radius: 8px;
        color: white !important;
    }
    
    /* Selectbox text styling */
    .stSelectbox > div > div > div > div {
        color: white !important;
        background-color: #2c3642 !important;
    }
    
    /* Remove text selection highlight */
    .stSelectbox * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        text-shadow: none !important;
        -webkit-text-stroke: 0 !important;
    }
    
    /* Hover effect for selectboxes */
    .stSelectbox > div > div > div:hover {
        background-color: #374149 !important;
        border-color: #4a5661 !important;
        box-shadow: none !important;
    }
    
    /* Dropdown options styling */
    .stSelectbox [data-baseweb="popover"] {
        background-color: #2c3642 !important;
    }
    
    .stSelectbox [data-baseweb="menu"] {
        background-color: #2c3642 !important;
        border: 1px solid #3d4a56 !important;
    }
    
    .stSelectbox [data-baseweb="menu"] > ul {
        background-color: #2c3642 !important;
    }
    
    .stSelectbox [data-baseweb="option"] {
        background-color: #2c3642 !important;
        color: white !important;
    }
    
    .stSelectbox [data-baseweb="option"]:hover {
        background-color: #374149 !important;
        color: white !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div > div {
        background-color: #2c3642 !important;
        border: 1px solid #3d4a56 !important;
        border-radius: 8px;
        color: white !important;
    }
    
    /* Multiselect text styling */
    .stMultiSelect > div > div > div * {
        color: white !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        text-shadow: none !important;
        -webkit-text-stroke: 0 !important;
    }
    
    .stMultiSelect > div > div > div:hover {
        background-color: #374149 !important;
        border-color: #4a5661 !important;
        box-shadow: none !important;
    }
    
    /* Selected items in multiselect */
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: #4a5661 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Multiselect dropdown options */
    .stMultiSelect [data-baseweb="popover"] {
        background-color: #2c3642 !important;
    }
    
    .stMultiSelect [data-baseweb="menu"] {
        background-color: #2c3642 !important;
        border: 1px solid #3d4a56 !important;
    }
    
    .stMultiSelect [data-baseweb="option"] {
        background-color: #2c3642 !important;
        color: white !important;
    }
    
    .stMultiSelect [data-baseweb="option"]:hover {
        background-color: #374149 !important;
        color: white !important;
    }
    
    /* Force dark theme for entire application */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }
    
    /* Sidebar dark theme */
    .css-1d391kg {
        background-color: #262730 !important;
    }
    
    /* Text inputs dark theme */
    .stTextInput > div > div > input {
        background-color: #323d45 !important;
        color: white !important;
        border: 1px solid #4a5661 !important;
    }
    
    /* Buttons dark theme */
    .stButton > button {
        background-color: #323d45 !important;
        color: white !important;
        border: 1px solid #4a5661 !important;
    }
    
    .stButton > button:hover {
        background-color: #3e4a52 !important;
        border-color: #5a6870 !important;
    }
    
    /* DataFrames dark theme */
    .stDataFrame {
        background-color: #262730 !important;
    }
    
    /* Info/Success/Error messages dark theme */
    .stAlert {
        background-color: #323d45 !important;
        color: white !important;
        border: 1px solid #4a5661 !important;
    }
    
    /* Headers and text dark theme */
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
    
    /* Force all text to be light colored */
    .stMarkdown, .stText, p, div, span, label {
        color: #fafafa !important;
    }
    
    /* Metrics containers */
    [data-testid="metric-container"] {
        background-color: #323d45 !important;
        border: 1px solid #4a5661 !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load data first (needed for filters)
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtros")
    
    # Period filter with 8 options
    period_options = [
        "Semana en Curso", "Semana Pasada", "1 Semana Adelante",
        "2 Semanas Pasadas", "2 Semanas Adelante", 
        "Mes Pasado", "Mes Actual", "1 Mes Adelante"
    ]
    selected_period = st.sidebar.selectbox("📅 Período", period_options)
    
    # Executive filter
    executives = ['Todos'] + sorted(df['Ejecutivo'].dropna().unique().tolist())
    selected_executive = st.sidebar.selectbox("👤 Ejecutivo", executives)
    
    # Dynamic title based on period selection
    st.title("📊 Control de Seguimiento")
    period_range_text = get_period_range_spanish(selected_period)
    st.markdown(f"### {period_range_text}")
    
    # Show data loading success
    st.success(f"Datos cargados: {len(df)} registros")
    
    # Process definitions - all processes displayed
    processes = {
        'FEnvío Cap': 'Ejecutivo Fcap',
        'Carta cobertura': 'Ejecutivo 5 días',
        '30 Días Pres. Cliente': 'Ejecutivo 30 días',
        '69 Días Sol. Aseguradora': 'Ejecutivo 69 días'
    }
    
    # First, collect all data for global summary
    all_process_data = []
    for process_name, exec_column in processes.items():
        process_data = get_all_records_for_process(df, process_name, exec_column, selected_period, selected_executive)
        if not process_data.empty:
            all_process_data.append(process_data)
    
    # Executive summary section (cleaned up layout)
    st.markdown("---")
    
    if all_process_data:
        # Combine all process data for summary
        combined_df = pd.concat(all_process_data).drop_duplicates(subset=['ID'])
        
        # Executive Performance Summary
        st.subheader("👤 Resumen por Ejecutivo")
        
        # Global statistics as small text below the title
        total_records = len(combined_df)
        completed_records = len(combined_df[combined_df['Color Priority'] == 'green'])
        pending_records = len(combined_df[combined_df['Color Priority'].isin(['yellow', 'red'])])
        
        st.markdown(f"**Total:** {total_records} registros | **Completados:** {completed_records} | **Pendientes:** {pending_records}")
        
        executive_summary = create_executive_summary(combined_df)
        st.dataframe(executive_summary, use_container_width=True)
        
        # Global export
        if st.button("Exportar Resumen Global"):
            output_file = f"resumen_global_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            combined_df.to_excel(output_file, index=False)
            st.success(f"Archivo exportado: {output_file}")
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados")
    
    # Display each process in its own section (after global summary)
    for process_name, exec_column in processes.items():
        st.markdown("---")  # Separator line
        
        # Get ALL data for this specific process (not just missing)
        process_all_df = get_all_records_for_process(
            df, process_name, exec_column, selected_period, selected_executive
        )
        
        # Simple counter header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"📋 {process_name}")
        with col2:
            if not process_all_df.empty:
                counter_text = get_simple_counter(len(process_all_df))
                st.markdown(f"""
                <div style="text-align: right; padding: 5px; border: 1px solid #4a5661; 
                            border-radius: 4px; font-size: 14px; background-color: #323d45; color: white;">
                    {counter_text}
                </div>
                """, unsafe_allow_html=True)
        
        if process_all_df.empty:
            st.info(f"No hay registros para {process_name} en el período seleccionado")
        else:
            # Search functionality for this process
            search_key = f"search_{process_name.replace(' ', '_')}"
            search_term = st.text_input(
                f"🔍 Buscar en {process_name}", 
                key=search_key
            )
            
            display_df = process_all_df.copy()
            if search_term:
                mask = (display_df['Cliente'].str.contains(search_term, case=False, na=False) | 
                        display_df['Pólizas'].str.contains(search_term, case=False, na=False))
                display_df = display_df[mask]
            
            # First remove Color Priority column from display
            display_columns = [col for col in display_df.columns if col != 'Color Priority']
            display_df_clean = display_df[display_columns].copy()
            
            # Create color mapping based on original data
            color_mapping = display_df['Color Priority'].to_dict()
            
            # Apply styling using the color mapping
            def highlight_by_priority(row):
                # Get the color priority from the mapping using the row's index
                color_priority = color_mapping.get(row.name, '')
                
                if color_priority == 'green':
                    return ['background-color: #28a745; color: white'] * len(row)
                elif color_priority == 'yellow':
                    return ['background-color: #ffc107; color: black'] * len(row)
                elif color_priority == 'red':
                    return ['background-color: #dc3545; color: white'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = display_df_clean.style.apply(highlight_by_priority, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Smaller export button without emoji
            if st.button(f"Exportar {process_name}", key=f"export_{process_name.replace(' ', '_')}"):
                safe_name = process_name.replace(' ', '_').replace(':', '')
                output_file = f"reporte_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                display_df_clean.to_excel(output_file, index=False)
                st.success(f"Archivo exportado: {output_file}")
    

if __name__ == "__main__":
    main()