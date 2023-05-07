# acts_alice3

## Instructions how to run the full chain simulation and reconstruction.

Full ACTS documentation is located [here](https://acts.readthedocs.io/en/latest/).
The configuration files located in the `acts_alice3` folder correspond to the ALICE3 layout v3a from the [ALICE3 letter of intent](https://cds.cern.ch/record/2803563?ln=en).

Assuming the ACTS software is installed with aliBuild and the directory with the provided files is cloned into the `alice` directory:
```
cd alice
git clone git@github.com:AliceO2Group/acts.git ACTS
aliBuild build ACTS -d
```

Setup the python bindings: 
* ```cd acts_alice3```
* ```alienv enter ACTS/latest-main-o2```
* ```source ../../sw/BUILD/ACTS-latest-main/ACTS/python/setup.sh```
* if successful the following message is printed: `INFO:    Acts Python 3.9 bindings setup complete.`

When completed, one runs the full chain simulation and reconstruction with a single script:
```
python full_chain_alice3.py
```

This will simulate a particle gun of muons in pseudorapidity range of `-4:4` with $\it{p}_{\rm{T}}$ from 0.5 to 10 GeV/*c*. The configuration of the particle gun is set by the `addParticleGun` method, if one wants to use Pythia generator, it is configured by `addPythia8`.
The propagation options of the generated particles are set in the `addFatras` method using the [FATRAS](https://indico.cern.ch/event/1184037/contributions/5071732/attachments/2517716/4328846/2022-09-28-ACTS-WS-Fatras.pdf) engine, and the `addDigitization` configures the smearing of the MC particle hits according to the resolution of the layers.
`addSeeding` enables the [seeding](https://acts.readthedocs.io/en/latest/core/seeding.html) algorithm and the `addCKFTracks` runs the simultaneous track finding and track fitting using the [Combinatorial Kalman Filter](https://acts.readthedocs.io/en/latest/tracking.html#combinatorial-kalman-filter) algorithm.   

The output root files are created in the `output` directory.

For the analysis of the output the [Analysis applications](https://acts.readthedocs.io/en/latest/examples/analysis_apps.html) are used.

