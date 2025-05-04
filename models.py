from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime

# データベースの設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'stock_data.db')
engine = create_engine(f'sqlite:///{DATABASE_PATH}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class StockData(Base):
    """株価データを保存するモデル"""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)  # 銘柄コード
    date = Column(DateTime, nullable=False)  # 日付
    open = Column(Float)  # 始値
    high = Column(Float)  # 高値
    low = Column(Float)  # 安値
    close = Column(Float)  # 終値
    volume = Column(Integer)  # 出来高
    interval = Column(String)  # 間隔 (1d, 1wk, 1mo など)
    
    def __repr__(self):
        return f"<StockData(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

class LastUpdate(Base):
    """最終更新日時を保存するモデル"""
    __tablename__ = 'last_update'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)  # 銘柄コード
    interval = Column(String, nullable=False)  # 間隔 (1d, 1wk, 1mo など)
    last_update = Column(DateTime, nullable=False)  # 最終更新日時
    
    def __repr__(self):
        return f"<LastUpdate(symbol='{self.symbol}', interval='{self.interval}', last_update='{self.last_update}')>"

# データベースの初期化
def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()