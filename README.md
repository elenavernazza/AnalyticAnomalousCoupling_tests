# AnalyticAnomalousCoupling_tests
Tests scripts for the AnalyticAnomalousCoupling combine model

# AnalyticAnomalousCoupling

Install:

    cmsrel CMSSW_10_2_13
    cd CMSSW_10_2_13/src
    cmsenv
    git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
    cd HiggsAnalysis/
    git clone git@github.com:amassiro/AnalyticAnomalousCoupling.git
 
Where:

    /afs/cern.ch/user/a/amassiro/work/Latinos/Framework/AnalyticAnomalousCoupling/CMSSW_10_2_13/src/HiggsAnalysis/AnalyticAnomalousCoupling
    

    
This repo contains packages to test the AnalyticAnomalousCoupling and plotting the comparison.
Downlaod this repo and place all of its content inside the `AnalyticAnomalousCoupling/test` folder.
Run `bash run.sh` to generate comparison plots for various scenarios and for all the three models
