# acts_alice3

## Instructions how to run the full chain simulation and reconstruction.

Full ACTS documentation is located [here](https://acts.readthedocs.io/en/latest/).

Assuming the ACTS software is installed with aliBuild and the directory with the provided files is cloned into the `alice` directory.

Setup the python bindings: 
* ```cd acts_alice3```
* ```alienv enter ACTS/latest-main-o2```
* ```source ../../sw/BUILD/ACTS-latest-main/ACTS/python/setup.sh```
* if successful the following message is printed: `INFO:    Acts Python 3.9 bindings setup complete.`

When completed, one runs the full chain simulation and reconstruction:
```
python full_chain_alice3.py
```

This will create the output root files in the `output` directory.
The following configuration is set:
* particle gun with $\mu^{\pm}$ with $\it{p}_{\rm{T}}$ from 0.5 to 10 GeV/*c*
* seeding configuration is given in the `addSeeding` section and the CKF one in the `addCKFTracks`