import yfinance as yf
import pandas as pd
import datetime
from sqlalchemy.orm import Session
from models import StockData, LastUpdate, Session as DBSession

def get_stock_data(symbol, period='1y', interval='1mo'):
    """
    Yahoo Financeから株価データを取得する
    
    Args:
        symbol (str): 銘柄コード（例: '7203.T'）
        period (str): 取得期間（例: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'）
        interval (str): 間隔（例: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'）
    
    Returns:
        pandas.DataFrame: 株価データ
    """
    try:
        # 日本の銘柄の場合、銘柄コードに .T を追加
        if not symbol.endswith('.T') and symbol.isdigit():
            symbol = f"{symbol}.T"
            
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        # インデックスをリセットして日付列を追加
        df = df.reset_index()
        
        return df, symbol
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, symbol

def save_stock_data(df, symbol, interval, session=None):
    """
    株価データをデータベースに保存する
    
    Args:
        df (pandas.DataFrame): 株価データ
        symbol (str): 銘柄コード
        interval (str): 間隔
        session (sqlalchemy.orm.Session, optional): SQLAlchemyセッション
    """
    if df is None or df.empty:
        return
    
    close_session = False
    if session is None:
        session = DBSession()
        close_session = True
    
    try:
        for _, row in df.iterrows():
            # 既存のデータを確認
            existing = session.query(StockData).filter_by(
                symbol=symbol,
                date=row['Date'],
                interval=interval
            ).first()
            
            if existing:
                # 既存のデータを更新
                existing.open = row['Open']
                existing.high = row['High']
                existing.low = row['Low']
                existing.close = row['Close']
                existing.volume = row['Volume']
            else:
                # 新しいデータを追加
                stock_data = StockData(
                    symbol=symbol,
                    date=row['Date'],
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume'],
                    interval=interval
                )
                session.add(stock_data)
        
        # 最終更新日時を更新
        last_update = session.query(LastUpdate).filter_by(
            symbol=symbol,
            interval=interval
        ).first()
        
        now = datetime.datetime.now()
        
        if last_update:
            last_update.last_update = now
        else:
            last_update = LastUpdate(
                symbol=symbol,
                interval=interval,
                last_update=now
            )
            session.add(last_update)
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error saving data: {e}")
    finally:
        if close_session:
            session.close()

def get_stock_data_from_db(symbol, interval, start_date=None, end_date=None, session=None):
    """
    データベースから株価データを取得する
    
    Args:
        symbol (str): 銘柄コード
        interval (str): 間隔
        start_date (datetime.datetime, optional): 開始日
        end_date (datetime.datetime, optional): 終了日
        session (sqlalchemy.orm.Session, optional): SQLAlchemyセッション
    
    Returns:
        pandas.DataFrame: 株価データ
    """
    close_session = False
    if session is None:
        session = DBSession()
        close_session = True
    
    try:
        query = session.query(StockData).filter_by(
            symbol=symbol,
            interval=interval
        )
        
        if start_date:
            query = query.filter(StockData.date >= start_date)
        
        if end_date:
            query = query.filter(StockData.date <= end_date)
        
        # 日付でソート
        query = query.order_by(StockData.date)
        
        results = query.all()
        
        if not results:
            return None
        
        # DataFrameに変換
        data = {
            'Date': [r.date for r in results],
            'Open': [r.open for r in results],
            'High': [r.high for r in results],
            'Low': [r.low for r in results],
            'Close': [r.close for r in results],
            'Volume': [r.volume for r in results]
        }
        
        df = pd.DataFrame(data)
        df.set_index('Date', inplace=True)
        
        return df
    except Exception as e:
        print(f"Error retrieving data from database: {e}")
        return None
    finally:
        if close_session:
            session.close()

def get_last_update(symbol, interval, session=None):
    """
    最終更新日時を取得する
    
    Args:
        symbol (str): 銘柄コード
        interval (str): 間隔
        session (sqlalchemy.orm.Session, optional): SQLAlchemyセッション
    
    Returns:
        datetime.datetime: 最終更新日時
    """
    close_session = False
    if session is None:
        session = DBSession()
        close_session = True
    
    try:
        last_update = session.query(LastUpdate).filter_by(
            symbol=symbol,
            interval=interval
        ).first()
        
        if last_update:
            return last_update.last_update
        else:
            return None
    except Exception as e:
        print(f"Error retrieving last update: {e}")
        return None
    finally:
        if close_session:
            session.close()

def update_stock_data(symbol, interval='1mo', period='1y'):
    """
    株価データを更新する（差分のみ取得）
    
    Args:
        symbol (str): 銘柄コード
        interval (str): 間隔
        period (str): 取得期間
    
    Returns:
        pandas.DataFrame: 更新後の株価データ
    """
    session = DBSession()
    
    try:
        # 最終更新日時を取得
        last_update = get_last_update(symbol, interval, session)
        
        # データベースからデータを取得
        df_db = get_stock_data_from_db(symbol, interval, session=session)
        
        # 新しいデータを取得
        df_new, symbol = get_stock_data(symbol, period=period, interval=interval)
        
        if df_new is None:
            return df_db
        
        # データベースに保存
        save_stock_data(df_new, symbol, interval, session)
        
        # 更新後のデータを取得
        df_updated = get_stock_data_from_db(symbol, interval, session=session)
        
        return df_updated
    except Exception as e:
        print(f"Error updating stock data: {e}")
        return None
    finally:
        session.close()

def get_or_update_stock_data(symbol, interval='1mo', period='1y'):
    """
    株価データを取得または更新する
    
    Args:
        symbol (str): 銘柄コード
        interval (str): 間隔
        period (str): 取得期間
    
    Returns:
        pandas.DataFrame: 株価データ
    """
    session = DBSession()
    
    try:
        # データベースからデータを取得
        df = get_stock_data_from_db(symbol, interval, session=session)
        
        # データがない場合は新規取得
        if df is None or df.empty:
            df_new, symbol = get_stock_data(symbol, period=period, interval=interval)
            if df_new is not None:
                save_stock_data(df_new, symbol, interval, session)
            return df_new
        
        # 最終更新日時を取得
        last_update = get_last_update(symbol, interval, session)
        
        # 最終更新から1日以上経過している場合は更新
        if last_update is None or (datetime.datetime.now() - last_update).days >= 1:
            return update_stock_data(symbol, interval, period)
        
        return df
    except Exception as e:
        print(f"Error in get_or_update_stock_data: {e}")
        return None
    finally:
        session.close()