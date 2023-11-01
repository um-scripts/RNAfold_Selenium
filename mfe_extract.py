import pandas as pd
import numpy as np
import os
import re

D = pd.read_csv('66StrandExpV.csv', names=['Ref', 'start', 'end',  'strand'])
D['MFE'] = np.nan
for i, row in D.iterrows():
    dir_name = f"NC_000962.3 {row['start']}-{row['end']}({row['strand']})"
    # dir_name = f"NC_000962.3 {row['start']}-{row['end']}"
    name = os.path.join('65strandExperimentallyV_curated', dir_name, 'mfe_ct_format.txt')
    print(name)
    d = open(name, 'r').readline().strip('\n')
    m = re.match('^.*ENERGY *= *(-?[0-9]+\\.[0-9]+).*$', d)
    D.loc[i, 'MFE'] = float(m.groups()[0])

D.to_csv('65_StrandExperimentV.csv', index=False)