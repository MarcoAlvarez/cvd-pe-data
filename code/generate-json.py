import json
import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

def load_excel_dict(fname, kwargs):
    df = pd.read_excel(fname, **kwargs).dropna()
    logging.info('{} read with shape {}x{}'.format(fname, df.shape[0], df.shape[1]))
    name, val = df.columns
    df[name] = df[name].map(lambda x: x.title())
    return pd.Series(df[val].values, index=df[name]).to_dict()
    
def load_local_files():
    pop_pe = load_excel_dict('./others/peru-population-2020-inei.xlsx', {'sheet_name':'DEPARTAMENTAL','skiprows':6,'skipfooter':4,'usecols':[1,2]})
    pop_w = load_excel_dict('./others/world-population.xlsx', {'sheet_name':'Data','skipfooter':5,'usecols':[0,4]})
    reg_pe = load_excel_dict('./others/peru-regions.xlsx', {})
    return pop_pe, pop_w, reg_pe 

def load_table(fname, places=None):
    df = pd.read_csv(fname, index_col=0)
    logging.info('{} read with shape {}x{}'.format(fname, df.shape[0], df.shape[1]))
    if places != None:
        df = df.loc[places]
    return { dt:df[dt].to_dict() for dt in df.columns }

def update_json(df, pop, others, avg_len):
    dates = sorted(df.keys())
    places = sorted(df[dates[0]].keys())
    entry = {}
    entry['d'] = dates[-1]
    entry['stats'] = {}
    tot = 0
    tot_p = 0
    for p in places:
        entry['stats'][p] = {}
        entry['stats'][p]['p'] = pop[p]
        for k,v in others.items():
            entry['stats'][p][k] = v[p]
        entry['stats'][p]['dates'] = dates
        counts, avgs = [], []
        n = len(dates)
        _t = 0
        for i in range(n):
            _c = df[dates[i]][p] if i == 0 else (df[dates[i]][p] - df[dates[i-1]][p])
            _t += _c
            j = avg_len - 1 if i > (avg_len-1) else i
            _a = (_c + sum([counts[x] for x in range(i-j,i)])) / (j+1)
            counts.append(_c)
            avgs.append(round(_a,2))
        entry['stats'][p]['data'] = {'c':counts, 'a':avgs}
        entry['stats'][p]['t'] = _t
        tot_p += pop[p]
        tot += _t
    entry['t'] = tot
    entry['tp'] = tot_p
    return entry

def save_file(data, fname):
    with open(fname, 'wt') as fid:
        json.dump(data, fid, separators=(',', ':'))
    logging.info('{} succesfully saved'.format(fname))

def run_app():
    # read local files
    pop_pe, pop_w, reg_pe = load_local_files()
    # read JHU files
    countries = ['Colombia', 'Peru', 'Bolivia', 'Chile', 'Brazil', 'Ecuador', 'Argentina', 'Venezuela', 'Uruguay', 'Paraguay', 'Mexico', 'Panama', 'United States', 'Spain', 'Italy', 'France', 'Portugal', 'United Kingdom', 'Sweden', 'Germany', 'Russia']
    jhu_c = load_table('./csv/jhu/consolidated-jhu-c.csv', countries)
    jhu_f = load_table('./csv/jhu/consolidated-jhu-f.csv', countries)
    # read ODPE files
    odpe_c = load_table('./csv/odpe/consolidated-odpe-c.csv')
    odpe_f = load_table('./csv/odpe/consolidated-odpe-f.csv')
    # update and save json files
    avg_n = 7
    save_file(update_json(odpe_f, pop_pe, {'r':reg_pe}, avg_n), './json/odpe/data-odpe-f.json')
    save_file(update_json(odpe_c, pop_pe, {'r':reg_pe}, avg_n), './json/odpe/data-odpe-c.json')
    #    save_file(update_json(jhu_f, pop_w, {}, avg_n), './json/jhu/data-jhu-f.json')
    #    save_file(update_json(jhu_c, pop_w, {}, avg_n), './json/jhu/data-jhu-c.json')

if __name__ == "__main__":
    run_app()
