# Импорт необходимых библиотий
import pandas as pd  # для работы с таблицами
import dash  # фреймворк для веб-приложений
from dash import dcc, html  # компоненты Dash: графики, элементы управления
from dash.dependencies import Input, Output  # для связывания ввода/вывода компонентов
import plotly.graph_objs as go  # для создания интерактивных графиков
import yfinance as yf  # библиотека для загрузки финансовых данных
import os  # для работы с файловой системой

# Имя CSV-файла, в который сохраняется история цен BTC
csv_file = 'BTC_USD.csv'

# Если файл уже существует — загружаем его
if os.path.exists(csv_file):
    # Чтение CSV без заголовков (header=None), пропуск первых 3 строк
    raw = pd.read_csv(csv_file, header=None, skiprows=3,
                      names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])

    # Вывод первых строк и названий столбцов в консоль для отладки
    print("Структура DataFrame после чтения CSV-файла:")
    print(raw.head())
    print(raw.columns)

    # Преобразуем колонку Date в формат datetime
    raw['Date'] = pd.to_datetime(raw['Date'])
    # Устанавливаем Date как индекс таблицы
    raw = raw.set_index('Date')

    # Сохраняем данные в переменную history
    history = raw.copy()
else:
    # Если файла нет — скачиваем данные по BTC-USD за 1 год с интервалом 1 день
    history = yf.download('BTC-USD', period='1y', interval='1d')
    history.index.name = 'Date'
    # Сохраняем в файл
    history.to_csv(csv_file)

# Создание Dash-приложения
app = dash.Dash(__name__)

# Определение структуры (layout) страницы
app.layout = html.Div([
    html.Div([  # Верхняя панель с кнопками фильтрации
        dcc.RadioItems(  # Радиокнопки для выбора временного интервала
            id='time-range',
            options=[
                {'label': 'Week', 'value': '7D'},
                {'label': 'Month', 'value': '30D'},
                {'label': '6 months', 'value': '180D'},
                {'label': 'All', 'value': 'ALL'}
            ],
            value='ALL',
            className='dash-radio-items'  # Кастомный CSS-класс
        ),
        dcc.Checklist(  # Чекбоксы для отображения дополнительных линий
            id='indicators',
            options=[
                {'label': 'MA', 'value': 'MA'},         # Скользящая средняя
                {'label': 'Mediana', 'value': 'MED'}    # Медиана
            ],
            value=['MA', 'MED'],  # По умолчанию обе включены
            className='custom-ma-med'  # Кастомный CSS-класс
        ),
    ], style={'margin': '10px'}),

    # График японских свечей (основной график)
    dcc.Graph(id='candlestick-chart',
              config={'displayModeBar': False, 'displaylogo': False}),  # убираем лишние кнопки

    # Интервал обновления графика (каждые 10 секунд)
    dcc.Interval(id='interval-component', interval=10 * 1000, n_intervals=0)
])

# Обработка обратного вызова (callback) для обновления графика
@app.callback(
    Output('candlestick-chart', 'figure'),  # что обновляем
    [Input('time-range', 'value'),          # откуда получаем входные данные
     Input('indicators', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(selected_range, selected_indicators, n):
    # Считываем CSV каждый раз при обновлении
    df = pd.read_csv(csv_file, header=None, skiprows=3,
                     names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'])

    # Преобразование дат
    df['Date'] = pd.to_datetime(df['Date'])
    # Оставляем только нужные столбцы
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    # Убираем строки с пропущенными значениями
    df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])

    # Добавляем колонку скользящей средней (по 10 последним точкам)
    df['MA'] = df['Close'].rolling(window=10).mean()
    # Добавляем медиану по тем же окнам
    df['Median'] = df['Close'].rolling(window=10).median()

    # Фильтрация по выбранному временному диапазону
    if selected_range != 'ALL':
        days = int(selected_range.rstrip('D'))  # Преобразуем, например, '7D' → 7
        cutoff = df['Date'].max() - pd.Timedelta(days=days)
        df = df[df['Date'] >= cutoff]

    # Построение графика свечей
    fig = go.Figure(data=[
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlestick'
        )
    ])

    # Добавление линий индикаторов по выбору пользователя
    if 'MA' in selected_indicators:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MA'],
            mode='lines', name='MA',
            line=dict(color='orange')
        ))
    if 'MED' in selected_indicators:
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Median'],
            mode='lines', name='Median',
            line=dict(color='purple')
        ))

    # Настройка внешнего вида графика
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        paper_bgcolor='#001f3f',     # Цвет фона страницы
        plot_bgcolor='#001f3f',      # Цвет фона графика
        font=dict(color='white', family='Good Times'),  # Цвет и шрифт текста
        xaxis=dict(color='white', gridcolor='#003366'),  # Цвет оси X
        yaxis=dict(color='white', gridcolor='#003366'),  # Цвет оси Y
        xaxis_rangeslider_visible=True,  # Отображение ползунка внизу
        margin=dict(l=40, r=20, t=20, b=40),  # Отступы
    )

    return fig  # Возвращаем фигуру, которая будет отображаться в dcc.Graph

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
