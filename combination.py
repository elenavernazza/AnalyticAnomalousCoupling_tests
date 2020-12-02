import os
import sys
import argparse
import numpy as np 
import itertools
from glob import glob
from tqdm import tqdm
import stat

opr = {
    'cW': [-2,2],
    'cHWB': [-20,20],
    'cHl3' : [-1,1],
    'cHq1':[-2,2],
    'cHq3': [-0.5,0.5],
    'cll1': [-0.5,0.5],
    'cHbox': [-10,20],
    'cHDD' : [-20,20], 
    'cHl1' : [-25,25], 
    'cHW': [-10,5]  ,    
    'cqq11': [-1,1]  ,     
    'cqq1' : [-1,1] ,  
    'cqq31':  [-1,1] ,   
    'cqq3':  [-1,1] ,   
    'cll':   [-70,70]   
}

def makeActivations(outdir, models, prefix):
    
    #Activation of t2w:
    file_name = outdir + "/runt.py"
    f = open(file_name, 'w')

    f.write("#!/usr/bin/env python\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDCInputs.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('from glob import glob\n')
    f.write('import os\n')

    f.write('if __name__ == "__main__":\n')
    f.write('   base_dir = os.getcwd()\n')
    f.write('   for dir in glob(base_dir + "/*/"):\n')
    f.write('      process = dir.split("/")[-2]\n')
    f.write('      op = process.split("{}")[1]\n'.format(prefix))
    f.write('      process = process.split(op)[0]\n')
    f.write('      for model in [{}]:\n'.format(",".join("\"{}\"".format(i) for i in models)))
    f.write('         print("[INFO] Running for op: {}, model: {}".format(op, model))\n')
    f.write('         os.chdir(dir + "/" + model)\n')
    f.write('         os.system("bash t2w.sh")\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

    #Activation of fit.sh:
    file_name = outdir + "/runc.py"
    f = open(file_name, 'w')

    f.write("#!/usr/bin/env python\n\n")
    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDCInputs.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    f.write('from glob import glob\n')
    f.write('import os\n')

    f.write('if __name__ == "__main__":\n')
    f.write('   base_dir = os.getcwd()\n')
    f.write('   for dir in glob(base_dir + "/*/"):\n')
    f.write('      process = dir.split("/")[-2]\n')
    f.write('      op = process.split("{}")[1]\n'.format(prefix))
    f.write('      process = process.split(op)[0]\n')
    f.write('      for model in [{}]:\n'.format(",".join("\"{}\"".format(i) for i in models)))
    f.write('         print("[INFO] Running for op: {}, model: {}".format(op, model))\n')
    f.write('         os.chdir(dir + "/" + model)\n')
    f.write('         os.system("bash fit.sh")\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)


def makeExecRunt(model, variables, ops, outdir,proc, tag):
    #creates an executable to create binary workspaces after running mkDatacards.py

    modeltot2w = {
        "EFT": "EFT",
        "EFTNeg": "EFTNegative",
        "EFTNeg-alt": "EFTNegative"
    }

    mod = modeltot2w[model]

    file_name = outdir + "/t2w.sh"
    f = open(file_name, 'w')

    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDCInputs.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    for var in variables:
        f.write("#-----------------------------------\n")
        f.write("cd datacards/{}/{}\n".format(proc,var))
        to_w = "text2workspace.py  {}.txt  -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCoupling{}:analiticAnomalousCoupling{}  -o   model.root \
        --X-allow-no-signal --PO eftOperators={}".format(tag, mod, mod, ",".join(op for op in ops))        
        if "alt" in model: to_w += " --PO  eftAlternative"
        
        to_w += "\n"
        f.write(to_w)
        f.write("cd ../../..\n\n\n")

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)



def makeExecRunc(variables, ops, outdir, proc ):
    #creates an executable to fit binary workspaces after running mkDatacards.py

    ranges = ":".join("k_"+op+"={},{}".format(opr[op][0],opr[op][1]) for op in ops)


    file_name = outdir + "/fit.sh"
    f = open(file_name, 'w')

    f.write("#-----------------------------------\n")
    f.write("#     Automatically generated       # \n")
    f.write("#        by mkDCInputs.py           # \n")
    f.write("#-----------------------------------\n")
    f.write("\n\n\n")

    for var in variables:
        f.write("#-----------------------------------\n")
        f.write("cd datacards/{}/{}\n".format(proc, var))
        to_w = "combine -M MultiDimFit model.root  --algo=grid --points 5000  -m 125   -t -1   --robustFit=1 --X-rtd FITTER_NEW_CROSSING_ALGO --X-rtd FITTER_NEVER_GIVE_UP --X-rtd FITTER_BOUND --redefineSignalPOIs {}     --freezeParameters r      --setParameters r=1    --setParameterRanges {}  --verbose -1".format(",".join("k_"+op for op in ops), ranges)
        to_w += "\n"
        f.write(to_w)
        f.write("cd ../../..\n\n\n")

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)

def mkdir(dir_name):
    try:
        os.mkdir(dir_name)
    except:
        print("dir already present")

    return 


parser = argparse.ArgumentParser(description='Command line parser for model testing')
parser.add_argument('--inFolders',     dest='inFolders',     help='comma separated list of folders output of mkDatacard', required = True)
parser.add_argument('--keys',     dest='keys',     help='comma separated list of keys for each folder output of mkDatacard', required = False, default="proc1,proc2")
parser.add_argument('--prefix',     dest='prefix',     help='comma separated list of prefix of same len of folder list', required = True)
parser.add_argument('--models',     dest='models',     help='comma separated list of models name', required = False, default="EFT,EFTNeg,EFTNeg-alt")
parser.add_argument('--do',     dest='do',     help='name .txt of the datacards coimbined', required = False, default="tot")
parser.add_argument('--ig_op',     dest='ig_op',     help='comma separated list of operators you want to ignore', required = False, default = "")
parser.add_argument('--ig_var',     dest='ig_var',     help='comma separated list of variables you want to ignore', required = False, default = "")
parser.add_argument('--out',     dest='out',     help='output folder name', required = False, default="combination_results")
parser.add_argument('--outPrefix',     dest='outPrefix',     help='output prefix name, default = none', required = False, default="")
parser.add_argument('--inputDtag',     dest='inputDtag',     help='Name of process - wise datacards, all datacard must have the same name for each process. No .txt as final', required = False, default="*,*")

args = parser.parse_args()

mkdir(args.out)

processes = args.inFolders.split(',')
prefixes = args.prefix.split(',')
models = args.models.split(',')
ig_op = args.ig_op.split(',')
ig_var = args.ig_var.split(',')
keys = args.keys.split(',')
tags = args.inputDtag.split(',')

if len(processes) != 2: sys.exit("AAAAH you can't do that yet... you greedy man")

all_dict = {}

variables = {}

print(" @ @ @ Retrieving shapes and datacards @ @ @")

for fol, prefix, k, tag in tqdm(zip(processes, prefixes, keys, tags)):
    subf = glob(fol + "/" + prefix + "*/")
    all_dict[k] = {}
    variables[k] = []

    for s in subf:
        op = (s.split("/")[-2]).split("_")[-1]
        if op in ig_op: continue
        proc = (s.split("/")[-2]).split("_")[-2]
        all_dict[k][op] = {}

        for model in models:
            all_dict[k][op][model] = {}

            for var in glob(s + "/" + model + "/datacards/*/*"):
                v = var.split("/")[-1]
                if v in ig_var: continue
                if v not in variables[k]:
                    variables[k].append(v)
                all_dict[k][op][model][v] = {}
                all_dict[k][op][model][v]['datacard'] = glob(var + "/{}.txt".format(tag))[0]
                all_dict[k][op][model][v]['shapes'] = glob(var + "/shapes/*.root")

print(" @ @ @ Making vars combo @ @ @")

global_path = os.getcwd()
outprefix = args.outPrefix

key1 = all_dict.keys()[0]
key2 = all_dict.keys()[1]
key3 = args.do

fp = all_dict[key1]
sp = all_dict[key2]

ops1 = np.array(fp.keys())
ops2 = np.array(sp.keys())

mask = np.isin(ops1, ops2)
commonops = ops1[mask]

v1 = variables[variables.keys()[0]] #first process with its ops
v2 = variables[variables.keys()[1]] #second process with its ops

var_comb = list(itertools.product(v1,v2)) # [(1st p var, 2nd p var), ... ]

for op in tqdm(commonops):
    cp = args.out + "/" + outprefix + key1 + "_" + key2 + "_" + op
    mkdir(cp)

    makeActivations(args.out, models, outprefix + key1 + "_" + key2 + "_")

    for model in models:
        cp = args.out + "/" + outprefix + key1 + "_" + key2 + "_" + op + "/" + model
        mkdir(cp)
        cp = args.out + "/" + outprefix + key1 + "_" + key2 + "_" + op + "/" + model + "/datacards/"
        mkdir(cp)
        cp = args.out + "/" + outprefix + key1 + "_" + key2 + "_" + op + "/" + model + "/datacards/" + key1 + "_" + key2
        mkdir(cp)

        var_fol_name = []
        for wc in var_comb:
            path_1_dat = all_dict[key1][op][model][wc[0]]['datacard']
            path_2_dat = all_dict[key2][op][model][wc[1]]['datacard']

            shapes_1 = all_dict[key1][op][model][wc[0]]['shapes']
            shapes_2 = all_dict[key2][op][model][wc[1]]['shapes']

            path_1_dat = os.path.abspath(path_1_dat)
            path_2_dat = os.path.abspath(path_2_dat)
            shapes_1 = [os.path.abspath(i) for i in shapes_1]
            shapes_2 = [os.path.abspath(i) for i in  shapes_2]

            cp = args.out + "/" + outprefix + key1 + "_" + key2 + "_" + op + "/" + model
            
            mkdir(cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}".format(wc[0], wc[1]))
            mkdir(cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}/shapes/".format(wc[0], wc[1]))
            os.system("cp {} {}/datacard_{}.txt".format(path_1_dat, cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}".format(wc[0], wc[1]), key1))
            os.system("cp {} {}/datacard_{}.txt".format(path_2_dat, cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}".format(wc[0], wc[1]), key2))

            for sh_idx in range(len(shapes_1)):
                os.system("cp {} {}".format(shapes_1[sh_idx], cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}/shapes/".format(wc[0], wc[1])))
            for sh_idx in range(len(shapes_2)):
                os.system("cp {} {}".format(shapes_2[sh_idx], cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}/shapes/".format(wc[0], wc[1])))

            var_fol_name.append("{}_{}".format(wc[0], wc[1])) 
            
            os.chdir(cp + "/datacards/" + key1 + "_" + key2 + "/{}_{}".format(wc[0], wc[1]))

            os.system("combineCards.py datacard_{}.txt datacard_{}.txt > datacard_{}.txt".format(key1, key2, key3))
            
            os.chdir(global_path)

        makeExecRunt(model, var_fol_name, [op], cp, key1 + "_" + key2, "datacard_{}.txt".format(key3))
        makeExecRunc(var_fol_name, [op], cp, key1 + "_" + key2)


print("@ @ @ Generated every combined card @ @ @")    