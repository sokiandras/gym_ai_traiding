import yfinance as yf

input_string = "1h"
numeric_value = int(input_string[:-1])

print(numeric_value)

symbol = "aapl"
start_date = "2022-02-01"
end_date = "2023-01-01"


testdata = yf.download(symbol, start=start_date, end=end_date, interval=input_string)

#pd.set_option("display.max_columns", None)
print("Testdata head: ")
print(testdata.head())

print("Első 10 ár a testdata-ból")
i=0
for i in range(10):
    print(testdata.iloc[i,0])
print("Stepnumber test: ")
stepnumber = len(testdata)
print('stepnumber: ', stepnumber)
print('utolsó ár: ', testdata.iloc[1612,0])