from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd 
from sklearn.model_selection import train_test_split

class classification:
    def predict(data: str,data_type: str,input_col: list[str],value: list[str],output_col: str):
        ERROR_LIST = {
            'null_value': "'value' Input can't be null",
            'null_dataset': "'data' can't be null"
        }

        value_list = [value]

        if data_type == "xlsx":
            if len(value_list) != 0:
                data = pd.read_excel(data)

                column_x = data[input_col].values
                column_y = data[[output_col]].values

                vectorizer = CountVectorizer(binary=True)
                vectors = vectorizer.fit_transform(column_x.ravel())

                model = svm.SVC(kernel='linear')
                model.fit(vectors,column_y.ravel())
                input = vectorizer.transform(value)
                pred = model.predict(input)
                for t in pred:
                    for q in t:
                        return q
            else:
                print(ERROR_LIST['null_value'])

        if data_type == 'csv':
            if len(value_list) != 0:
                data = pd.read_csv(data)

                column_x = data[input_col].values
                column_y = data[[output_col]].values

                vectorizer = CountVectorizer(binary=True)
                vectors = vectorizer.fit_transform(column_x.ravel())
        
                model = svm.SVC(kernel='linear')
                model.fit(vectors,column_y.ravel())
                input = vectorizer.transform(value)
                pred = model.predict(input)
                for r in pred:
                    for j in r:
                        return j
            else:
                print(ERROR_LIST['null_value'])
