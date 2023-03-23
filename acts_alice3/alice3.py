#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse

from acts.examples import (
    TGeoDetector,
    WhiteBoard,
    AlgorithmContext,
    ProcessCode,
    CsvTrackingGeometryWriter,
    ObjTrackingGeometryWriter,
    JsonSurfacesWriter,
    JsonMaterialWriter,
    JsonFormat,
    Interval,
)

import acts

from acts import MaterialMapJsonConverter, UnitConstants as u


def runALICE3(
    trackingGeometry,
    decorators,
    outputDir: Path,
    events=1,
    outputObj=True,
    outputCsv=False,
    outputJson=False,
):

    for ievt in range(events):
        eventStore = WhiteBoard(
            name=f"EventStore#{ievt}", level=acts.logging.INFO)
        ialg = 0

        context = AlgorithmContext(ialg, ievt, eventStore)

        for cdr in decorators:
            r = cdr.decorate(context)
            if r != ProcessCode.SUCCESS:
                raise RuntimeError("Failed to decorate event context")

        if outputCsv:
            csv_dir = outputDir / "csv"
            csv_dir.mkdir(exist_ok=True)
            writer = CsvTrackingGeometryWriter(
                level=acts.logging.INFO,
                trackingGeometry=trackingGeometry,
                outputDir=str(csv_dir),
                writePerEvent=True,
            )
            writer.write(context)

        if outputObj:
            obj_dir = outputDir / "obj"
            obj_dir.mkdir(exist_ok=True)
            writer = ObjTrackingGeometryWriter(
                level=acts.logging.INFO,
                outputDir=str(obj_dir),
            )
            writer.write(context, trackingGeometry)

        if outputJson:
            json_dir = outputDir / "json"
            json_dir.mkdir(exist_ok=True)
            writer = JsonSurfacesWriter(
                level=acts.logging.INFO,
                trackingGeometry=trackingGeometry,
                outputDir=str(json_dir),
                writePerEvent=True,
                writeSensitive=True,
            )
            writer.write(context)

            jmConverterCfg = MaterialMapJsonConverter.Config(
                processSensitives=True,
                processApproaches=True,
                processRepresenting=True,
                processBoundaries=True,
                processVolumes=True,
                processNonMaterial=True,
                context=context.geoContext,
            )

            jmw = JsonMaterialWriter(
                level=acts.logging.VERBOSE,
                converterCfg=jmConverterCfg,
                fileName=str(json_dir / "geometry-map"),
                writeFormat=JsonFormat.Json,
            )

            jmw.write(trackingGeometry)


