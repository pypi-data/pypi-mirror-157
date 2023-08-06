from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

from copy import copy
import tqdm


class physSpectrum:
    
    def __init__(self, pathToInputDF, primParticleType, nBins=60, trackType="all"):
        
        primEnergyLimits = {"proton":{"min":0.1,"max":100},
                           "electron":{"min":0.1,"max":8}}
        
        primaryEnergyLimitNormFactor = primEnergyLimits[primParticleType]["max"] - \
                                       primEnergyLimits[primParticleType]["min"]
        
        if type(pathToInputDF) == str:
            fullInputDF = pd.read_csv(pathToInputDF,delimiter=",").sort_values(["eventID","trackID"])
        else:
            fullInputDF = pathToInputDF.sort_values(["eventID","trackID"])
        
        self.trackType = trackType
        
        if trackType == "primary":
            inputDF = fullInputDF[fullInputDF["trackID"] == 1]
        elif trackType == "secondary":
            inputDF = fullInputDF[fullInputDF["trackID"] > 1]
        else:
            inputDF = fullInputDF
            
            self.primaryOnlySpectrum = physSpectrum(inputDF,primParticleType,trackType="primary")
            self.secondaryOnlySpectrum = physSpectrum(inputDF,primParticleType,trackType="secondary")
        
        primPEnergies = inputDF["primaryPkinEn/MeV"]
        
        totalPrimaryNumber = inputDF["eventID"].tail(1).iloc[0]

        lowEnergy = (0.8) * primPEnergies.min()
        highEnergy = (1.2) * primPEnergies.max()

        binList = np.linspace(lowEnergy,highEnergy,nBins+1)
        histogramValuesRaw = np.transpose([binList[:-1],binList[1:],np.zeros(nBins)])
        stdValuesRaw = np.transpose([binList[:-1],binList[1:],np.zeros(nBins)])

        previousTrackNumber = 0
        currentTrackNumber = 0
        previousEventID = 0
        currentEventID = 0
        
        for index,row in inputDF.iterrows():
            #print(row)
            primPEnergy = row["primaryPkinEn/MeV"]
            particleCharge = row["particleCharge"]
            currentTrackNumber = row["trackID"]
            currentEventID = row["eventID"]
    
            binIndex = np.where((histogramValuesRaw[:,0] <= primPEnergy) * \
                                (histogramValuesRaw[:,1] > primPEnergy))[0][0]
        
            if (currentTrackNumber != previousTrackNumber) and (currentEventID != previousEventID):
                netCharge = 0.0
    
            if row["IsFirstStepInVol"] == True:
                histogramValuesRaw[binIndex,2] += particleCharge
                netCharge += particleCharge
            elif row["IsLastStepInVol"] == True:
                histogramValuesRaw[binIndex,2] -= particleCharge
                netCharge -= particleCharge
            else:
                raise ValueError("row was neither first or last step, unsure how to handle this.")
            
            if netCharge**2 < 0.01**2:
                stdValuesRaw[binIndex,2] = np.sqrt((stdValuesRaw[binIndex,2]**2) + (particleCharge**2))
                
            previousTrackNumber = currentTrackNumber
            previousEventID = currentEventID
                
        self.histogramValues = histogramValuesRaw
        binDiffValues = self.histogramValues[1:,0] - self.histogramValues[:-1,0]
        binDiffValues = np.append(binDiffValues,binDiffValues[-1])
    
        self.histogramValues[:,2] = (self.histogramValues[:,2] * primaryEnergyLimitNormFactor)/ \
                                    (binDiffValues * totalPrimaryNumber) #normalising per incoming particle
        self.histogramUnits = "mean deposited charge / primary\n(elementary charge units)"
        self.xunits = "primary particle kinetic energy (MeV)"
        
        self.stdValues = stdValuesRaw
        self.stdValues[:,2] = (stdValuesRaw[:,2]* primaryEnergyLimitNormFactor)/ \
                              (binDiffValues * totalPrimaryNumber)
        
        print("charge spectrum successfully created, with totalPrimaryNumber =",totalPrimaryNumber)
        
    def plot(self,specLabel=None,plotSubSpectra=False,plotStd=True,**xargs):

        if specLabel is not None:
            labelToUse = specLabel
        else:
            labelToUse = "Total"
        
        if (self.trackType=="all") and (plotStd==True):
            plt.fill_between(self.histogramValues[:,0],
                 self.histogramValues[:,2]+self.stdValues[:,2],
                 self.histogramValues[:,2]-self.stdValues[:,2],
                 step="pre",
                 alpha=0.3)
            plt.step(self.histogramValues[:,0],self.histogramValues[:,2],where="pre",label=labelToUse,**xargs)
        elif plotStd is not True:
            plt.step(self.histogramValues[:,0],self.histogramValues[:,2],where="pre",label=labelToUse,**xargs)
        else:
            plt.step(self.histogramValues[:,0],self.histogramValues[:,2],where="pre",**xargs)
        plt.grid(True)
        
        plt.gca().set_xlim(left=0)
        
        if plotSubSpectra == True:
            self.primaryOnlySpectrum.plot(label="primaries")
            self.secondaryOnlySpectrum.plot(label="secondaries")
        
        plt.xlabel(self.xunits)
        plt.ylabel(self.histogramUnits)
        
    def evaluate(self, x):
        
        if sum(np.where(self.histogramValues[:,0] < x)[0]) == 0:
            outputValue = 0.0
            outputStd = 0.0
            
        else:
        
            binToUse = np.where(self.histogramValues[:,0] < x)[0][-1]
        
            outputValue = self.histogramValues[binToUse,2]
            outputStd = self.stdValues[binToUse,2]
        
        return outputValue,outputStd
        
    def __add__(self,right):
        
        outputChargeSpectrum = copy.deepcopy(self)
        
        outputChargeSpectrum.histogramValues[:,2] = self.histogramValues[:,2] + right.histogramValues[:,2]
        outputChargeSpectrum.stdValues[:,2] = np.sqrt((self.stdValues[:,2]**2) + (right.stdValues[:,2]**2))
        
        if self.trackType == "all":
            outputChargeSpectrum.primaryOnlySpectrum = self.primaryOnlySpectrum + right.primaryOnlySpectrum
            outputChargeSpectrum.secondaryOnlySpectrum = self.secondaryOnlySpectrum + right.secondaryOnlySpectrum
        
        return outputChargeSpectrum
        
    def __sub__(self,right):
        
        outputChargeSpectrum = copy.deepcopy(self)
        
        outputChargeSpectrum.histogramValues[:,2] = self.histogramValues[:,2] - right.histogramValues[:,2]
        outputChargeSpectrum.stdValues[:,2] = np.sqrt((self.stdValues[:,2]**2) + (right.stdValues[:,2]**2))
        print(self.stdValues[:,2]**2)
        
        if self.trackType == "all":
            outputChargeSpectrum.primaryOnlySpectrum = self.primaryOnlySpectrum - right.primaryOnlySpectrum
            outputChargeSpectrum.secondaryOnlySpectrum = self.secondaryOnlySpectrum - right.secondaryOnlySpectrum
        
        return outputChargeSpectrum
    
    def __mul__(self,right):
        
        outputChargeSpectrum = copy.deepcopy(self)
        
        outputChargeSpectrum.histogramValues[:,2] = self.histogramValues[:,2] * right
        outputChargeSpectrum.stdValues[:,2] = self.stdValues[:,2] * right
        
        if self.trackType == "all":
            outputChargeSpectrum.primaryOnlySpectrum = self.primaryOnlySpectrum * right
            outputChargeSpectrum.secondaryOnlySpectrum = self.secondaryOnlySpectrum * right
        
        return outputChargeSpectrum
    
    __rmul__ = __mul__
    
    def convolveFluxAndResponseMatrix(self, inputFluxDF):
        
        outputCurrentPrediction = copy.deepcopy(self)
        
        ####################
    
        relevantFluxColumns = inputFluxDF.columns[2:]
        deltaEnergies = np.append(relevantFluxColumns[1:] - relevantFluxColumns[:-1],relevantFluxColumns[-1])
        print(deltaEnergies)
    
        for inputResponseSpec in [outputCurrentPrediction, 
                                  outputCurrentPrediction.primaryOnlySpectrum, 
                                  outputCurrentPrediction.secondaryOnlySpectrum]:
            
            ResponseArray = [inputResponseSpec.evaluate(x)[0] for x in relevantFluxColumns]
            stdErrResponseArray = [inputResponseSpec.evaluate(x)[1] for x in relevantFluxColumns]
        
            OutputIntegralSeries = (inputFluxDF[relevantFluxColumns] * ResponseArray * deltaEnergies).sum(axis=1)
            OutputIntegralErrorSeries = (inputFluxDF[relevantFluxColumns] * stdErrResponseArray * deltaEnergies).sum(axis=1)
            
            OutputIntegralDF = pd.concat([inputFluxDF["L"],
                                          inputFluxDF["L"],
                                          OutputIntegralSeries],axis=1)
            OutputIntegralDFError = pd.concat([inputFluxDF["L"],
                                          inputFluxDF["L"],
                                          inputFluxDF["L"],
                                          OutputIntegralErrorSeries],axis=1)
            
            inputResponseSpec.histogramValues = OutputIntegralDF.to_numpy()
            inputResponseSpec.stdValues = OutputIntegralDFError.to_numpy()
            inputResponseSpec.xunits = "L value"
            inputResponseSpec.histogramUnits = "current"
            #OutputIntegralDF.columns = ["L","Current"]
            
        print(outputCurrentPrediction.histogramValues)
    
        return outputCurrentPrediction

    def rebin(self, nbins, parentRun=True):
        outputSpectra = copy.deepcopy(self)

        initialXValues = self.histogramValues[:,0]
        initialCountRate = self.histogramValues[:,2]
        initialStd = self.stdValues[:,2]

        initialDataDF = pd.DataFrame(np.transpose([initialXValues,initialCountRate,initialStd]),
                                    columns=["xValues","yValues","yStd"])

        newXBins = np.linspace(min(initialXValues),max(initialXValues),nbins)
        initialDataDF["newBinLabels"] = np.digitize(initialXValues,newXBins)

        def meanInQuadrature(inputSeries):
            values = inputSeries.values
            squaredValues = values**2

            numberOfValues = len(values)
            return np.sqrt(sum(squaredValues))/numberOfValues

        def addInQuadrature(inputSeries):
            values = inputSeries.values
            squaredValues = values**2

            numberOfValues = len(values)
            return np.sqrt(sum(squaredValues)/numberOfValues)

        aggDF = initialDataDF.groupby("newBinLabels").agg({"xValues":"mean","yValues":"mean","yStd":addInQuadrature})

        outputSpectra.histogramValues = aggDF[["xValues","xValues","yValues"]].to_numpy()
        outputSpectra.stdValues = aggDF[["xValues","xValues","yStd"]].to_numpy()

        if parentRun == True:
            try:
                outputSpectra.primaryOnlySpectrum = outputSpectra.primaryOnlySpectrum.rebin(nbins,parentRun=False)
            except:
                pass

            try:
                outputSpectra.secondaryOnlySpectrum = outputSpectra.secondaryOnlySpectrum.rebin(nbins,parentRun=False)
            except:
                pass

        return outputSpectra

    def rebin2(self, nbins):
        outputSpectra = copy.deepcopy(self)

        initialXValues = self.histogramValues[:,0]
        initialCountRate = self.histogramValues[:,1]
        initialStd = self.histogramValues[:,1]

        newEnergyBins = np.linspace(min(initialXValues),max(initialXValues),nbins)
        newBinsToAddTo = np.digitize(initialXValues,newEnergyBins)

        newValuesList = []
        for index,xValue in tqdm.tqdm(enumerate(newEnergyBins)):
            
            newValue = np.mean(initialCountRate[newBinsToAddTo == index])
            newStd = np.sqrt(np.sum((initialStd**2)[newBinsToAddTo == index]))/sum(newBinsToAddTo == index)
            newValuesList = [xValue, newValue, newStd]

        outputSpectra.histogramValues = np.array(newValuesList)

        try:
            outputSpectra.primaryOnlySpectrum = outputSpectra.primaryOnlySpectrum.rebin(nbins)
        except:
            pass

        try:
            outputSpectra.secondaryOnlySpectrum = outputSpectra.secondaryOnlySpectrum.rebin(nbins)
        except:
            pass

        return outputSpectra
