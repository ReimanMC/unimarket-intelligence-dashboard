
# -*- coding: utf-8 -*-
"""
UNIMARKET LATIN FOOD · Decision Dashboard
Versión corregida: mejora de visibilidad en gráficas de rentabilidad.
Ejecutar:
    streamlit run dashboard/unimarket_dashboard.py

Requisitos:
    pandas
    streamlit
    plotly
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="UNIMARKET Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "V5.5 - stable tables visual fix"

DEFAULT_ROOT = Path(r"D:\UNIMARKET_PROJECT")

COLOR_BG = "#070B18"
COLOR_CARD = "#111827"
COLOR_CARD_2 = "#0F172A"
COLOR_TEXT = "#F8FAFC"
COLOR_MUTED = "#A7B0C3"
COLOR_GREEN = "#84D37F"
COLOR_RED = "#E65373"
COLOR_ORANGE = "#F2A64A"
COLOR_BLUE = "#8FD8F7"
COLOR_PURPLE = "#8B6CFF"
COLOR_BORDER = "#2B3654"

MONEY_COLS = [
    "gross_sales_final",
    "net_sales_final",
    "gross_to_net_reduction_final",
    "discount_reduction_final",
    "refund_reduction_final",
    "repayment_recovery_final",
    "cogs_final",
    "gross_profit_final",
    "absolute_negative_gross_profit",
    "positive_net_sales_exposure",
    "zero_cogs_sales_exposure",
    "missing_profitability_sales_exposure",
    "configuration_anomaly_sales_exposure",
    "absolute_cogs_configuration_gap",
]


# ============================================================
# CSS
# ============================================================

def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"] {{
            background: radial-gradient(circle at top right, #131A35 0%, {COLOR_BG} 38%, #050816 100%) !important;
            color: {COLOR_TEXT};
        }}

        [data-testid="stSidebar"] {{
            background: #0B1020 !important;
            border-right: 1px solid {COLOR_BORDER};
        }}

        [data-testid="stSidebar"] * {{
            color: {COLOR_TEXT};
        }}

        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1500px;
        }}

        h1, h2, h3 {{
            color: {COLOR_TEXT};
            letter-spacing: -0.02em;
        }}

        h1 {{
            font-size: 3.2rem !important;
            font-weight: 900 !important;
        }}

        h2 {{
            font-size: 2.0rem !important;
            font-weight: 850 !important;
            margin-top: 1.5rem !important;
        }}

        h3 {{
            font-size: 1.35rem !important;
            font-weight: 800 !important;
        }}

        .subtitle {{
            color: {COLOR_MUTED};
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }}

        .note-box {{
            border-left: 5px solid {COLOR_BLUE};
            background: linear-gradient(90deg, rgba(143,216,247,.12), rgba(17,24,39,.7));
            border-radius: 14px;
            padding: 1rem 1.2rem;
            color: {COLOR_TEXT};
            line-height: 1.55;
            margin: 1rem 0 1.4rem 0;
        }}

        .warning-box {{
            border-left: 5px solid {COLOR_ORANGE};
            background: linear-gradient(90deg, rgba(242,166,74,.14), rgba(17,24,39,.7));
            border-radius: 14px;
            padding: 1rem 1.2rem;
            color: {COLOR_TEXT};
            line-height: 1.55;
            margin: 1rem 0 1.4rem 0;
        }}

        .kpi-card {{
            background: linear-gradient(145deg, rgba(17,24,39,.96), rgba(15,23,42,.94));
            border: 1px solid {COLOR_BORDER};
            border-radius: 24px;
            padding: 1.25rem 1.35rem;
            min-height: 150px;
            box-shadow: 0 14px 40px rgba(0,0,0,.25);
            position: relative;
            overflow: hidden;
        }}

        .kpi-card::after {{
            content: "";
            position: absolute;
            right: -40px;
            top: -50px;
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: rgba(143,216,247,.12);
            filter: blur(8px);
        }}

        .kpi-label {{
            color: {COLOR_MUTED};
            font-size: .82rem;
            text-transform: uppercase;
            letter-spacing: .16em;
            font-weight: 800;
            margin-bottom: .6rem;
        }}

        .kpi-value {{
            color: {COLOR_TEXT};
            font-size: 2.25rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: .5rem;
        }}

        .kpi-help {{
            color: {COLOR_MUTED};
            font-size: .92rem;
            line-height: 1.35;
        }}

        .kpi-green .kpi-value {{ color: {COLOR_GREEN}; }}
        .kpi-red .kpi-value {{ color: {COLOR_RED}; }}
        .kpi-orange .kpi-value {{ color: {COLOR_ORANGE}; }}
        .kpi-blue .kpi-value {{ color: {COLOR_BLUE}; }}

        .section-tabs div[role="tablist"] {{
            gap: .45rem;
        }}

        div[data-baseweb="tab-list"] {{
            gap: .6rem;
        }}

        button[data-baseweb="tab"] {{
            background: #0F172A !important;
            border: 1px solid {COLOR_BORDER} !important;
            border-radius: 16px !important;
            padding: .65rem 1rem !important;
            color: {COLOR_MUTED} !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {COLOR_TEXT} !important;
            background: linear-gradient(90deg, rgba(143,216,247,.22), rgba(139,108,255,.18)) !important;
            border-color: {COLOR_BLUE} !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 16px;
            overflow: hidden;
        }}

        .small-muted {{
            color: {COLOR_MUTED};
            font-size: .92rem;
            line-height: 1.45;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# UTILIDADES
# ============================================================

def money(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "$0"
    return f"${float(value):,.{decimals}f}"


def pct(value: float | int | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "0.00%"
    return f"{float(value):,.{decimals}f}%"


def number(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "0"
    return f"{float(value):,.{decimals}f}"


def safe_sum(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns or df.empty:
        return 0.0
    return float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())


def safe_count(df: pd.DataFrame) -> int:
    return 0 if df is None or df.empty else int(len(df))


def first_existing(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def clean_priority(value: object) -> str:
    s = str(value).strip().lower()
    if s in {"critical", "critico", "crítico"}:
        return "Crítica"
    if s in {"high", "alto", "alta"}:
        return "Alta"
    if s in {"medium", "medio", "media"}:
        return "Media"
    if s in {"low", "bajo", "baja"}:
        return "Baja"
    return "Sin prioridad"


def profitability_label(row: pd.Series) -> str:
    gp = pd.to_numeric(row.get("gross_profit_final", 0), errors="coerce")
    cogs = pd.to_numeric(row.get("cogs_final", None), errors="coerce")
    status = str(row.get("corrected_profitability_scope_status", "")).lower()

    if pd.notna(gp) and gp < 0:
        return "Pérdida / utilidad negativa"
    if pd.isna(cogs):
        return "Sin costo registrado"
    if cogs == 0 and pd.to_numeric(row.get("net_sales_final", 0), errors="coerce") > 0:
        return "COGS cero"
    if "configuration" in status or "anomaly" in status:
        return "Anomalía de configuración"
    margin = pd.to_numeric(row.get("gross_margin_pct_final", None), errors="coerce")
    if pd.notna(margin) and margin < 23:
        return "Margen bajo"
    return "Rentabilidad validada"


def format_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve una tabla limpia para Streamlit sin nombres de columnas duplicados.
    El error anterior ocurría porque algunos CSV ya traían columnas traducidas
    como "Refunds" y al renombrar "refund_reduction_final" se generaban dos columnas
    con el mismo nombre. PyArrow/Streamlit no permite columnas duplicadas.
    """
    if df.empty:
        return df

    out = df.copy()

    # Eliminar columnas duplicadas ANTES del rename.
    out = out.loc[:, ~out.columns.duplicated()].copy()

    rename = {
        "category_context": "Categoría",
        "Name": "Producto",
        "gross_sales_final": "Ventas brutas",
        "net_sales_final": "Ventas netas",
        "sold_final": "Unidades vendidas",
        "gross_to_net_reduction_final": "Reducción bruta a neta",
        "discount_reduction_final": "Descuentos",
        "refund_reduction_final": "Refunds",
        "cogs_final": "COGS / costo",
        "gross_profit_final": "Utilidad bruta",
        "gross_margin_pct_final": "Margen bruto %",
        "final_priority": "Prioridad",
        "priority_readable": "Prioridad",
    }

    out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})

    # Eliminar columnas duplicadas DESPUÉS del rename.
    out = out.loc[:, ~out.columns.duplicated()].copy()

    visible_cols = [
        "Categoría",
        "Producto",
        "Ventas brutas",
        "Ventas netas",
        "Unidades vendidas",
        "Reducción bruta a neta",
        "Descuentos",
        "Refunds",
        "COGS / costo",
        "Utilidad bruta",
        "Margen bruto %",
        "Prioridad",
    ]

    visible_cols = [c for c in visible_cols if c in out.columns]
    out = out[visible_cols].copy()

    # Limpieza final de duplicados por seguridad.
    out = out.loc[:, ~out.columns.duplicated()].copy()

    # Formato visual sin romper tipos internos importantes.
    for col in [
        "Ventas brutas",
        "Ventas netas",
        "Reducción bruta a neta",
        "Descuentos",
        "Refunds",
        "COGS / costo",
        "Utilidad bruta",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").round(2)

    if "Margen bruto %" in out.columns:
        out["Margen bruto %"] = pd.to_numeric(out["Margen bruto %"], errors="coerce").round(2)

    return out


def kpi_card(label: str, value: str, help_text: str = "", style: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi-card {style}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str, warning: bool = False) -> None:
    cls = "warning-box" if warning else "note-box"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def load_data(root: Path) -> dict[str, pd.DataFrame]:
    dash = root / "data" / "dashboard"
    outputs = root / "outputs" / "csv"

    product = load_csv(str(dash / "unimarket_dashboard_product_mart.csv"))
    category = load_csv(str(dash / "unimarket_dashboard_category_mart.csv"))
    finding = load_csv(str(dash / "unimarket_dashboard_finding_mart.csv"))
    kpi = load_csv(str(dash / "unimarket_dashboard_kpi_mart.csv"))
    queue = load_csv(str(dash / "unimarket_dashboard_priority_queue.csv"))

    if product.empty:
        product = load_csv(str(root / "data" / "processed" / "eda_08_final_decision_layer_snapshot.csv"))

    # Complementos EDA previos
    zero_cogs = load_csv(str(outputs / "eda_05b_zero_cogs_records.csv"))
    missing_profit = load_csv(str(outputs / "eda_05b_corrected_profitability_scope_summary.csv"))
    manual = load_csv(str(outputs / "eda_07b_manual_adjustment_records.csv"))
    margin_alert = load_csv(str(outputs / "eda_06_negative_margin_driver_records.csv"))
    low_margin = load_csv(str(outputs / "eda_06_low_margin_driver_records.csv"))
    catalog_queue = load_csv(str(outputs / "eda_07b_actionable_catalog_review_queue.csv"))

    return {
        "product": product,
        "category": category,
        "finding": finding,
        "kpi": kpi,
        "queue": queue,
        "zero_cogs": zero_cogs,
        "missing_profit": missing_profit,
        "manual": manual,
        "margin_alert": margin_alert,
        "low_margin": low_margin,
        "catalog_queue": catalog_queue,
    }


def normalize_product(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()

    # Normalizar columnas esperadas.
    aliases = {
        "gross_sales": "gross_sales_final",
        "net_sales": "net_sales_final",
        "sold": "sold_final",
        "cogs": "cogs_final",
        "gross_profit": "gross_profit_final",
        "gross_margin_pct": "gross_margin_pct_final",
        "discounts": "discount_reduction_final",
        "refunds": "refund_reduction_final",
        "repayments": "repayment_recovery_final",
        "gross_to_net_reduction": "gross_to_net_reduction_final",
    }
    for old, new in aliases.items():
        if new not in out.columns and old in out.columns:
            out[new] = out[old]

    for col in MONEY_COLS + ["gross_margin_pct_final", "sold_final"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    if "final_priority" not in out.columns:
        out["final_priority"] = "low"

    out["priority_readable"] = out["final_priority"].apply(clean_priority)
    out["profitability_readable"] = out.apply(profitability_label, axis=1)

    if "Name" not in out.columns:
        out["Name"] = "Producto sin nombre"

    if "category_context" not in out.columns:
        out["category_context"] = "Sin categoría"

    return out


def build_category_from_product(product: pd.DataFrame) -> pd.DataFrame:
    if product.empty:
        return pd.DataFrame()

    g = (
        product.groupby("category_context", dropna=False)
        .agg(
            productos=("Name", "count"),
            ventas_brutas=("gross_sales_final", "sum"),
            ventas_netas=("net_sales_final", "sum"),
            unidades=("sold_final", "sum"),
            cogs=("cogs_final", "sum"),
            utilidad_bruta=("gross_profit_final", "sum"),
            reduccion=("gross_to_net_reduction_final", "sum"),
            descuentos=("discount_reduction_final", "sum"),
            refunds=("refund_reduction_final", "sum"),
            productos_negativos=("gross_profit_final", lambda s: pd.to_numeric(s, errors="coerce").lt(0).sum()),
            cogs_cero=("cogs_final", lambda s: pd.to_numeric(s, errors="coerce").fillna(-1).eq(0).sum()),
            cogs_faltante=("cogs_final", lambda s: pd.to_numeric(s, errors="coerce").isna().sum()),
        )
        .reset_index()
    )

    g["margen_bruto_pct"] = g.apply(
        lambda r: (r["utilidad_bruta"] / r["ventas_netas"] * 100) if r["ventas_netas"] else 0,
        axis=1,
    )
    return g.sort_values("ventas_netas", ascending=False)


# ============================================================
# GRÁFICAS
# ============================================================

def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str,
    x_title: str = "",
    y_title: str = "",
    money_labels: bool = True,
    height: int | None = None,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    plot_df = df.copy()
    plot_df = plot_df.sort_values(x, ascending=True)

    values = pd.to_numeric(plot_df[x], errors="coerce").fillna(0)
    max_val = float(values.max()) if len(values) else 0.0
    text = values.apply(lambda v: money(v, 0) if money_labels else number(v, 0))

    fig = go.Figure(
        go.Bar(
            x=values,
            y=plot_df[y].astype(str),
            orientation="h",
            marker=dict(color=color),
            text=text,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=21, color=COLOR_TEXT)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT, size=13),
        height=height or max(440, 34 * len(plot_df) + 130),
        margin=dict(l=20, r=190, t=70, b=40),
        xaxis=dict(
            title=x_title,
            gridcolor="rgba(255,255,255,.10)",
            zerolinecolor="rgba(255,255,255,.25)",
        ),
        yaxis=dict(title=y_title, automargin=True),
        showlegend=False,
    )

    # FIX PRINCIPAL: espacio a la derecha para que no se corten etiquetas.
    if max_val > 0:
        fig.update_xaxes(range=[0, max_val * 1.28])

    return fig


def signed_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: int | None = None,
) -> go.Figure:
    if df.empty:
        return go.Figure()

    plot_df = df.copy().sort_values(x, ascending=True)
    vals = pd.to_numeric(plot_df[x], errors="coerce").fillna(0)
    colors = [COLOR_GREEN if v >= 0 else COLOR_RED for v in vals]
    max_abs = float(vals.abs().max()) if len(vals) else 0

    fig = go.Figure(
        go.Bar(
            x=vals,
            y=plot_df[y].astype(str),
            orientation="h",
            marker=dict(color=colors),
            text=vals.apply(lambda v: money(v, 0)),
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=21, color=COLOR_TEXT)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT, size=13),
        height=height or max(420, 34 * len(plot_df) + 120),
        margin=dict(l=20, r=190, t=70, b=40),
        xaxis=dict(
            title="Utilidad bruta",
            gridcolor="rgba(255,255,255,.10)",
            zeroline=True,
            zerolinecolor="rgba(255,255,255,.35)",
        ),
        yaxis=dict(automargin=True),
        showlegend=False,
    )

    if max_abs > 0:
        fig.update_xaxes(range=[-max_abs * 1.28, max_abs * 1.28])

    return fig