def buildALICE3Geometry(
    geo_dir: Path,
    material: bool = False,
    jsonconfig: bool = False,
    logLevel=acts.logging.DEBUG,
):

    logger = acts.logging.getLogger("buildALICE3Geometry")

    matDeco = None
    if material:
        file = geo_dir / "material-maps.root"
        logger.info("Adding material from %s", file.absolute())
        matDeco = acts.IMaterialDecorator.fromFile(
            file,
            level=acts.logging.Level(
                min(acts.logging.INFO.value, logLevel.value)),
        )

    tgeo_fileName = geo_dir / "geom/o2sim_geometry_alice3.root"

    if jsonconfig:
        jsonFile = geo_dir / "tgeo-config.json"
        logger.info("Create geometry from %s", jsonFile.absolute())
        return TGeoDetector.create(
            jsonFile=str(jsonFile),
            fileName=str(tgeo_fileName),
            surfaceLogLevel=logLevel,
            layerLogLevel=logLevel,
            volumeLogLevel=logLevel,
            mdecorator=matDeco,
        )

    Volume = TGeoDetector.Config.Volume
    LayerTriplet = TGeoDetector.Config.LayerTriplet
    equidistant = TGeoDetector.Config.BinningType.equidistant
    arbitrary = TGeoDetector.Config.BinningType.arbitrary

    return TGeoDetector.create(
        fileName=str(tgeo_fileName),
        mdecorator=matDeco,
        buildBeamPipe=True,
        unitScalor=10.0,  # explicit units
        beamPipeRadius=3.7 * u.mm,
        beamPipeHalflengthZ=500.0 * u.mm,
        beamPipeLayerThickness=0.1 * u.mm,
        beampipeEnvelopeR=0.1 * u.mm,
        layerEnvelopeR=0.1 * u.mm,
        surfaceLogLevel=logLevel,
        layerLogLevel=logLevel,
        volumeLogLevel=logLevel,
        volumes=[
            Volume(
                name="InnerPixels",
                binToleranceR=(5 * u.mm, 5 * u.mm),
                binToleranceZ=(5 * u.mm, 5 * u.mm),
                binTolerancePhi=(0.025 * u.mm, 0.025 * u.mm),
                layers=LayerTriplet(True),
                subVolumeName=LayerTriplet(
                    negative="FT3*", central="ITS*", positive="FT3*"),
                sensitiveNames=LayerTriplet(
                    negative=["FT3Sensor*"], central=["ITSUSensor*"], positive=["FT3Sensor*"]),
                sensitiveAxes=LayerTriplet("XYZ"),
                rRange=LayerTriplet((3.9 * u.mm, 45 * u.mm)),
                zRange=LayerTriplet(
                    negative=(-400 * u.mm, -250 * u.mm),
                    central=(-250 * u.mm, 250 * u.mm),
                    positive=(250 * u.mm, 400 * u.mm),
                ),
                splitTolR=LayerTriplet(
                    negative=-1.0, central=3 * u.mm, positive=-1.0),
                splitTolZ=LayerTriplet(
                    negative=10 * u.mm, central=-1.0, positive=10 * u.mm),
                binning0=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                binning1=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                cylinderDiscSplit=True,
                cylinderNZSegments=0,
                cylinderNPhiSegments=0,
                discNRSegments=1,
                discNPhiSegments=32,
                itkModuleSplit=False,
                barrelMap={},
                discMap={},
            ),
            Volume(
                name="OuterPixels",
                binToleranceR=(5 * u.mm, 5 * u.mm),
                binToleranceZ=(5 * u.mm, 5 * u.mm),
                binTolerancePhi=(0.025 * u.mm, 0.025 * u.mm),
                layers=LayerTriplet(True),
                subVolumeName=LayerTriplet(
                    negative="FT3*", central="ITS*", positive="FT3*"),
                sensitiveNames=LayerTriplet(
                    negative=["FT3Sensor*"], central=["ITSUSensor*"], positive=["FT3Sensor*"]),
                sensitiveAxes=LayerTriplet("XYZ"),
                rRange=LayerTriplet(negative=(50 * u.mm, 1000 * u.mm),
                                    central=(50 * u.mm, 350 * u.mm),
                                    positive=(50 * u.mm, 1000 * u.mm)),
                zRange=LayerTriplet(
                    negative=(-1300 * u.mm, -700 * u.mm),
                    central=(-700 * u.mm, 700 * u.mm),
                    positive=(700 * u.mm, 1300 * u.mm),
                ),
                splitTolR=LayerTriplet(
                    negative=-1.0, central=5 * u.mm, positive=-1.0),
                splitTolZ=LayerTriplet(
                    negative=5 * u.mm, central=-1.0, positive=5 * u.mm
                ),
                binning0=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                binning1=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                cylinderDiscSplit=True,
                cylinderNZSegments=6,
                cylinderNPhiSegments=32,
                discNRSegments=6,
                discNPhiSegments=32,
                itkModuleSplit=False,
                barrelMap={},
                discMap={},
            ),
            Volume(
                name="OuterMostBarrel",
                binToleranceR=(5 * u.mm, 5 * u.mm),
                binToleranceZ=(5 * u.mm, 5 * u.mm),
                binTolerancePhi=(0.025 * u.mm, 0.025 * u.mm),
                layers=LayerTriplet(
                    positive=False, central=True, negative=False),
                subVolumeName=LayerTriplet("ITS*"),
                sensitiveNames=LayerTriplet(["ITSUSensor*"]),
                sensitiveAxes=LayerTriplet("XYZ"),
                rRange=LayerTriplet(
                    central=(445 * u.mm, 1500 * u.mm),
                ),
                zRange=LayerTriplet(
                    central=(-1400 * u.mm, 1400 * u.mm),
                ),
                splitTolR=LayerTriplet(
                    central=5 * u.mm,
                ),
                splitTolZ=LayerTriplet(-1.0),
                binning0=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                binning1=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                cylinderDiscSplit=True,
                cylinderNZSegments=6,
                cylinderNPhiSegments=32,
                discNRSegments=0,
                discNPhiSegments=0,
                itkModuleSplit=False,
                barrelMap={},
                discMap={},
            ),
            Volume(
                name="OuterMostEndcap",
                binToleranceR=(5 * u.mm, 5 * u.mm),
                binToleranceZ=(5 * u.mm, 5 * u.mm),
                binTolerancePhi=(0.025 * u.mm, 0.025 * u.mm),
                layers=LayerTriplet(
                    positive=True, central=False, negative=True),
                subVolumeName=LayerTriplet("FT3*"),
                sensitiveNames=LayerTriplet(["FT3Sensor*"]),
                sensitiveAxes=LayerTriplet("XYZ"),
                rRange=LayerTriplet(
                    negative=(0 * u.mm, 1500 * u.mm),
                    positive=(0 * u.mm, 1500 * u.mm),
                ),
                zRange=LayerTriplet(
                    negative=(-4200 * u.mm, -1350 * u.mm),
                    positive=(1350 * u.mm, 4200 * u.mm),
                ),
                splitTolR=LayerTriplet(-1.0),
                splitTolZ=LayerTriplet(negative=5 * u.mm, positive=5 * u.mm),
                binning0=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                binning1=LayerTriplet(
                    negative=[(0, equidistant)],
                    central=[(0, equidistant)],
                    positive=[(0, equidistant)],
                ),
                cylinderDiscSplit=True,
                cylinderNZSegments=0,
                cylinderNPhiSegments=0,
                discNRSegments=6,
                discNPhiSegments=32,
                itkModuleSplit=False,
                barrelMap={},
                discMap={},
            ),
        ],
    )


