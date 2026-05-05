import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import cargar_datos, REGION_COORDS


# ──────────────────────────────────────────────────────────────────────────────
#  Formateo
# ──────────────────────────────────────────────────────────────────────────────

def fmt_money(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:.0f}"


# ──────────────────────────────────────────────────────────────────────────────
#  Barra lateral compartida — autenticación + filtros
# ──────────────────────────────────────────────────────────────────────────────

def sidebar_con_filtros() -> pd.DataFrame | None:
    """
    Muestra la barra lateral con info de usuario, logout y filtros.
    Devuelve el DataFrame filtrado, o None si no hay sesión activa.
    """
    # Guard: redirigir si no hay sesión
    if not st.session_state.get("logged_in", False):
        st.warning("Debes iniciar sesión para ver esta página.")
        st.stop()

    with st.sidebar:
        st.title("RetailDash")
        st.write(f"**{st.session_state.nombre}**")
        st.caption(f"Rol: {st.session_state.user_role}")
        st.divider()

        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

        st.divider()
        st.subheader("Filtros")

        df_raw = cargar_datos()

        categorias = ["Todas"] + sorted(df_raw["Category"].unique().tolist())
        cat_sel = st.selectbox("Categoria", categorias, key="cat_sel")

        regiones = ["Todas"] + sorted(df_raw["Region"].unique().tolist())
        reg_sel = st.selectbox("Region", regiones, key="reg_sel")

        años = sorted(df_raw["Year"].unique().tolist())
        año_sel = st.multiselect("Año", años, default=años, key="año_sel")

    # Aplicar filtros
    df = df_raw.copy()
    if cat_sel != "Todas":
        df = df[df["Category"] == cat_sel]
    if reg_sel != "Todas":
        df = df[df["Region"] == reg_sel]
    if año_sel:
        df = df[df["Year"].isin(año_sel)]

    if df.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()

    return df


# ──────────────────────────────────────────────────────────────────────────────
#  KPIs
# ──────────────────────────────────────────────────────────────────────────────

def calcular_kpis(df: pd.DataFrame) -> dict:
    total_ventas  = df["Sales"].sum()
    total_profit  = df["Profit"].sum()
    total_items   = int(df["Quantity"].sum())
    num_registros = len(df)
    margen_prom   = (total_profit / total_ventas * 100) if total_ventas else 0
    ticket_prom   = total_ventas / num_registros if num_registros else 0

    return {
        "ventas":     total_ventas,
        "profit":     total_profit,
        "items":      total_items,
        "registros":  num_registros,
        "margen":     margen_prom,
        "ticket":     ticket_prom,
    }


def mostrar_kpis(df: pd.DataFrame) -> None:
    kpis = calcular_kpis(df)
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Ventas Totales",    fmt_money(kpis["ventas"]))
    k2.metric("Ganancia Total",    fmt_money(kpis["profit"]))
    k3.metric("Unidades Vendidas", f"{kpis['items']:,}")
    k4.metric("Registros",         f"{kpis['registros']:,}")
    k5.metric("Margen Promedio",   f"{kpis['margen']:.1f}%")
    k6.metric("Ticket Promedio",   fmt_money(kpis["ticket"]))


# ──────────────────────────────────────────────────────────────────────────────
#  Gráficas
# ──────────────────────────────────────────────────────────────────────────────

def grafico_ventas_tiempo(df: pd.DataFrame) -> go.Figure:
    ts = df.groupby("Month")["Sales"].sum().reset_index()
    ts["Month_dt"] = pd.to_datetime(ts["Month"])
    ts = ts.sort_values("Month_dt")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["Month_dt"], y=ts["Sales"],
        mode="lines+markers",
        line=dict(color="#FF4B4B", width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(255,75,75,0.10)",
        name="Ventas",
    ))
    fig.update_layout(title="Ventas Mensuales", xaxis_title="", yaxis_title="USD")
    return fig


def grafico_ventas_anuales(df: pd.DataFrame) -> go.Figure:
    anual = df.groupby("Year")["Sales"].sum().reset_index()
    fig = px.bar(
        anual, x="Year", y="Sales",
        title="Ventas por Año",
        text_auto=".2s",
        color="Sales",
        color_continuous_scale="Reds",
    )
    fig.update_layout(coloraxis_showscale=False, xaxis=dict(type="category"))
    return fig


def grafico_categoria_barras(df: pd.DataFrame) -> go.Figure:
    cat = df.groupby("Category")["Sales"].sum().sort_values(ascending=True).reset_index()

    fig = go.Figure(go.Bar(
        x=cat["Sales"], y=cat["Category"],
        orientation="h",
        marker_color="#FF4B4B",
        text=[fmt_money(v) for v in cat["Sales"]],
        textposition="outside",
    ))
    fig.update_layout(title="Ventas por Categoria", xaxis_title="")
    return fig


