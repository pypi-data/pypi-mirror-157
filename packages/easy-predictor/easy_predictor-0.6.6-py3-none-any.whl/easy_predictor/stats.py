import pandas as pd
from collections import Counter

class statistical:
    def mean(dataset,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            s = 0
            for i in selected_column:
                s = s + i
            return (s/len(selected_column))

        if data_type == 'csv':
            data = pd.read_csv(dataset)
            selected_column = data[column].values
            s = 0
            for i in selected_column:
                s = s + i
            return (s/len(selected_column))
            
    def median(dataset,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            median = (selected_column[0]+selected_column[-1])/2
            return (median)   

        if data_type == 'csv':  
            data = pd.read_csv(dataset)       
            selected_column = data[column].values
            median = (selected_column[0]+selected_column[-1])/2
            return (median)

    def mode(dataset,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            to_tuple = [tuple(x) for x in selected_column] # Hashable
            return ([Counter(to_tuple).most_common(1)[0][0]])
            
        if data_type == 'csv':
            data = pd.read_csv(dataset)
            selected_column = data[column].values
            to_tuple = [tuple(x) for x in selected_column] # Hashable
            return ([Counter(to_tuple).most_common(1)[0][0]])

def half(dataset,data_type: str,column: list[str]):
    if data_type == 'xlsx':
        data = pd.read_excel(dataset)   
        selected_column = data[column]
        selected_column = selected_column.apply(lambda r: r / 2)
        return (selected_column)

    if data_type == 'csv':
        data = pd.read_csv(dataset)   
        selected_column = data[column]
        selected_column = selected_column.apply(lambda r: r / 2)
        return (selected_column)