# ============================================================
# SIDEBAR Y FILTROS
# ============================================================

def sidebar(product: pd.DataFrame, category_summary: pd.DataFrame) -> tuple[str, str, int, pd.DataFrame]:
    st.sidebar.markdown("# Navegación")

    section = st.sidebar.selectbox(
        "Sección",
        [
            "Resumen ejecutivo",
            "Categorías y productos",
            "Productos con utilidad negativa",
            "Margen bajo y prevención",
            "Reducciones y pérdida de utilidad",
            "Rentabilidad y COGS",
            "Transacciones y errores",
            "Catálogo y calidad de datos",
            "Cola priorizada",
            "Recomendaciones ejecutivas",
            "Metodología y notas",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("# Filtros")

    ordered_categories = ["Todas las categorías"]
    if not category_summary.empty:
        ordered_categories += category_summary.sort_values("ventas_netas", ascending=False)["category_context"].astype(str).tolist()
    elif "category_context" in product.columns:
        ordered_categories += (
            product.groupby("category_context")["net_sales_final"]
            .sum()
            .sort_values(ascending=False)
            .index.astype(str)
            .tolist()
        )

    category = st.sidebar.selectbox(
        "Categoría — ordenada de mayor a menor venta",
        ordered_categories,
        index=0,
    )

    top_n = st.sidebar.slider(
        "Cantidad de productos en rankings",
        min_value=5,
        max_value=50,
        value=20,
        step=5,
    )

    filtered = product.copy()
    if category != "Todas las categorías":
        filtered = filtered[filtered["category_context"].astype(str).eq(category)]

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Los totales ejecutivos del periodo no cambian con los filtros. "
        "Las tablas y rankings sí responden a la categoría seleccionada."
    )

    return section, category, top_n, filtered


# ============================================================
# SECCIONES
# ============================================================

def section_executive(product: pd.DataFrame, category_summary: pd.DataFrame) -> None:
    st.title("UNIMARKET INTELLIGENCE")
    st.markdown(
        '<div class="subtitle">Financial control · Profitability · Action engine</div>',
        unsafe_allow_html=True,
    )

    note(
        "Este dashboard traduce el reporte agregado por producto en indicadores de decisión. "
        "No declara pérdidas automáticamente cuando falta información; separa pérdida reportada, "
        "exposición por calidad de datos y oportunidades de revisión."
    )

    gross_sales = safe_sum(product, "gross_sales_final")
    net_sales = safe_sum(product, "net_sales_final")
    reduction = safe_sum(product, "gross_to_net_reduction_final")
    discounts = safe_sum(product, "discount_reduction_final")
    refunds = safe_sum(product, "refund_reduction_final")
    gp = safe_sum(product, "gross_profit_final")
    cogs = safe_sum(product, "cogs_final")
    margin = (gp / net_sales * 100) if net_sales else 0

    negative_df = product[pd.to_numeric(product.get("gross_profit_final", 0), errors="coerce") < 0]
    negative_abs = abs(safe_sum(negative_df, "gross_profit_final"))

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Ventas brutas totales", money(gross_sales, 2), "Valor antes de descuentos y refunds.", "kpi-blue")
    with c2:
        kpi_card("Ventas netas totales", money(net_sales, 2), "Ingreso final reportado.", "kpi-green")
    with c3:
        kpi_card("Reducción bruta a neta", money(reduction, 2), "Descuentos + refunds − repayments.", "kpi-orange")

    c4, c5, c6 = st.columns(3)
    with c4:
        kpi_card("COGS reportado", money(cogs, 2), "Costo registrado de productos vendidos.")
    with c5:
        kpi_card("Utilidad bruta reportada", money(gp, 2), "Ventas netas menos COGS.", "kpi-green" if gp >= 0 else "kpi-red")
    with c6:
        kpi_card("Margen bruto reportado", pct(margin, 2), "Utilidad bruta / ventas netas.", "kpi-green")

    c7, c8, c9 = st.columns(3)
    with c7:
        kpi_card("Descuentos", money(discounts, 2), "Reducciones comerciales aplicadas.", "kpi-orange")
    with c8:
        kpi_card("Refunds", money(refunds, 2), "Devoluciones o reversos registrados.", "kpi-orange")
    with c9:
        kpi_card("Utilidad negativa", money(negative_abs, 2), f"{len(negative_df):,.0f} productos con utilidad negativa.", "kpi-red")

    st.markdown("## Lectura ejecutiva")
    note(
        f"El negocio reporta <b>{money(net_sales,2)}</b> en ventas netas y <b>{money(gp,2)}</b> de utilidad bruta. "
        f"La reducción entre ventas brutas y netas fue de <b>{money(reduction,2)}</b>. "
        f"Hay <b>{len(negative_df)}</b> productos con utilidad negativa reportada por <b>{money(negative_abs,2)}</b>. "
        "El análisis recomienda revisar primero productos con utilidad negativa, COGS cero o faltante, "
        "márgenes bajos y reducciones fuertes de ingreso.",
        warning=False,
    )

    if not category_summary.empty:
        st.markdown("## Categorías más y menos rentables")
        st.markdown(
            '<div class="small-muted">Las barras verdes muestran dónde se concentra la mayor utilidad bruta. '
            'Las barras naranjas muestran las categorías con menor utilidad positiva. '
            'Las etiquetas se muestran completas para evitar cortes visuales.</div>',
            unsafe_allow_html=True,
        )

        positive_cat = category_summary[
            pd.to_numeric(category_summary["utilidad_bruta"], errors="coerce") > 0
        ].copy()

        col_a, col_b = st.columns(2)

        top_profitable = positive_cat.sort_values("utilidad_bruta", ascending=False).head(15)
        less_profitable = positive_cat.sort_values("utilidad_bruta", ascending=True).head(15)

        with col_a:
            fig = bar_chart(
                top_profitable,
                x="utilidad_bruta",
                y="category_context",
                title="Categorías más rentables",
                color=COLOR_GREEN,
                x_title="Utilidad bruta",
                money_labels=True,
                height=650,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            fig = bar_chart(
                less_profitable,
                x="utilidad_bruta",
                y="category_context",
                title="Categorías menos rentables",
                color=COLOR_ORANGE,
                x_title="Utilidad bruta",
                money_labels=True,
                height=650,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("## Categorías por ventas netas")
        fig = bar_chart(
            category_summary.sort_values("ventas_netas", ascending=False).head(25),
            x="ventas_netas",
            y="category_context",
            title="Ventas netas por categoría",
            color=COLOR_BLUE,
            x_title="Ventas netas",
            money_labels=True,
        )
        st.plotly_chart(fig, use_container_width=True)


def section_categories(filtered: pd.DataFrame, product: pd.DataFrame, category: str, top_n: int) -> None:
    st.title("Categorías y productos")

    note(
        "Primero se revisa la categoría de mayor a menor venta. Después, dentro de cada categoría, "
        "se comparan productos más vendidos, menos vendidos, mayor utilidad, menor utilidad y margen bajo."
    )

    data = filtered.copy()

    gross = safe_sum(data, "gross_sales_final")
    net = safe_sum(data, "net_sales_final")
    gp = safe_sum(data, "gross_profit_final")
    margin = (gp / net * 100) if net else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Ventas netas", money(net, 2), "Ventas de la selección.", "kpi-green")
    with c2:
        kpi_card("Utilidad bruta", money(gp, 2), "Ganancia antes de gastos operativos.", "kpi-green" if gp >= 0 else "kpi-red")
    with c3:
        kpi_card("Margen bruto", pct(margin, 2), "Utilidad / ventas netas.")
    with c4:
        kpi_card("Productos", number(len(data)), "Productos en la selección.")

    tabs = st.tabs(
        [
            "Más vendidos",
            "Menos vendidos",
            "Mayor utilidad",
            "Menor utilidad / pérdida",
            "Margen más bajo",
        ]
    )

    with tabs[0]:
        top = data.sort_values("net_sales_final", ascending=False).head(top_n)
        fig = bar_chart(top, "net_sales_final", "Name", f"Top {top_n} productos más vendidos", COLOR_GREEN)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(format_table(top), use_container_width=True, hide_index=True)

    with tabs[1]:
        low = data[pd.to_numeric(data["net_sales_final"], errors="coerce") > 0].sort_values("net_sales_final").head(top_n)
        fig = bar_chart(low, "net_sales_final", "Name", f"Top {top_n} productos menos vendidos", COLOR_ORANGE)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(format_table(low), use_container_width=True, hide_index=True)

    with tabs[2]:
        profit = data.sort_values("gross_profit_final", ascending=False).head(top_n)
        fig = signed_bar_chart(profit, "gross_profit_final", "Name", f"Top {top_n} productos con mayor utilidad")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(format_table(profit), use_container_width=True, hide_index=True)

    with tabs[3]:
        loss = data.sort_values("gross_profit_final", ascending=True).head(top_n)
        fig = signed_bar_chart(loss, "gross_profit_final", "Name", f"Top {top_n} productos con menor utilidad o pérdida")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(format_table(loss), use_container_width=True, hide_index=True)

    with tabs[4]:
        margin_col = "gross_margin_pct_final"
        margin_df = data[
            pd.to_numeric(data.get("net_sales_final", 0), errors="coerce") > 0
        ].copy()
        margin_df = margin_df[pd.to_numeric(margin_df.get(margin_col, None), errors="coerce").notna()]
        margin_df = margin_df.sort_values(margin_col, ascending=True).head(top_n)

        fig = bar_chart(
            margin_df,
            x=margin_col,
            y="Name",
            title=f"Top {top_n} productos con margen más bajo",
            color=COLOR_RED,
            x_title="Margen bruto %",
            money_labels=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(format_table(margin_df), use_container_width=True, hide_index=True)


def section_negative(product: pd.DataFrame, top_n: int) -> None:
    st.title("Productos con utilidad negativa")

    note(
        "Aquí se listan productos donde la utilidad bruta reportada es menor que cero. "
        "En palabras simples: después de considerar ventas netas y costo registrado, el producto aparece perdiendo dinero."
    )

    data = product[pd.to_numeric(product.get("gross_profit_final", 0), errors="coerce") < 0].copy()
    data["perdida_abs"] = data["gross_profit_final"].abs()
    data = data.sort_values("perdida_abs", ascending=False)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Productos negativos", number(len(data)), "Cantidad de productos con utilidad negativa.", "kpi-red")
    with c2:
        kpi_card("Pérdida reportada", money(safe_sum(data, "perdida_abs"), 2), "Suma absoluta de utilidad negativa.", "kpi-red")
    with c3:
        kpi_card("Mayor pérdida individual", money(data["perdida_abs"].max() if not data.empty else 0, 2), "Producto más crítico.", "kpi-red")

    if data.empty:
        st.info("No hay productos con utilidad negativa para los filtros actuales.")
        return

    fig = bar_chart(
        data.head(top_n),
        x="perdida_abs",
        y="Name",
        title=f"Top {top_n} productos con mayor pérdida reportada",
        color=COLOR_RED,
        x_title="Pérdida absoluta",
        money_labels=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(format_table(data.head(top_n)), use_container_width=True, hide_index=True)


def section_low_margin(product: pd.DataFrame, top_n: int) -> None:
    st.title("Margen bajo y prevención")

    note(
        "Un producto puede no estar perdiendo dinero, pero tener un margen tan bajo que deja muy poco espacio "
        "para cubrir renta, nómina, desperdicio, comisiones o errores de precio."
    )

    data = product.copy()
    margin = pd.to_numeric(data.get("gross_margin_pct_final", None), errors="coerce")
    net = pd.to_numeric(data.get("net_sales_final", 0), errors="coerce")
    gp = pd.to_numeric(data.get("gross_profit_final", 0), errors="coerce")

    low = data[(net > 0) & (gp >= 0) & (margin.notna()) & (margin < 23)].copy()
    low = low.sort_values(["gross_margin_pct_final", "net_sales_final"], ascending=[True, False])

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Productos de margen bajo", number(len(low)), "Margen positivo pero riesgoso.", "kpi-orange")
    with c2:
        kpi_card("Ventas asociadas", money(safe_sum(low, "net_sales_final"), 2), "Ventas en productos con margen bajo.", "kpi-orange")
    with c3:
        kpi_card("Margen mínimo", pct(low["gross_margin_pct_final"].min() if not low.empty else 0), "Menor margen encontrado.", "kpi-orange")

    if low.empty:
        st.info("No hay productos de margen bajo con los filtros actuales.")
        return

    fig = bar_chart(
        low.head(top_n),
        x="gross_margin_pct_final",
        y="Name",
        title=f"Top {top_n} productos con margen más bajo",
        color=COLOR_ORANGE,
        x_title="Margen bruto %",
        money_labels=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(format_table(low.head(top_n)), use_container_width=True, hide_index=True)


def section_reductions(product: pd.DataFrame, top_n: int) -> None:
    st.title("Reducciones y pérdida de utilidad")

    note(
        "Esta sección muestra productos donde las ventas brutas se reducen por descuentos, refunds o ajustes. "
        "No todo descuento es malo, pero descuentos altos pueden convertir un producto rentable en uno de bajo margen o pérdida."
    )

    data = product.copy()
    data["reduction_abs"] = pd.to_numeric(data.get("gross_to_net_reduction_final", 0), errors="coerce").fillna(0)
    data = data[data["reduction_abs"] > 0].sort_values("reduction_abs", ascending=False)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Reducción total", money(safe_sum(data, "reduction_abs"), 2), "Gross Sales - Net Sales.", "kpi-orange")
    with c2:
        kpi_card("Descuentos", money(safe_sum(product, "discount_reduction_final"), 2), "Descuentos aplicados.", "kpi-orange")
    with c3:
        kpi_card("Refunds", money(safe_sum(product, "refund_reduction_final"), 2), "Devoluciones registradas.", "kpi-orange")

    if data.empty:
        st.info("No hay reducciones para mostrar.")
        return

    fig = bar_chart(
        data.head(top_n),
        x="reduction_abs",
        y="Name",
        title=f"Top {top_n} productos con mayor reducción bruta a neta",
        color=COLOR_ORANGE,
        x_title="Reducción bruta a neta",
        money_labels=True,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(format_table(data.head(top_n)), use_container_width=True, hide_index=True)


def section_cogs(product: pd.DataFrame, top_n: int) -> None:
    st.title("Rentabilidad y COGS")

    note(
        "COGS es el costo del producto vendido. Si un producto aparece con COGS cero o sin COGS, "
        "la utilidad puede verse mejor de lo real. Esta sección habla de riesgo de calidad de datos, "
        "no de pérdida confirmada."
    )

    cogs = pd.to_numeric(product.get("cogs_final", None), errors="coerce")
    net = pd.to_numeric(product.get("net_sales_final", 0), errors="coerce")

    zero = product[(net > 0) & (cogs == 0)].copy()
    missing = product[(net > 0) & (cogs.isna())].copy()

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Ventas con COGS cero", money(safe_sum(zero, "net_sales_final"), 2), f"{len(zero)} productos.", "kpi-orange")
    with c2:
        kpi_card("Ventas sin COGS", money(safe_sum(missing, "net_sales_final"), 2), f"{len(missing)} productos.", "kpi-orange")
    with c3:
        gp = safe_sum(product, "gross_profit_final")
        net_total = safe_sum(product, "net_sales_final")
        margin = (gp / net_total * 100) if net_total else 0
        kpi_card("Margen reportado", pct(margin, 2), "Margen con datos disponibles.", "kpi-green")

    tabs = st.tabs(["COGS cero", "COGS faltante"])
    with tabs[0]:
        if zero.empty:
            st.info("No hay productos con COGS cero en la selección.")
        else:
            zero = zero.sort_values("net_sales_final", ascending=False).head(top_n)
            fig = bar_chart(zero, "net_sales_final", "Name", f"Top {top_n} ventas con COGS cero", COLOR_ORANGE)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(format_table(zero), use_container_width=True, hide_index=True)

    with tabs[1]:
        if missing.empty:
            st.info("No hay productos con COGS faltante en la selección.")
        else:
            missing = missing.sort_values("net_sales_final", ascending=False).head(top_n)
            fig = bar_chart(missing, "net_sales_final", "Name", f"Top {top_n} ventas sin COGS", COLOR_ORANGE)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(format_table(missing), use_container_width=True, hide_index=True)


def section_transactions(product: pd.DataFrame) -> None:
    st.title("Transacciones y errores")

    note(
        "Las transacciones manuales negativas deben revisarse contra recibos, devoluciones, ajustes y autorización. "
        "No se declaran automáticamente como pérdida porque el dataset está agregado por producto."
    )

    name = product.get("Name", pd.Series(dtype=str)).astype(str).str.lower()
    net = pd.to_numeric(product.get("net_sales_final", 0), errors="coerce").fillna(0)

    manual = product[name.str.contains("manual transaction", na=False) | ((net < 0) & (product.get("category_context", "").astype(str).str.lower() == "uncategorized"))].copy()

    c1, c2 = st.columns(2)
    with c1:
        kpi_card("Transacciones manuales", number(len(manual)), "Registros manuales encontrados.")
    with c2:
        kpi_card("Saldo neto manual", money(safe_sum(manual, "net_sales_final"), 2), "Suma neta de transacciones manuales.", "kpi-red")

    if manual.empty:
        st.info("No hay transacciones manuales negativas con los filtros actuales.")
    else:
        st.dataframe(format_table(manual.sort_values("net_sales_final")), use_container_width=True, hide_index=True)


def section_catalog(product: pd.DataFrame, top_n: int) -> None:
    st.title("Catálogo y calidad de datos")

    note(
        "Identifica productos posiblemente duplicados, mal etiquetados, con presentación confusa o que requieren revisión de SKU/UPC. "
        "No significa pérdida directa, pero puede causar errores de precio, costo, inventario o análisis."
    )

    reason_col = first_existing(product, ["catalog_review_reason_corrected", "catalog_review_reason", "catalog_finding_class"])
    if reason_col is None:
        st.info("No hay columna de razón de catálogo disponible.")
        return

    reason = product[reason_col].astype(str)
    catalog = product[
        reason.notna()
        & ~reason.str.lower().isin(["", "none", "nan", "no_catalog_finding"])
    ].copy()

    c1, c2 = st.columns(2)
    with c1:
        kpi_card("Registros de catálogo a revisar", number(len(catalog)), "Productos con posible problema de catálogo.", "kpi-orange")
    with c2:
        kpi_card("Ventas asociadas", money(safe_sum(catalog, "net_sales_final"), 2), "Ventas relacionadas con estos registros.", "kpi-orange")

    if catalog.empty:
        st.info("No hay hallazgos de catálogo en la selección.")
        return

    catalog = catalog.sort_values("net_sales_final", ascending=False).head(top_n)
    st.dataframe(format_table(catalog), use_container_width=True, hide_index=True)


def section_queue(product: pd.DataFrame, top_n: int) -> None:
    st.title("Cola priorizada")

    note(
        "Esta cola ordena productos para revisar primero. La prioridad combina impacto financiero, pérdida, margen bajo, "
        "reducciones, calidad de costos y catálogo."
    )

    priority_order = {"Crítica": 0, "Alta": 1, "Media": 2, "Baja": 3, "Sin prioridad": 4}
    data = product.copy()
    data["priority_rank"] = data["priority_readable"].map(priority_order).fillna(9)
    data["impact"] = (
        pd.to_numeric(data.get("gross_profit_final", 0), errors="coerce").fillna(0).abs()
        + pd.to_numeric(data.get("gross_to_net_reduction_final", 0), errors="coerce").fillna(0).abs()
        + pd.to_numeric(data.get("net_sales_final", 0), errors="coerce").fillna(0) * 0.01
    )

    data = data.sort_values(["priority_rank", "impact"], ascending=[True, False]).head(top_n)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Productos en cola", number(len(data)), "Productos visibles según filtros.")
    with c2:
        kpi_card("Críticos / altos", number(data["priority_readable"].isin(["Crítica", "Alta"]).sum()), "Máxima prioridad.")
    with c3:
        kpi_card("Ventas asociadas", money(safe_sum(data, "net_sales_final"), 2), "Ventas de la cola visible.")

    st.dataframe(format_table(data), use_container_width=True, hide_index=True)


def section_recommendations() -> None:
    st.title("Recomendaciones ejecutivas")

    st.markdown(
        """
        ### 1. Revisar productos con utilidad negativa
        Confirmar precio de venta, costo unitario, descuentos aplicados y refunds. Estos productos son la primera prioridad porque ya aparecen con pérdida reportada.

        ### 2. Corregir COGS cero o faltante
        Un producto sin costo puede inflar artificialmente la utilidad. Antes de tomar decisiones de precios, el catálogo debe tener costos confiables.

        ### 3. Controlar descuentos y refunds
        Separar descuentos comerciales normales de descuentos que destruyen margen. Revisar productos donde la reducción bruta a neta es alta.

        ### 4. Depurar catálogo
        Revisar duplicados, packs, unidades, tamaños y SKU/UPC. Un catálogo confuso puede generar errores de precio, inventario y rentabilidad.

        ### 5. Solicitar data transaccional completa
        Para una auditoría precisa se necesita información por fecha, ticket, empleado, canal de venta, método de pago, descuentos autorizados, refunds, inventario y costo histórico.
        """
    )


def section_methodology() -> None:
    st.title("Metodología y notas")

    st.markdown(
        """
        ## Definiciones simples

        **Gross Sales / Ventas brutas:** valor vendido antes de descuentos, devoluciones o ajustes.

        **Net Sales / Ventas netas:** valor final después de descuentos, refunds y repayments.

        **COGS:** costo del producto vendido. Es lo que le cuesta al negocio vender ese producto.

        **Gross Profit / Utilidad bruta:** ventas netas menos COGS.

        **Gross Margin / Margen bruto:** porcentaje de utilidad que queda después del costo.

        **Reducción bruta a neta:** diferencia entre Gross Sales y Net Sales. Incluye descuentos, refunds y repayments.

        **COGS cero:** producto vendido que aparece con costo igual a cero. Puede inflar la utilidad.

        **Rentabilidad incompleta:** producto sin costo o utilidad completa. No permite saber con precisión si gana o pierde.

        **Anomalía de configuración:** inconsistencia entre costo, utilidad y margen reportado.

        ## Nota importante

        El dataset es un reporte agregado por producto. Por eso no permite atribuir pérdidas a fechas, empleados, turnos o transacciones específicas sin tener la data transaccional completa.

        ## Qué datos faltan para una auditoría precisa

        Fecha y hora de cada venta, ticket, empleado, canal, descuentos autorizados, refunds, método de pago, costo histórico, inventario inicial/final, compras, merma y cambios de precio.
        """
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    inject_css()

    st.sidebar.markdown("## Configuración")
    root_input = st.sidebar.text_input("Ruta raíz del proyecto", value=str(DEFAULT_ROOT))
    root = Path(root_input)

    data = load_data(root)
    product = normalize_product(data["product"])

    if product.empty:
        st.error(
            "No se encontró el product mart del dashboard. Verifica que exista: "
            "data/dashboard/unimarket_dashboard_product_mart.csv"
        )
        st.stop()

    category_summary = build_category_from_product(product)

    section, category, top_n, filtered = sidebar(product, category_summary)

    if section == "Resumen ejecutivo":
        section_executive(product, category_summary)
    elif section == "Categorías y productos":
        section_categories(filtered, product, category, top_n)
    elif section == "Productos con utilidad negativa":
        section_negative(filtered, top_n)
    elif section == "Margen bajo y prevención":
        section_low_margin(filtered, top_n)
    elif section == "Reducciones y pérdida de utilidad":
        section_reductions(filtered, top_n)
    elif section == "Rentabilidad y COGS":
        section_cogs(filtered, top_n)
    elif section == "Transacciones y errores":
        section_transactions(filtered)
    elif section == "Catálogo y calidad de datos":
        section_catalog(filtered, top_n)
    elif section == "Cola priorizada":
        section_queue(filtered, top_n)
    elif section == "Recomendaciones ejecutivas":
        section_recommendations()
    elif section == "Metodología y notas":
        section_methodology()

    st.caption(f"UNIMARKET LATIN FOOD · {APP_VERSION}")


if __name__ == "__main__":
    main()
