#!/usr/bin/env python3
from acts.examples.reconstruction import (
    addSeeding,
    TruthSeedRanges,
    SeedFinderConfigArg,
    SeedFinderOptionsArg,
    SeedFilterConfigArg,
    SpacePointGridConfigArg,
    SeedingAlgorithmConfigArg,
    SeedingAlgorithm,
    ParticleSmearingSigmas,
    addCKFTracks,
    CKFPerformanceConfig,
)
from acts.examples.simulation import (
    addParticleGun,
    MomentumConfig,
    EtaConfig,
    ParticleConfig,
    addPythia8,
    addFatras,
    ParticleSelectorConfig,
    addDigitization,
)
import pathlib
import acts
import acts.examples
import alice3

heavyion = False
u = acts.UnitConstants
geo_dir = pathlib.Path.cwd()
outputDir = pathlib.Path(
    "output/ckf_muongun_100ev_ptmin500MeV_paramsckfv13_cfg10")

detector, trackingGeometry, decorators = alice3.buildALICE3Geometry(
    geo_dir, False, False, acts.logging.VERBOSE)
field = acts.ConstantBField(acts.Vector3(0.0, 0.0, 2.0 * u.T))
rnd = acts.examples.RandomNumbers(seed=42)


s = acts.examples.Sequencer(events=100, numThreads=-1)

if not heavyion:
    addParticleGun(
        s,
        MomentumConfig(0.5 * u.GeV, 10.0 * u.GeV, transverse=True),
        EtaConfig(-4.0, 4.0, uniform=True),
        ParticleConfig(1, acts.PdgParticle.eMuon, randomizeCharge=True),
        rnd=rnd,
    )
else:
    s = addPythia8(
        s,
        npileup=1,
        beam=acts.PdgParticle.eLead,
        cmsEnergy=5 * acts.UnitConstants.TeV,
        # hardProcess=["Top:qqbar2ttbar=on"],
        # npileup=200,
        vtxGen=acts.examples.GaussianVertexGenerator(
            stddev=acts.Vector4(0.0125 * u.mm, 0.0125 *
                                u.mm, 55.5 * u.mm, 5.0 * u.ns),
            mean=acts.Vector4(0, 0, 0, 0),
        ),
        rnd=rnd,
        outputDirRoot=outputDir,
    )
s = addFatras(
    s,
    trackingGeometry,
    field,
    rnd=rnd,
    preSelectParticles=ParticleSelectorConfig(
        eta=(0.0, 4.0), pt=(500 * u.MeV, None), removeNeutral=False),
    outputDirRoot=outputDir,
)
s = addDigitization(
    s,
    trackingGeometry,
    field,
    digiConfigFile=geo_dir / "alice3-smearing-config.json",
    outputDirRoot=outputDir,
    rnd=rnd,
)
s = addSeeding(
    s,
    trackingGeometry,
    field,
    TruthSeedRanges(pt=(0.5 * u.GeV, None), eta=(0, 4.0), nHits=(7, None)),
    SeedFinderConfigArg(
        r=(None, 200 * u.mm),
        deltaR=(1. * u.mm, 60 * u.mm),
        collisionRegion=(-250 * u.mm, 250 * u.mm),
        z=(-2000 * u.mm, 2000 * u.mm),
        maxSeedsPerSpM=1,
        sigmaScattering=5.,
        radLengthPerSeed=0.1,
        minPt=500 * u.MeV,
        impactMax=3. * u.mm,
        cotThetaMax=27.2899,
        seedConfirmation=False,
        centralSeedConfirmationRange=acts.SeedConfirmationRangeConfig(
            zMinSeedConf=-620 * u.mm,
            zMaxSeedConf=620 * u.mm,
            rMaxSeedConf=36 * u.mm,
            nTopForLargeR=1,
            nTopForSmallR=2,
        ),
        forwardSeedConfirmationRange=acts.SeedConfirmationRangeConfig(
            zMinSeedConf=-1220 * u.mm,
            zMaxSeedConf=1220 * u.mm,
            rMaxSeedConf=36 * u.mm,
            nTopForLargeR=1,
            nTopForSmallR=2,
        ),
        skipPreviousTopSP=True,
        useVariableMiddleSPRange=True,
        #deltaRMiddleMinSPRange=10 * u.mm,
        #deltaRMiddleMaxSPRange=10 * u.mm,
        deltaRMiddleSPRange=(1 * u.mm, 10 * u.mm),
    ),
    SeedFinderOptionsArg(bFieldInZ = 2 * u.T, beamPos=(0 * u.mm, 0 * u.mm)),
    SeedFilterConfigArg(
        seedConfirmation=False,
        maxSeedsPerSpMConf=5,
        maxQualitySeedsPerSpMConf=5,
    ),
    SpacePointGridConfigArg(
        # zBinEdges=[
        # -4000.0,
        # -2500.0,
        # -2000.0,
        # -1320.0,
        # -625.0,
        # -350.0,
        # -250.0,
        # 250.0,
        # 350.0,
        # 625.0,
        # 1320.0,
        # 2000.0,
        # 2500.0,
        # 4000.0,
        # ],
        impactMax=3. * u.mm,
        phiBinDeflectionCoverage=3,
    ),
    SeedingAlgorithmConfigArg(
        # zBinNeighborsTop=[
        # [0, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 0],
        # ],
        # zBinNeighborsBottom=[
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 1],
        # [0, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # [-1, 0],
        # ],
        # numPhiNeighbors=1,
    ),
    geoSelectionConfigFile=geo_dir /
    "geoSelection-alice3-cfg10.json",
    outputDirRoot=outputDir,
)
s = addCKFTracks(
    s,
    trackingGeometry,
    field,
    CKFPerformanceConfig(ptMin=500.0 * u.MeV, nMeasurementsMin=7),
    outputDirRoot=outputDir,
    writeTrajectories=True,
)

s.run()

