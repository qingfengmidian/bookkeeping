import pandas as pd


def process_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    按月汇总收支数据。
    
    Args:
        df: 原始账单DataFrame，包含列：日期、类型、金额
        
    Returns:
        月度汇总透视表，列包含：收入、支出、总收入、总支出
        索引为年月(YYYY-MM格式)
        
    Example:
        >>> df = pd.DataFrame({
        ...     '日期': ['2025-01-01', '2025-01-02'],
        ...     '类型': ['收入', '支出'],
        ...     '金额': [1000.0, 50.0]
        ... })
        >>> monthly = process_monthly(df)
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce', format='mixed')
    df = df.dropna(subset=['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    monthly = df.pivot_table(index='年月', columns='类型', values='金额', aggfunc='sum', fill_value=0)
    monthly['总收入'] = monthly.get('收入', 0)
    monthly['总支出'] = monthly.get('支出', 0)
    return monthly


def process_detail(df: pd.DataFrame, month: str) -> pd.DataFrame:
    """
    获取指定月份的明细数据。
    
    Args:
        df: 原始账单DataFrame
        month: 目标月份，格式为'YYYY-MM'
        
    Returns:
        指定月份的明细DataFrame
        
    Example:
        >>> df = pd.DataFrame({
        ...     '日期': ['2025-01-01', '2025-02-01'],
        ...     '类型': ['收入', '支出'],
        ...     '金额': [1000.0, 50.0]
        ... })
        >>> jan_data = process_detail(df, '2025-01')
    """
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce', format='mixed')
    df = df.dropna(subset=['日期'])
    df['年月'] = df['日期'].dt.to_period('M').astype(str)
    return df[df['年月'] == month]
