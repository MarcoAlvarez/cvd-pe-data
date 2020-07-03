import sys
import logging
import pandas as pd
from datetime import datetime as dttm 
from datetime import timedelta
import numpy as np
logging.basicConfig(level=logging.INFO)

def save_odpe(fname, tgt_file, field):
    # download file from URL
    df = pd.read_csv(fname, encoding='latin-1')
    logging.info('{} read with shape {}x{}'.format(fname, df.shape[0], df.shape[1]))
    # create table of unique indices (region names)
    idx_vec = sorted(df['DEPARTAMENTO'].unique())
    idx_tab = {v:k for k,v in enumerate(idx_vec)}
    # reformat dates and sort in ascending order
    df[field] = df[field].map(lambda x: dttm.strptime(x,'%d/%m/%Y').strftime('%Y/%m/%d') if isinstance(x,str) else '')
    cols_vec = sorted(df[field].unique())
    if '' in cols_vec:
        cols_vec.remove('')
    # remove dates after today (this is necessary due to errors in the original file)
    # month and day were swapped in a few cases
    today = dttm.now().strftime('%Y/%m/%d')
    cols_vec = list(filter(lambda x: x <= today, cols_vec))
    # generate a list of consistent dates (no missing dates in the series)
    s_date = dttm.strptime(cols_vec[0],'%Y/%m/%d')
    n_dates = (dttm.strptime(cols_vec[-1],'%Y/%m/%d')-dttm.strptime(cols_vec[0],'%Y/%m/%d')).days + 1
    cols_vec = [(s_date+timedelta(days=i)).strftime('%Y/%m/%d') for i in range(n_dates)]
    # create table of unique dates
    cols_tab = {v:k for k,v in enumerate(cols_vec)}
    # create and fill matrix with integer values (per day statistics)
    matrix = np.zeros((len(idx_vec),len(cols_vec)), dtype=int)
    count1, count2 = 0, 0
    for i, row in df.iterrows():
        if row[field] == '':
            count1 += 1
        elif row[field] not in cols_tab:
            count2 += 1
        else:
            matrix[idx_tab[row['DEPARTAMENTO']], cols_tab[row[field]]] += 1
    logging.warning('{} rows ignored, either empty ({}) or date out-of-range ({})'.format(count1+count2,count1,count2))
    # aggregate columns
    for i in range(1, matrix.shape[1]):
        matrix[:,i] += matrix[:,i-1]
    # create new dataframe and save it to disk
    newdf = pd.DataFrame(data=matrix, index=idx_vec, columns=cols_vec)
    newdf.index = newdf.index.str.title()
    newdf.to_csv(tgt_file)
   
def save_jhu(fname, tgt_file):
    # download file from URL
    df = pd.read_csv(fname)
    logging.info('{} read with shape {}x{}'.format(fname, df.shape[0], df.shape[1]))
    # drop and reformat dates, aggregate data by countries
    df = df.drop(columns=['Lat', 'Long'])
    df = df.groupby(by='Country/Region').sum()
    df.rename(lambda x: dttm.strptime(x,'%m/%d/%y').strftime('%Y/%m/%d'), axis='columns', inplace=True)
    # check dates are consisten (no missing dates in the series)
    assert(((dttm.strptime(df.columns[-1],'%Y/%m/%d') - dttm.strptime(df.columns[0],'%Y/%m/%d')).days+1) == len(df.columns))
    # final details
    df.index.name = 'Country'
    df.index = df.index.str.title()
    df.rename(index={'Us':'United States'}, inplace=True)
    # save to file
    df.to_csv(tgt_file)

# must specify two command line arguments
# <source> either 'minsa' or 'jhu' or 'odpe'
# <date> for minsa, in the format ddmmyyyy
if __name__ == "__main__":
    assert len(sys.argv) == 2
    assert sys.argv[1] in set(['jhu', 'odpe']) 
    if sys.argv[1] == 'jhu':
        save_jhu('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', 'consolidated-jhu-c.csv')
        save_jhu('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', 'consolidated-jhu-f.csv')
    if sys.argv[1] == 'odpe':
        save_odpe('https://cloud.minsa.gob.pe/s/Md37cjXmjT9qYSa/download', 'consolidated-odpe-f.csv', 'FECHA_FALLECIMIENTO')
        save_odpe('https://cloud.minsa.gob.pe/s/Y8w3wHsEdYQSZRp/download', 'consolidated-odpe-c.csv', 'FECHA_RESULTADO')
