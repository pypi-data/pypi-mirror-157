import pandas as pd 

def tabulator(path,data_type: str,columns: list[str]):

    dtype_list = ['xlsx','csv']
    
    if data_type == dtype_list[0]:
        data = pd.read_excel(path)
        selected = data[columns]
        print(selected)

    if data_type == dtype_list[-1]:
        data = pd.read_csv(path)
        selected = data[columns]
        print(selected)

