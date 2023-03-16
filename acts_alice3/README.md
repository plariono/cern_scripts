# acts_alice3

## Instructions how to run the full chain simulation and reconstruction.

Assuming the ACTS software is installed with aliBuild. The provided files must be copied:
* `alice3.py` and `full_chain_alice3.py` in `$ACTS_SOURCE/Examples/Scripts/Python/` 
* the `geom` folder and the json files in `$ACTS_BUILD/bin/`

Before running the full chain script the acts module should be loaded: 

```
source $ACTS_BUILD/python/setup.sh
```

Then from the source directory:

```
python3 Examples/Scripts/Python/full_chain_alice3.py
```

