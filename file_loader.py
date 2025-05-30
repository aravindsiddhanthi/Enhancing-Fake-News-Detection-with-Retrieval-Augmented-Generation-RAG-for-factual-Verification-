import pandas as pd

def load_data(file):
    ext = file.name.split('.')[-1].lower()
    if ext in ['xlsx', 'xls']:
        return pd.read_excel(file)
    elif ext == 'csv':
        try:
            return pd.read_csv(file)
        except:
            return pd.read_csv(file, encoding='latin1')
    else:
        raise ValueError("Unsupported file format")
