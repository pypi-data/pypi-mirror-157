![Screenshot_10](https://user-images.githubusercontent.com/64541739/174754962-952e3e72-0b2c-4ae6-987d-9f46c965e5c4.png)

# Easy Predictor

Perform Regression/Classifcation prediction on Excel dataset with ease.   

## Features

- Perform linear regression prediction by utilizing **linear** function
- Perform classification prediction by utilizing **classification** function
- Perform statistical calculation by utilizing **stats** function
- Visualize excel dataset by utilizing **tabulator** 

## Instruction

1. Linear Regression Prediction

```python
from easy_predictor import linear 

dataset = "path_to_excel_file"
linear.predict(dataset,dataset_type: 'xlsx','csv',columns=list[str],column_y,value: int)
```
2. Text Classification Prediction

```python
from easy_predictor import classification

dataset = "path_to_excel_file"
classification.predict(dataset,dataset_type: 'xlsx','csv',columns=list[str],column_y,value: str)
```

3. Visualize Data

```python
from easy_predictor import table

dataset = "path_to_excel_file"
table.tabulator(dataset,dataset_type: 'xlsx','csv',columns=list[str])
```

# Github Link

https://github.com/Tho100/easy_predictor

## Latest Update 0.1.0

```
CSV (Comma Seperated Values) File supported
```
## Latest Update 0.2.0

```
New 'table' Function To Visualize Data In Tabular Form
```

## Latest Update 0.3.0

```
ImportError: cannot import name 'table' from 'easy_predictor'. Bug
Fixed
```

## Latest Update 0.4.0

```
TypeError: object of type 'int' has no len(). Bug Fixed
```

## Latest Update 0.5.0

```
Bugs Fixed
```

## Latest Update 0.6.1

```
Multiple Column Input Supported
```

## Latest Update 0.6.2

```
Statistical Function
```

## Latest Update 0.6.3

```
Bugs Fixed
```

## Latest Update 0.6.6

```
User now can assign the predicted value to variable
```