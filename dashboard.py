import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Page config - Force light theme
st.set_page_config(
    page_title="Control de Seguimiento de Daños", 
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data():
    """Load and preprocess the Excel data"""
    df = pd.read_excel("reporte_danos.xlsx")
    
    # Filter out cancelled registries (where Cancelaciones contains 'Si' in any case)
    if 'Cancelaciones' in df.columns:
        df = df[~df['Cancelaciones'].str.upper().str.strip().eq('SI')]
    
    # Clean executive names to remove trailing spaces
    df['Ejecutivo'] = df['Ejecutivo'].str.strip()
    
    # Convert date columns to datetime
    date_columns = ['FEnvío Cap', 'Carta cobertura', '30 Días Pres. Cliente', '69 Días Sol. Aseguradora',
                   'Ejecutivo Fcap', 'Ejecutivo 5 días', 'Ejecutivo 30 días', 'Ejecutivo 69 días',
                   '74 Días Recepcion de  Info. Del cliente', 'Ejecutivo 74 días ', '89 Días Env. Info, al cliente',
                   'Ejecutivo 89 días', '100 Días Solicitud Siniestralidad', 'Ejecutivo 100 días']
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
    end_date = end_date.replace(hour=23, minute=59, second=59)
    return df[(df[base_column] >= start_date) & (df[base_column] <= end_date)]

def filter_by_date_range(df, start_date, end_date, base_column):
    """Filter dataframe by custom date range using specified base column"""
    return df[(df[base_column] >= start_date) & (df[base_column] <= end_date)]

def get_missing_dates(df, column_pairs):
    """Get records with missing dates in executive columns based on column pairs"""
    missing_data = []
    
    # Column mapping: base_column -> executive_column
    column_mapping = {
        'FEnvío Cap': 'Ejecutivo Fcap',
        'Carta cobertura': 'Ejecutivo 5 días',
        '30 Días Pres. Cliente': 'Ejecutivo 30 días',
        '69 Días Sol. Aseguradora': 'Ejecutivo 69 días',
        '74 Días Recepcion de  Info. Del cliente': 'Ejecutivo 74 días ',
        '89 Días Env. Info, al cliente': 'Ejecutivo 89 días',
        '100 Días Solicitud Siniestralidad': 'Ejecutivo 100 días'
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
                'ID': int(row['ID']) if pd.notna(row['ID']) else 0,
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
    """Create executive performance summary with enhanced metrics"""
    if df.empty:
        return pd.DataFrame()

    # Create a copy for processing
    df_copy = df.copy()

    # Extract numeric value from PrimaNeta for aggregation
    def extract_numeric_prima(prima_str):
        if pd.isna(prima_str):
            return 0.0
        # Remove currency symbols and convert to float
        numeric_str = str(prima_str).replace('USD$', '').replace('$', '').replace(',', '')
        try:
            return float(numeric_str)
        except:
            return 0.0

    df_copy['PrimaNeta_numeric'] = df_copy['PrimaNeta'].apply(extract_numeric_prima)

    # Calculate timing statistics
    timing_stats = df_copy.groupby('Ejecutivo')['Estado Tiempo'].value_counts().unstack(fill_value=0)

    # Calculate completion statistics
    completion_stats = df_copy.groupby('Ejecutivo')['Color Priority'].apply(
        lambda x: (x == 'green').sum() / len(x) * 100
    ).round(1)

    # Calculate average response time (only for completed cases)
    def calculate_avg_response_time(group):
        completed = group[group['Color Priority'] == 'green']
        if completed.empty:
            return 0

        response_times = []
        for _, row in completed.iterrows():
            # Find the corresponding base and exec dates from original data
            base_col = None
            exec_col = None

            # Determine which process this is based on the data structure
            # This is a simplified approach - in practice you'd pass this info
            if 'FEnvío Cap' in df.columns:
                try:
                    orig_row = df[df['ID'] == row['ID']].iloc[0]
                    # Try different process combinations
                    process_pairs = [
                        ('FEnvío Cap', 'Ejecutivo Fcap'),
                        ('Carta cobertura', 'Ejecutivo 5 días'),
                        ('30 Días Pres. Cliente', 'Ejecutivo 30 días'),
                        ('69 Días Sol. Aseguradora', 'Ejecutivo 69 días'),
                        ('74 Días Recepcion de  Info. Del cliente', 'Ejecutivo 74 días '),
                        ('89 Días Env. Info, al cliente', 'Ejecutivo 89 días'),
                        ('100 Días Solicitud Siniestralidad', 'Ejecutivo 100 días')
                    ]

                    for base_col, exec_col in process_pairs:
                        if pd.notna(orig_row[base_col]) and pd.notna(orig_row[exec_col]):
                            response_time = (orig_row[exec_col] - orig_row[base_col]).days
                            if response_time >= 0:  # Valid response time
                                response_times.append(response_time)
                            break
                except:
                    pass

        return round(np.mean(response_times), 1) if response_times else 0

    # Group by executive and calculate all metrics
    summary_data = []
    for exec_name in df_copy['Ejecutivo'].unique():
        exec_data = df_copy[df_copy['Ejecutivo'] == exec_name]

        # Basic counts
        total_cases = len(exec_data)
        unique_clients = exec_data['Cliente'].nunique()
        completed_cases = len(exec_data[exec_data['Color Priority'] == 'green'])
        completion_rate = round((completed_cases / total_cases * 100), 1) if total_cases > 0 else 0

        # Timing statistics
        en_tiempo = timing_stats.get('En Tiempo', {}).get(exec_name, 0)
        retrasadas = timing_stats.get('Retrasado', {}).get(exec_name, 0)
        pendientes = timing_stats.get('Pendiente', {}).get(exec_name, 0)
        sin_fecha = timing_stats.get('Sin Fecha Base', {}).get(exec_name, 0)

        # Currency separation
        usd_data = exec_data[exec_data['Moneda'] == 'Dólares']
        nacional_data = exec_data[exec_data['Moneda'] == 'Nacional']

        prima_usd = usd_data['PrimaNeta_numeric'].sum()
        prima_nacional = nacional_data['PrimaNeta_numeric'].sum()

        # Average response time calculation (simplified)
        avg_response = 0  # Placeholder for now, complex to calculate without process context

        summary_data.append({
            'Ejecutivo': exec_name,
            'Total Casos': total_cases,
            'Clientes Únicos': unique_clients,
            'En Tiempo': en_tiempo,
            'Retrasadas': retrasadas,
            'Pendientes': pendientes + sin_fecha,
            '% Completado': completion_rate,
            'Prima USD': f"${prima_usd:,.2f}" if prima_usd > 0 else "$0.00",
            'Prima Nacional': f"${prima_nacional:,.2f}" if prima_nacional > 0 else "$0.00"
        })

    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.set_index('Ejecutivo')

    return summary_df.sort_values('Total Casos', ascending=False)

def get_all_records_for_process(df, base_column, exec_column, selected_period, selected_executive, use_calendar=False, start_date=None, end_date=None):
    """Get ALL records for a specific process with color coding"""
    # Filter by period or date range
    if use_calendar and start_date and end_date:
        period_filtered = filter_by_date_range(df, start_date, end_date, base_column)
    else:
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

        # Determine timing status for new column
        if pd.notna(exec_date) and pd.notna(base_date):
            if exec_date.date() <= base_date.date():
                timing_status = "En Tiempo"
                timing_color = "green"
            else:
                timing_status = "Retrasado"
                timing_color = "red"
        elif pd.notna(exec_date) and pd.isna(base_date):
            timing_status = "Sin Fecha Base"
            timing_color = "yellow"
        else:
            timing_status = "Pendiente"
            timing_color = "yellow"

        # Calculate status and color coding (existing logic)
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

        # Format PrimaNeta with currency symbol
        currency = row.get('Moneda', 'Nacional')
        currency_symbol = '$' if currency == 'Nacional' else 'USD$'
        formatted_prima = f"{currency_symbol}{row['PrimaNeta']:,.2f}" if pd.notna(row['PrimaNeta']) else f"{currency_symbol}0.00"

        processed_data.append({
            'ID': int(row['ID']) if pd.notna(row['ID']) else 0,
            'Cliente': row['Cliente'],
            'Pólizas': row['Pólizas'],
            'Fecha Base': formatted_base_date,
            'Fecha Ejecutivo': formatted_exec_date,
            'Estado Tiempo': timing_status,
            'Ejecutivo': row['Ejecutivo'],
            'PrimaNeta': formatted_prima,
            'Moneda': currency,
            'SRamoNombre': row['SRamoNombre'],
            'Status': status,
            'Color Priority': color_priority,
            'Timing Color': timing_color
        })

    return pd.DataFrame(processed_data)


def get_simple_counter(total_count):
    """Get simple counter without emojis or colors"""
    return f"{total_count}"

def main():
    # Custom CSS for modern, Material Design 3-inspired theme - FINAL POLISH
    st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

    /* --- Base & Typography --- */
    html, body, .stApp, .main {
        font-family: 'Roboto', sans-serif;
        background-color: #f8f9fa; /* Light gray background */
        color: #212529;
    }

    h1, h2, h3 {
        font-weight: 700;
        color: #0d1b2a; /* Dark blue-gray for headers */
    }

    h1 { font-size: 2.25rem; }
    h2 { font-size: 1.75rem; }
    h3 { font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 1rem; }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dee2e6;
    }

    /* --- Main Content --- */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* --- Card Design for Metric Containers --- */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    }

    /* --- Tabs --- */
    [data-testid="stTabs"] {
        border-bottom: 2px solid #dee2e6;
    }
    [data-testid="stTabs"] button {
        font-weight: 600;
        color: #495057;
        padding: 0.75rem 1.25rem;
        border-radius: 8px 8px 0 0;
        transition: all 0.2s ease-in-out;
        border: none;
        background-color: transparent;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #f8f9fa;
        color: #005f73; /* Primary accent color */
        border-bottom: 3px solid #005f73;
    }
    [data-testid="stTabs"] button:hover {
        background-color: #e9ecef;
    }

    /* --- Expander/Accordion --- */
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 0.05rem; /* Reduced spacing */
        transition: box-shadow 0.2s ease-in-out;
    }
    [data-testid="stExpander"]:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.08);
    }
    [data-testid="stExpander"] summary {
        font-weight: 600;
        font-size: 1.1rem;
        color: #0d1b2a;
        padding: 1.25rem 1.5rem;
    }
    [data-testid="stExpander"] .streamlit-expanderContent {
        padding: 0 1.5rem 1.5rem 1.5rem;
    }

    /* --- Table Styling --- */
    .stDataFrame {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        overflow: hidden;
    }
    .stDataFrame table {
        width: 100%;
    }
    .stDataFrame thead th {
        background-color: #f1f3f5;
        color: #343a40;
        font-weight: 600;
        border-bottom: 2px solid #dee2e6;
        padding: 0.75rem;
    }
    .stDataFrame tbody td {
        padding: 0.75rem;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f8f9fa;
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

    # Calendar vs Period selection is now at the top
    use_calendar = st.sidebar.checkbox("Rango de Fechas")

    start_date = None
    end_date = None
    selected_period = None

    if use_calendar:
        start_date = st.sidebar.date_input("Fecha Inicio", value=datetime.now() - timedelta(days=30))
        end_date = st.sidebar.date_input("Fecha Fin", value=datetime.now() + timedelta(days=30))
        # Convert to datetime
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.min.time()).replace(hour=23, minute=59, second=59)
    else:
        period_options = [
            "Semana en Curso", "Semana Pasada", "1 Semana Adelante",
            "2 Semanas Pasadas", "2 Semanas Adelante",
            "Mes Pasado", "Mes Actual", "1 Mes Adelante"
        ]
        selected_period = st.sidebar.selectbox("📅 Período", period_options)

    # Executive filter is now after the date/period filters
    executives = ['Todos'] + sorted(df['Ejecutivo'].dropna().unique().tolist())
    selected_executive = st.sidebar.selectbox("👤 Ejecutivo", executives)

    # Color legend explanation
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Leyenda de Colores**")
    st.sidebar.markdown("""
    - 🟢 **Verde**: Casos completados
    - 🟡 **Amarillo**: Casos con tiempo restante (>1 día)
    - 🔴 **Rojo**: Casos vencidos o que vencen hoy
    """)
    
    # Dynamic title based on selection
    st.title("Control de Seguimiento")

    if use_calendar and start_date and end_date:
        period_range_text = f"{start_date.strftime('%d/%m/%Y')} al {end_date.strftime('%d/%m/%Y')}"
    elif selected_period:
        period_range_text = get_period_range_spanish(selected_period)
    else:
        period_range_text = "Rango de fechas no seleccionado"

    st.markdown(f"### {period_range_text}")

    # Show data loading success
    st.success(f"Datos cargados: {len(df)} registros")

    # Process definitions - all processes displayed
    processes = {
        'FEnvío Cap': 'Ejecutivo Fcap',
        'Carta cobertura': 'Ejecutivo 5 días',
        '30 Días Pres. Cliente': 'Ejecutivo 30 días',
        '69 Días Sol. Aseguradora': 'Ejecutivo 69 días',
        '74 Días Recepcion de  Info. Del cliente': 'Ejecutivo 74 días ',
        '89 Días Env. Info, al cliente': 'Ejecutivo 89 días',
        '100 Días Solicitud Siniestralidad': 'Ejecutivo 100 días'
    }

    # First, collect all data for global summary
    all_process_data = []
    for process_name, exec_column in processes.items():
        process_data = get_all_records_for_process(
            df, process_name, exec_column, selected_period, selected_executive,
            use_calendar, start_date, end_date
        )
        if not process_data.empty:
            all_process_data.append(process_data)
    
    # Create two tabs for better organization
    tab1, tab2 = st.tabs(["Resumen Global", "Detalle por Proceso"])

    with tab1:
        # Executive summary section (cleaned up layout)
        if all_process_data:
            # Combine all process data for summary
            combined_df = pd.concat(all_process_data).drop_duplicates(subset=['ID'])
            
            # Executive Performance Summary
            st.subheader("👤 Resumen por Ejecutivo")

            # Global statistics as small text below the title
            total_records = len(combined_df)
            completed_records = len(combined_df[combined_df['Color Priority'] == 'green'])
            pending_records = len(combined_df[combined_df['Color Priority'].isin(['yellow', 'red'])])

            # Calculate global percentages
            completion_percentage = round((completed_records / total_records * 100), 1) if total_records > 0 else 0
            pending_percentage = round((pending_records / total_records * 100), 1) if total_records > 0 else 0

            st.markdown(f"**Total:** {total_records} registros | **Completados:** {completed_records} | **Pendientes:** {pending_records}")

            # Global percentage section
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("% Global Completado", f"{completion_percentage}%")
            with col2:
                st.metric("% Global Pendiente", f"{pending_percentage}%")
            with col3:
                st.metric("Total Registros", total_records)

            executive_summary = create_executive_summary(combined_df)
            st.dataframe(executive_summary, use_container_width=True)

            # Global export with download button using BytesIO (no disk write)
            output = BytesIO()
            combined_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            st.download_button(
                label="Exportar",
                data=output,
                file_name=f"resumen_global_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay datos para mostrar con los filtros seleccionados")
    
    with tab2:
        # Display each process in its own section (after global summary)
        for process_name, exec_column in processes.items():
            # Get ALL data for this specific process to get the count for the expander title
            process_all_df = get_all_records_for_process(
                df, process_name, exec_column, selected_period, selected_executive,
                use_calendar, start_date, end_date
            )
            
            # Create the title with the count in a subtle way
            expander_title = f"📋 {process_name}  |  {len(process_all_df)} registros"

            with st.expander(expander_title, expanded=True):
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
                    
                    # Remove internal columns from display
                    display_columns = [col for col in display_df.columns if col not in ['Color Priority', 'Timing Color']]
                    display_df_clean = display_df[display_columns].copy()

                    # Create color mapping based on original data
                    color_mapping = display_df['Color Priority'].to_dict()
                    timing_color_mapping = display_df['Timing Color'].to_dict()

                    # Apply styling using the color mapping - Uniform row colors
                    def highlight_by_priority(row):
                        # Get the color priority from the mapping using the row's index
                        color_priority = color_mapping.get(row.name, '')

                        # Apply uniform styling to entire row based on overall priority
                        if color_priority == 'green':
                            return ['background-color: #dcfce7; color: #14532d; border-left: 4px solid #16a34a; font-weight: 600'] * len(row)
                        elif color_priority == 'yellow':
                            return ['background-color: #fef3c7; color: #92400e; border-left: 4px solid #d97706; font-weight: 600'] * len(row)
                        elif color_priority == 'red':
                            return ['background-color: #fee2e2; color: #991b1b; border-left: 4px solid #dc2626; font-weight: 600'] * len(row)
                        else:
                            return [''] * len(row)

                    styled_df = display_df_clean.style.apply(highlight_by_priority, axis=1)
                    st.dataframe(styled_df, use_container_width=True)

                    # Export with download button using BytesIO (no disk write)
                    safe_name = process_name.replace(' ', '_').replace(':', '')
                    output = BytesIO()
                    display_df_clean.to_excel(output, index=False, engine='openpyxl')
                    output.seek(0)

                    st.download_button(
                        label="Exportar",
                        data=output,
                        file_name=f"reporte_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"export_{process_name.replace(' ', '_')}"
                    )
    

if __name__ == "__main__":
    main()