if "__main__" == __name__:
    p = argparse.ArgumentParser(
        description="Example script to construct the ALICE3 geometry and write it out to CSV and OBJ formats"
    )
    p.add_argument(
        "geo_dir",
        help="Input directory containing the ALICE3 standalone geometry.",
    )
    p.add_argument(
        "--output-dir",
        default=Path.cwd(),
        type=Path,
        help="Directory to write outputs to",
    )
    p.add_argument(
        "--output-csv", action="store_true", help="Write geometry in CSV format."
    )
    p.add_argument(
        "--output-obj", action="store_true", help="Write geometry in OBJ format."
    )
    p.add_argument(
        "--output-json",
        action="store_true",
        help="Write geometry and material in JSON format.",
    )
    p.add_argument(
        "--no-material", action="store_true", help="Decorate material to the geometry"
    )

    args = p.parse_args()
    args.output_dir.mkdir(exist_ok=True, parents=True)

    geo_example_dir = Path(args.geo_dir)
    assert geo_example_dir.exists(), "Detector example input directory missing"

    detector, trackingGeometry, decorators = buildALICE3Geometry(
        geo_example_dir,
        material=not args.no_material,
    )

    runALICE3(
        trackingGeometry=trackingGeometry,
        decorators=decorators,
        outputDir=args.output_dir,
        outputCsv=args.output_csv,
        outputObj=args.output_obj,
        outputJson=args.output_json,
    )
