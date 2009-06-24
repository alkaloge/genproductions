#------------------------------------------------------------------------
# Production of cosmics, underground
# CMSSW 2_2_11. CMS geometry incl. smaller shafts and more detailed simulation
# Last update: K.Hoepfner 08.05.09
#
# Special sample for HCAL: limited to tracker acceptance
# B-field OFF, Global tag for ECAL gain 50 and no field: COSMMC_BOFFV3
# Pmin = 100 GeV
#-----------------------------------------------------------------------

import FWCore.ParameterSet.Config as cms

process = cms.Process("runCosMuoGen")

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))

process.configurationMetadata = cms.untracked.PSet(
    version = cms.untracked.string('$Revision: 1.1 $'),
    name = cms.untracked.string('$Source:/cvs_server/repositories/CMSSW/CMSSW/Configuration/GenProduction/python/CosmicMC_BOFF_10GeV_TrackerOnly_cfg.py'),
    annotation = cms.untracked.string('Simulated cosmics, HCAL samples')
    )

#--------- Standard sequences

process.load('FWCore/MessageService/MessageLogger_cfi')

process.load("Configuration.StandardSequences.GeometryPilot2_cff")
process.load("Configuration.StandardSequences.MixingNoPileUp_cff")
process.load("Configuration.StandardSequences.VtxSmearedNoSmear_cff")

process.load("Configuration.StandardSequences.Generator_cff")
process.load("Configuration.StandardSequences.Simulation_cff")
process.load('Configuration.StandardSequences.Digi_cff')
process.load("Configuration.StandardSequences.DigiToRaw_cff")

process.load('Configuration.EventContent.EventContentCosmics_cff')


#--- random number generator

process.load('Configuration/StandardSequences/Services_cff')
process.RandomNumberGeneratorService.theSource.initialSeed = cms.untracked.uint32(12345647)

#--- non-collision events

process.g4SimHits.NonBeamEvent = cms.bool(True)
process.g4SimHits.Generator.ApplyEtaCuts = cms.bool(False)
process.psim = cms.Sequence(cms.SequencePlaceholder("randomEngineStateProducer")*process.g4SimHits)


#--- Cosmic Generator

process.load("GeneratorInterface.CosmicMuonGenerator.CMSCGENsource_cfi")
process.CosMuoGenSource.MinP = 10.
process.CosMuoGenSource.RadiusOfTarget = 1100.
process.CosMuoGenSource.ZDistOfTarget  = 3000.

#--- Conditions

process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag =  'COSMMC_BOFFV3::All'
process.prefer("GlobalTag")


#--------- Magnetic field Field should be ON for this sample

process.load("Configuration.StandardSequences.MagneticField_0T_cff")


#--------- Include L1 emulator

process.load('Configuration/StandardSequences/SimL1Emulator_cff')
process.load('L1Trigger.DTTrackFinder.dttfDigis_cfi')
process.dttfDigis.Open_LUTs = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_ME1a = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_ME1b = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_ME2  = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_ME3  = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_ME4  = True
process.simCsctfTrackDigis.SectorProcessor.trigger_on_MB1a = False
process.simCsctfTrackDigis.SectorProcessor.trigger_on_MB1d = False
process.simCsctfTrackDigis.SectorProcessor.singlesTrackPt  = cms.uint32(255)
process.simCsctfTrackDigis.SectorProcessor.singlesTrackOutput = cms.uint32(1)
process.simCsctfTrackDigis.useDT = cms.bool(False)


#-------- SPECIAL stuff for subsystems: use SelReadout

#                                                    
# Full-scale Digitization of the simulated hits      
# in all CMS subdets : Tracker, ECAL, HCAl, Muon's;  
# MixingModule (at least in zero-pileup mode) needs  
# to be included to make Digi's operational, since   
# it's required for ECAL/HCAL & Muon's                
# Defined in a separate fragment
#                                                    
# Tracker Digis (Pixel + SiStrips)
# returns sequence "trDigi"
#
from SimTracker.Configuration.SimTracker_cff import *

# Calorimetry Digis (Ecal + Hcal) - * unsuppressed *
# returns sequence "calDigi"
from SimCalorimetry.Configuration.SimCalorimetry_cff import *
# Muon Digis (CSC + DT + RPC)
# returns sequence "muonDigi"
#
from SimMuon.Configuration.SimMuon_cff import *
#
# include TrackingParticle Producer
# NOTA BENE: it MUST be run here at the moment, since it depends 
# of the availability of the CrossingFrame in the Event
#
from SimGeneral.Configuration.SimGeneral_cff import *

#Special parameterization for cosmics
simSiPixelDigis.TofLowerCut = cms.double(18.5)
simSiPixelDigis.TofUpperCut = cms.double(43.5)
simSiStripDigis.CosmicDelayShift = cms.untracked.double(31)

#### New ECAL without selective readout for EE
simEcalUnsuppressedDigis.cosmicsPhase = cms.bool(True)
simEcalUnsuppressedDigis.cosmicsShift = cms.double(1.)
EcalTrigPrimESProducer.DatabaseFile = cms.untracked.string("TPG_startup.txt.gz")
simEcalDigis.ebDccAdcToGeV = cms.double(0.035)
simEcalDigis.ecalDccZs1stSample = cms.int32(3)
simEcalDigis.dccNormalizedWeights = cms.vdouble(-1.1865, 0.0195, 0.2900, 0.3477, 0.3008, 0.2266)
simEcalDigis.srpBarrelLowInterestChannelZS = cms.double(3*0.035)   
simEcalDigis.srpEndcapLowInterestChannelZS = cms.double(3*0.06)                             
simEcalDigis.srpEndcapHighInterestChannelZS = cms.double(3*0.06)

simHcalDigis.HBlevel = cms.int32(-10000)
simHcalDigis.HElevel = cms.int32(-10000)
simHcalDigis.HOlevel   = cms.int32(-10000)
simHcalDigis.HFlevel   = cms.int32(-10000)

doAllDigi = cms.Sequence(trDigi+calDigi+muonDigi)
pdigi = cms.Sequence(cms.SequencePlaceholder("randomEngineStateProducer")*cms.SequencePlaceholder("mix")*doAllDigi*trackingParticles)


###----------------------------------


#--------- Processes and output

process.output = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('CosmicMC_BOFF_10GeV_TKOnly.root'),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RAW'),
        filterName = cms.untracked.string('')
    )
                                  )


#---------------------------------------
# paths and sequences
#---------------------------------------
process.p0 = cms.Path(process.pgen)
process.p1 = cms.Path(process.psim)
process.p2 = cms.Path(process.pdigi)
process.p3 = cms.Path(process.SimL1Emulator)
process.p4 = cms.Path(process.DigiToRaw)
process.outpath = cms.EndPath(process.output)


process.schedule = cms.Schedule(process.p0,process.p1,process.p2,process.p3,process.p4,process.outpath)
