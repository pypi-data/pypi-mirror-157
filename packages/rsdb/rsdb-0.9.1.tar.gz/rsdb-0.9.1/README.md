# rsdb
Object–relational mapping for [RiskSpectrum PSA](https://www.lr.org/en/riskspectrum/technical-information/psa/) model database.

[![image](https://img.shields.io/pypi/v/rsdb.svg)](https://pypi.python.org/pypi/rsdb/)

## Installation
```sh
# PyPI
pip install rsdb
```

## Usage
```python
from rsdb.connection import Connector
import rsdb.orm

server = Connector(ip='<ip>', port=1433)
# Show available models
print(server.GetAvailableModels())
# Get SqlAlchemy session factory
Session = server.GetModelSession('<model_name>')

with Session() as session:
    event_trees = session.execute(select(rsdb.orm EventTrees)).scalars().all()
        for et in event_trees:
            print(et.ID)
            func_events = et.FunctionEvents
            for event in func_events:
                print(f'\t fe:{e.ID}')

            initiating_event = et.InitiatingEvent
            print(f'\t ie:{ie.ID}')
```