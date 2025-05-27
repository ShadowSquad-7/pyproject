import panel as pn
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
from pathlib import Path
import os

pn.extension("plotly")

pn.config.raw_css = ["""
.dashboard-container {
  top: 20px;
  max-width: 1200px;
  margin: auto;
}

.bk-input {
  background-color: #003366 !important;
  padding: 6px 12px;
  border-radius: 5px !important;
  margin: 10px;
  color: white !important;
  border: 1px solid #555 !important;
}
"""]




# Конфиг
BASE_DIR = Path(__file__).resolve().parents[1] / "data"

COLOR_SCHEMES = {
    "Стандартная": {"up": "#2ECC71", "down": "#E74C3C"},
    "Для дальтоников": {"up": "#3498DB", "down": "#F39C12"},
    "Высокая контрастность": {"up": "#000000", "down": "#FFFFFF"}
}

INTERVAL_CONFIG = {
    "1 день":   timedelta(days=1),
    "1 неделя": timedelta(weeks=1),
    "1 месяц":  timedelta(days=30),
    "1 год":    timedelta(days=365)
}

CURRENCY_FILES = {
    "CNY": "CNY_RUB.csv",
    "EUR": "EUR_RUB.csv",
    "USD": "USD_RUB.csv",
    "BTC": "BTC_USD.csv"
}

# Кэш последнего времени изменения csv
_LAST_MTIME = {}



def load_data(cur: str) -> pd.DataFrame:
    file = BASE_DIR / CURRENCY_FILES[cur]
    if not file.exists():
        return pd.DataFrame()

    df = pd.read_csv(file)

    # выбираем колонку с датой
    if "Date" in df.columns:
        date_col = "Date"
    elif "Price" in df.columns:
        df.rename(columns={"Price": "Date"}, inplace=True)
        date_col = "Date"
    else:
        raise ValueError("Нет колонки Date/Price")

    # фильтруем и приводим к datetime
    df = df[df[date_col].astype(str).str.match(r"\d{4}-\d{2}-\d{2}")]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df.set_index(date_col, inplace=True)
    df.sort_index(inplace=True)

    # приводим цены к числу
    for col in ["Open", "High", "Low", "Close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["Open", "High", "Low", "Close"])


def make_plot(df: pd.DataFrame, title: str, colors: dict):
    fig = go.Figure([go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        increasing_line_color=colors["up"],
        decreasing_line_color=colors["down"]
    )])
    fig.update_layout(
        title=title,
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )
    return fig


# Чтение параметров из URL
def get_url_params():
    try:
        args = pn.state.session_args 
        return {k: v[0].decode() for k, v in args.items()}
    except Exception:
        return {}

params = get_url_params()
default_currency = params.get("currency", "USD")



# Виджеты
selected_currency = pn.widgets.StaticText(name="Валюта", value=default_currency if default_currency in CURRENCY_FILES else "USD")



period = pn.widgets.Select(
     options=list(INTERVAL_CONFIG.keys()), value="1 неделя"
)
scheme = pn.widgets.Select(
     options=list(COLOR_SCHEMES.keys()), value="Стандартная"
)


# Создание графика

def create_initial_fig():
    df = load_data(selected_currency.value)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Нет данных", template="plotly_dark")
        return fig
    df = df[df.index >= df.index.max() - INTERVAL_CONFIG[period.value]]
    title = f"{selected_currency.value} ➜ {'USD' if selected_currency.value=='BTC' else 'RUB'}  ({period.value})"
    return make_plot(df, title, COLOR_SCHEMES[scheme.value])


# Создаем панель с первоначальным объектом графика
plotly_pane = pn.pane.Plotly(create_initial_fig(), height=500, sizing_mode="fixed", width=1200)


#Обновление

def _file_modified(path: Path) -> bool:
    """Возвращает True, если файл изменился со времени последнего чтения."""
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        return False
    if _LAST_MTIME.get(path) != mtime:
        _LAST_MTIME[path] = mtime
        return True
    return False


def _apply_interval_filter(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df.index >= df.index.max() - INTERVAL_CONFIG[period.value]]


def update_plot(force: bool = False):
    """Обновление графика без перезагрузки страницы."""
    file_path = BASE_DIR / CURRENCY_FILES[selected_currency.value]

    # Выходим, если csv не менялся и нет принудительного обновления
    if not force and not _file_modified(file_path):
        return

    try:
        df = load_data(selected_currency.value)
    except Exception as err:
        plotly_pane.object = go.Figure(layout=dict(title=f"Ошибка чтения: {err}", template="plotly_dark"))
        return

    if df.empty:
        plotly_pane.object = go.Figure(layout=dict(title="Нет данных", template="plotly_dark"))
        return

    df = _apply_interval_filter(df)
    title = f"{selected_currency.value} ➜ {'USD' if selected_currency.value=='BTC' else 'RUB'}  ({period.value})"

    fig = plotly_pane.object
    if fig and fig.data:
        candle = fig.data[0]
        candle.x = df.index
        candle.open = df["Open"]
        candle.high = df["High"]
        candle.low = df["Low"]
        candle.close = df["Close"]
        candle.increasing.line.color = COLOR_SCHEMES[scheme.value]["up"]
        candle.decreasing.line.color = COLOR_SCHEMES[scheme.value]["down"]
        fig.update_layout(title=title)

        plotly_pane.param.trigger("object")
    else:
        plotly_pane.object = make_plot(df, title, COLOR_SCHEMES[scheme.value])



pn.state.curdoc.add_periodic_callback(update_plot, 3_000)


for widget in (period, scheme):
    widget.param.watch(lambda *_: update_plot(force=True), "value")



dashboard = pn.Column(
    pn.Row(period, scheme),
    plotly_pane,
    css_classes=["dashboard-container"]
)


dashboard.servable()
