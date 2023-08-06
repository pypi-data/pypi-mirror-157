## Rankability Toolbox
This repo contains various implementations that provide insights into the rankability of data and the linear ordering problem.

## Install instructions
### Prerequisites
graphviz headers must be installed:
```bash
apt-get install -y libgraphviz-dev
```

### Recommended package installation
```bash
pip install pyrankability
```

### Post package installation: Gurobi License
This library relies on Gurobi optimizer. Gurobi provides free academic licenses and more information on obtaining and installing your license can be found here: https://support.gurobi.com/hc/en-us/articles/360040541251. 

### Verify installation
```python
import pyrankability
n=8
D=np.zeros((n,n))
D[np.triu_indices(n,1)]=1
D[[5,3,7]] = 1-D[[5,3,7]]
D=pd.DataFrame(D)
k_hillside,details_hillside = pyrankability.rank.solve(D,method='hillside')
k_lop,details_lop = pyrankability.rank.solve(D,method='lop')

assert k_hillside == 54 and k_lop == 12.0
```

## Development notes
### Running tests
```bash
cd ranking_toolbox
python3 -m venv ../env
source ../env/bin/activate
cd tests
pytest tests.py
```

## Authors
Paul Anderson, Ph.D.<br>
Department of Computer Science<br>
Director, Data Science Program<br>
College of Charleston<br>

Amy Langville, Ph.D.<br>
Department of Mathematics<br>
College of Charleston<br>

Tim Chartier, Ph.D.<br>
Department of Mathematics<br>
Davidson College

## Acknowledgements
We would like to thank the entire IGARDS team for their invaluable insight and encouragement.