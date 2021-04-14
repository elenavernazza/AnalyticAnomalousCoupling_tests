#!/usr/bin/env python
import os
import sys
from glob import glob
#from configparser import ConfigParser
import numpy as np
import stat

opr = {
    'cW': [-1,1],
    'cHWB': [-10,10],
    'cHl3' : [-20,20],
    'cHq1':[-5,5],
    'cHq3': [-3,3],
    'cll1': [-20,20],
    'cHbox': [-25,25],
    'cHDD' : [-10,10], 
    'cHl1' : [-20,20], 
    'cHW': [-8,8]  ,    
    'cqq11': [-2,2]  ,     
    'cqq1' : [-2,2] ,  
    'cqq31':  [-2,2] ,   
    'cqq3':  [-1,1] ,   
    'cll':   [-20,20]   
}

def redemensionOpinput(config):
    sample = config.getlist("general", "sample")
    ops = config.getlist("eft", "operators")

    ops = [i[1:-1].split(":") for i in ops]
    ops = [list(map(str, sublist)) for sublist in ops]

    if len(sample) > len(ops) and len(ops) == 1:
        return ops*len(samples)

    elif len(sample) > len(ops) and len(ops) == 1:
        sys.exit("[ERROR] Ambiguity in the definition of samples and op per sample")
    
    else:
        return ops

def createOpRange(config):

    if not config.has_option("eft", "fitranges"): 
        all_ops = np.unique([item for subs in redemensionOpinput(config) for item in subs])
        return dict((i, [-10,10]) for i in all_ops)
    
    else:
        or_ = config.getlist("eft", "fitranges")
        return dict( (i.split(":")[0], [ float(i.split(":")[1]) , float(i.split(":")[2]) ] ) for i in or_ )

def makeSubmit(outdir, npoints):

    file_name = outdir + "/submit.sh"
    f = open(file_name, 'w')

    f.write("#!/bin/sh\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDatacard.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    f.write('cd $1\n')
    f.write('eval `scram run -sh`\n')
    f.write('cd -\n')
    f.write('cp -r $1 ./\n')
    f.write('text2workspace.py  $1/datacard.txt  -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCouplingEFTNegative:analiticAnomalousCouplingEFTNegative -o combined.root --X-allow-no-signal --PO eftOperators=$3\n')
    f.write('#-----------------------------------\n')
    f.write('combine -M MultiDimFit combined.root --algo=grid --points $2 -m 125 -t -1 --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs k_$3 --freezeParameters r --setParameters r=1 --setParameterRanges k_$3=$4,$5 --verbose -1\n')
    f.write('cp combined.root $1\n')
    f.write('cp higgsCombineTest.MultiDimFit.mH125.root $1\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

    file_name_1 = outdir + "/submit.sub"
    f1 = open(file_name_1, 'w')

    f1.write('Universe    = vanilla\n')
    f1.write('Executable  = submit.sh\n')
    f1.write('arguments   = $(dir) {} $(op1) $(min_op1) $(max_op1)\n'.format(npoints))
    f1.write('output      = $(dir)/submit.out\n')
    f1.write('error       = $(dir)/submit.err\n')
    f1.write('log         = $(dir)/submit.log\n')
    f1.write('queue dir,op1,min_op1,max_op1 from list.txt\n')
    f1.write('+JobFlavour = "espresso"\n')

    f1.close()
    #convert to executable
    st = os.stat(file_name_1)
    os.chmod(file_name_1, st.st_mode | stat.S_IEXEC)


if __name__ == "__main__":

    if len(sys.argv) < 4: sys.exit("[ERROR] Provide folder path, prefix, process name, [npoints = 20000], [models = EFTNeg], [flavour = microcentury], [floatOtherPOI = 0], [ pois = Default ] after running mkDatacards.py ...")

    outputFolder = os.getcwd() + "/" + sys.argv[1]
    print(outputFolder)
    subf = glob(os.getcwd() + "/" + sys.argv[1] + "/*/")
    prefix = sys.argv[2]
    process = sys.argv[3]
    npoints = 20000
    model = "EFTNeg"
    flavour = "espresso"
    floatOtherPOI = 0
    pois = None
    if len(sys.argv) > 4:
        npoints = sys.argv[4]
    if len(sys.argv) > 5:
        models = sys.argv[5].split(",")
    if len(sys.argv) > 6:
        flavour = sys.argv[6]
    if len(sys.argv) > 7:
        floatOtherPOI = sys.argv[7]
    if len(sys.argv) > 8:
        pois = sys.argv[8].split(",")

    all_sub_paths = []

    makeSubmit(outputFolder, npoints)
    l = open(outputFolder + "/list.txt", 'w')

    print(". . . @ @ @ Retrieving folders @ @ @ . . .")
    
    for s in subf:
        subfolder = s.split("/")[-2]
        prc = subfolder.split(prefix + "_")[-1]
        op_ = prc.split(process + "_")[-1]
        vars_ = glob(s + model + "/datacards/" + prc + "/*/")
        for var_ in vars_:
            print(var_)
            l.write('{} {} {} {}\n'.format(var_, op_, opr[op_][0], opr[op_][1]))

    l.close()

    print(". . . @ @ @ Done @ @ @ . . .")
