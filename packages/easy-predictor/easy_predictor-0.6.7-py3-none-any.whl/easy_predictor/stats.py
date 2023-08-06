import pandas as pd
from collections import Counter

class statistical:
    def mean(self,dataset: str,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            s = 0
            for i in selected_column:
                s = s + i
            result = (s/len(selected_column))
            for q in result:
                return q

        if data_type == 'csv':
            data = pd.read_csv(dataset)
            selected_column = data[column].values
            s = 0
            for i in selected_column:
                s = s + i
            result = (s/len(selected_column))
            for p in result:
                return p

    def median(self,dataset,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            median = (selected_column[0]+selected_column[-1])/2
            result = (median)   
            for u in result:
                return u

        if data_type == 'csv':  
            data = pd.read_csv(dataset)       
            selected_column = data[column].values
            median = (selected_column[0]+selected_column[-1])/2
            result = (median)
            for t in result:
                return t

    def mode(self,dataset,data_type: str,column: list[str]):
        if data_type == 'xlsx':
            data = pd.read_excel(dataset)
            selected_column = data[column].values
            to_tuple = [tuple(x) for x in selected_column] # Hashable
            result = ([Counter(to_tuple).most_common(1)[0][0]])
            for i in result:
                for t in i:
                    return t
            
        if data_type == 'csv':
            data = pd.read_csv(dataset)
            selected_column = data[column].values
            to_tuple = [tuple(x) for x in selected_column] # Hashable
            result = ([Counter(to_tuple).most_common(1)[0][0]])
            for m in result:
                for j in m:
                    return j

    def half(self,dataset,data_type: str,column: list[str]):
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