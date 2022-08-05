import pandas as pd
from pathlib import Path    
from sklearn.preprocessing import LabelEncoder      

file_name = "ExecutedTraces.csv"
df = pd.read_csv(file_name)
stations = df.columns.get_loc('at station')

left = df.iloc[:, :stations]
dumb = pd.get_dummies(df['at station'], prefix="at station ", prefix_sep='')
rite = df.iloc[:, stations+1:]

df = pd.concat([left, dumb, rite], axis=1)

decision_df = pd.DataFrame(df, columns=['Decision'])
# creating instance of labelencoder
labelencoder = LabelEncoder()
# Assigning numerical values and storing in another column
df['Decision'] = labelencoder.fit_transform(decision_df['Decision'])
#df = df.drop('Decision', axis=1)

filepath = Path('ExecutedTracesOneHot.csv')  
df.to_csv(filepath, index=False) 