def grafico_margen_categoria(df: pd.DataFrame) -> go.Figure:
    mg = df.groupby("Category").apply(
        lambda g: (g["Profit"].sum() / g["Sales"].sum() * 100) if g["Sales"].sum() else 0,
        include_groups=False,
    ).reset_index(name="Margen")
    mg = mg.sort_values("Margen", ascending=False)

    fig = go.Figure(go.Bar(
        x=mg["Category"], y=mg["Margen"],
        marker_color=["#FF4B4B" if v == mg["Margen"].max() else "#636EFA" for v in mg["Margen"]],
        text=[f"{v:.1f}%" for v in mg["Margen"]],
        textposition="outside",
    ))
    fig.update_layout(title="Margen de Ganancia por Categoria (%)", yaxis_title="%")
    return fig


def grafico_profit_tiempo(df: pd.DataFrame) -> go.Figure:
    ts = df.groupby("Month")["Profit"].sum().reset_index()
    ts["Month_dt"] = pd.to_datetime(ts["Month"])
    ts = ts.sort_values("Month_dt")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["Month_dt"], y=ts["Profit"],
        mode="lines+markers",
        line=dict(color="#636EFA", width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(99,110,250,0.10)",
        name="Ganancia",
    ))
    fig.update_layout(title="Ganancia Mensual", xaxis_title="", yaxis_title="USD")
    return fig


def grafico_region_pie(df: pd.DataFrame) -> go.Figure:
    reg = df.groupby("Region")["Sales"].sum().reset_index()

    fig = go.Figure(go.Pie(
        labels=reg["Region"], values=reg["Sales"],
        hole=0.45,
    ))
    fig.update_layout(title="Distribucion de Ventas por Region")
    return fig


def grafico_region_barras(df: pd.DataFrame) -> go.Figure:
    reg = df.groupby("Region").agg(
        Ventas=("Sales", "sum"),
        Ganancia=("Profit", "sum"),
    ).reset_index().sort_values("Ventas", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Ventas",   x=reg["Region"], y=reg["Ventas"],   marker_color="#FF4B4B"))
    fig.add_trace(go.Bar(name="Ganancia", x=reg["Region"], y=reg["Ganancia"], marker_color="#636EFA"))
    fig.update_layout(barmode="group", title="Ventas y Ganancia por Region", xaxis_title="")
    return fig


def grafico_scatter_ventas_profit(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df.sample(min(len(df), 600), random_state=1),
        x="Sales", y="Profit",
        color="Category",
        size="Quantity",
        opacity=0.7,
        title="Ventas vs Ganancia (muestra 600 registros)",
        trendline="ols",
    )
    return fig


def grafico_categoria_treemap(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["Category", "Region"]).agg(Sales=("Sales", "sum")).reset_index()
    fig = px.treemap(
        agg, path=["Category", "Region"], values="Sales",
        title="Composicion de Ventas: Categoria → Region",
        color="Sales", color_continuous_scale="Reds",
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig


def grafico_mapa_regiones(df: pd.DataFrame) -> go.Figure:
    reg = df.groupby("Region").agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Registros=("Sales", "count"),
    ).reset_index()

    reg["lat"] = reg["Region"].map(lambda r: REGION_COORDS.get(r, {}).get("lat", 0))
    reg["lon"] = reg["Region"].map(lambda r: REGION_COORDS.get(r, {}).get("lon", 0))
    reg["Sales_fmt"]  = reg["Sales"].apply(fmt_money)
    reg["Profit_fmt"] = reg["Profit"].apply(fmt_money)

    fig = go.Figure(go.Scattergeo(
        lat=reg["lat"],
        lon=reg["lon"],
        text=reg.apply(
            lambda r: f"<b>{r['Region']}</b><br>Ventas: {r['Sales_fmt']}<br>"
                      f"Ganancia: {r['Profit_fmt']}<br>Registros: {r['Registros']}",
            axis=1,
        ),
        hoverinfo="text",
        mode="markers",
        marker=dict(
            size=(reg["Sales"] / reg["Sales"].max() * 45 + 15),
            color=reg["Sales"],
            colorscale="Reds",
            showscale=True,
            colorbar=dict(title="Ventas USD"),
            line=dict(color="#ffffff", width=1),
            opacity=0.85,
        ),
    ))

    fig.update_geos(scope="usa")
    fig.update_layout(title="Mapa de Ventas por Region (EE.UU.)", height=480)
    return fig