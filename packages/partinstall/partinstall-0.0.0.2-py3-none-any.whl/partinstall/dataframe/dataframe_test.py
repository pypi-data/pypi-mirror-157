import pandas as pd
def to_dataframe(array_data):
    df_data = pd.DataFrame(array_data)
    print(df_data)
    return df_data