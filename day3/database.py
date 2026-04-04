from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

engine = create_engine("sqlite:///dantri_news.db", echo=False)
metadata = MetaData()

articles_table = Table(
    "articles", 
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(500), nullable=False),
    Column("link", String(500), nullable=False, unique=True)
)

def init_db():
    metadata.create_all(engine)
    print("Đã thiết lập xong Database 'dantri_news.db'!")