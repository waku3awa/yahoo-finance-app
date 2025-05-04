from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import pandas as pd
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta
import os

from models import init_db
from stock_utils import get_or_update_stock_data

# データベースの初期化
init_db()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html')

@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    """株価データを取得するAPI"""
    symbol = request.args.get('symbol', '7203.T')  # デフォルトはトヨタ自動車
    interval = request.args.get('interval', '1mo')  # デフォルトは月足
    period = request.args.get('period', '1y')  # デフォルトは1年
    
    # 日本の銘柄の場合、銘柄コードに .T を追加
    if not symbol.endswith('.T') and symbol.isdigit():
        symbol = f"{symbol}.T"
    
    # データを取得または更新
    df = get_or_update_stock_data(symbol, interval, period)
    
    if df is None or df.empty:
        return jsonify({'error': 'データを取得できませんでした。銘柄コードを確認してください。'}), 404
    
    # DataFrameをJSONに変換
    df = df.reset_index()
    df_json = df.to_json(orient='records', date_format='iso')
    
    return df_json

@app.route('/api/plot', methods=['GET'])
def plot_stock_data():
    """株価データをプロットするAPI"""
    symbol = request.args.get('symbol', '7203.T')  # デフォルトはトヨタ自動車
    interval = request.args.get('interval', '1mo')  # デフォルトは月足
    period = request.args.get('period', '1y')  # デフォルトは1年
    
    # 日本の銘柄の場合、銘柄コードに .T を追加
    if not symbol.endswith('.T') and symbol.isdigit():
        symbol = f"{symbol}.T"
    
    # データを取得または更新
    df = get_or_update_stock_data(symbol, interval, period)
    
    if df is None or df.empty:
        return jsonify({'error': 'データを取得できませんでした。銘柄コードを確認してください。'}), 404
    
    # ローソク足チャートを作成
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='ローソク足'
    )])
    
    # 出来高を追加
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='出来高',
        yaxis='y2'
    ))
    
    # レイアウトを設定
    fig.update_layout(
        title=f'{symbol} - {interval} - {period}',
        yaxis_title='価格',
        xaxis_title='日付',
        yaxis2=dict(
            title='出来高',
            overlaying='y',
            side='right'
        ),
        xaxis_rangeslider_visible=False
    )
    
    # JSONに変換
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON

@app.route('/api/intervals', methods=['GET'])
def get_intervals():
    """利用可能な間隔を取得するAPI"""
    intervals = [
        {'value': '1d', 'label': '日足'},
        {'value': '1wk', 'label': '週足'},
        {'value': '1mo', 'label': '月足'}
    ]
    
    return jsonify(intervals)

@app.route('/api/periods', methods=['GET'])
def get_periods():
    """利用可能な期間を取得するAPI"""
    periods = [
        {'value': '1mo', 'label': '1ヶ月'},
        {'value': '3mo', 'label': '3ヶ月'},
        {'value': '6mo', 'label': '6ヶ月'},
        {'value': '1y', 'label': '1年'},
        {'value': '2y', 'label': '2年'},
        {'value': '5y', 'label': '5年'},
        {'value': '10y', 'label': '10年'},
        {'value': 'max', 'label': '全期間'}
    ]
    
    return jsonify(periods)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 51953))
    app.run(host='0.0.0.0', port=port, debug=True)