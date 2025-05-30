from datetime import datetime
import pandas as pd

def format_date(val):
    try:
        if pd.isna(val): return "Unknown"
        if isinstance(val, str):
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try: return datetime.strptime(val, fmt).strftime("%B %d, %Y")
                except: continue
            return val
        elif isinstance(val, (datetime, pd.Timestamp)):
            return val.strftime("%B %d, %Y")
        return str(val)
    except:
        return str(val)
