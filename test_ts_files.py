import os
from datetime import date

path = os.getcwd()
today = date.today().strftime('%Y%m%d')
folders = tuple(os.walk(path))[0][1]
for f in folders:
    if not os.path.exists(os.path.join(path, f, today)):
        print(f + ' no stream')
    else:
        os.chdir(os.path.join(path, f, today))
        if not os.path.exists('ts.tmp'):
            print(f+' no stream')

