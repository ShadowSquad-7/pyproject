import panel as pn
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta
from pathlib import Path

def get_currency_dashboard():
    pn.extension("plotly")

    # ─── КОНФИГ ─────────────────────────────────────────────
    BASE_DIR = Path(__file__).resolve().parents[2] / "data"

    COLOR_SCHEMES = {
        "standart": {"up": "#2ECC71", "down": "#E74C3C"},
        "daltonic": {"up": "#3498DB", "down": "#F39C12"},
        "contrast": {"up":"#000000", "down": "#FFFFFF"}
    }

    INTERVAL_CONFIG = {
        "1 day":   timedelta(days=1),
        "1 week": timedelta(weeks=1),
        "1 month":  timedelta(days=30),
        "1 year":    timedelta(days=365)
    }

    CURRENCY_FILES = {
        "CNY": "CNY_RUB.csv",
        "EUR": "EUR_RUB.csv",
        "USD": "USD_RUB.csv",
        "BTC": "BTC_USD.csv"
    }

    # Кэш последнего времени изменения csv
    _LAST_MTIME = {}

    # ─── УТИЛИТЫ ───────────────────────────────────────────

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


    # ─── ВИДЖЕТЫ ───────────────────────────────────────────
    currency = pn.widgets.Select(
        name="currency", options=list(CURRENCY_FILES.keys()), value="USD"
    )
    period = pn.widgets.Select(
        name="period", options=list(INTERVAL_CONFIG.keys()), value="1 week"
    )
    scheme = pn.widgets.Select(
        name="color", options=list(COLOR_SCHEMES.keys()), value="standart"
    )


    # ─── ИНИЦИАЛЬНОЕ СОЗДАНИЕ ГРАФИКА ─────────────────────────

    def create_initial_fig():
        df = load_data(currency.value)
        if df.empty:
            fig = go.Figure()
            fig.update_layout(title="Нет данных", template="plotly_dark")
            return fig
        df = df[df.index >= df.index.max() - INTERVAL_CONFIG[period.value]]
        title = f"{currency.value} ➜ {'USD' if currency.value=='BTC' else 'RUB'}  ({period.value})"
        return make_plot(df, title, COLOR_SCHEMES[scheme.value])


    # Создаем панель с первоначальным объектом графика
    plotly_pane = pn.pane.Plotly(create_initial_fig(), height=500)


    # ─── ФУНКЦИЯ ОБНОВЛЕНИЯ ──────────────────────────

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


    def update_plot(event=None):
        """Обновление графика при изменении виджетов."""
        try:
            df = load_data(currency.value)
        except Exception as err:
            plotly_pane.object = go.Figure(layout=dict(title=f"Ошибка чтения: {err}", template="plotly_dark"))
            return

        if df.empty:
            plotly_pane.object = go.Figure(layout=dict(title="Нет данных", template="plotly_dark"))
            return

        df = _apply_interval_filter(df)
        title = f"{currency.value} ➜ {'USD' if currency.value=='BTC' else 'RUB'}  ({period.value})"

        fig = make_plot(df, title, COLOR_SCHEMES[scheme.value])
        plotly_pane.object = fig


    # ─── ОБРАБОЧИКИ ─────────────────────────────────────
    # Привязываем обработчики к виджетам
    currency.param.watch(update_plot, 'value')
    period.param.watch(update_plot, 'value')
    scheme.param.watch(update_plot, 'value')


    # ─── СБОРКА ДАШБОРДА ─────────────────────────────────
    dashboard = pn.Column(
        pn.Row(currency, period, scheme),
        plotly_pane,
    )


    dashboard.servable()
    return dashboard
