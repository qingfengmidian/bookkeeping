import pandas as pd

def process_monthly(df):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    monthly = df.pivot_table(index='年月', columns='类型', values='金额', aggfunc='sum', fill_value=0)
    monthly['总收入'] = monthly.get('收入', 0)
    monthly['总支出'] = monthly.get('支出', 0)
    return monthly

def process_detail(df, month):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    return df[df['年月'] == month]
