import os
import sys
import argparse
import numpy as np 
import itertools
from glob import glob
from tqdm import tqdm
import stat

opr = {
    'cHDD':[-20,20],
    'cHWB':[-20,20], 
    'cHW':[-30,30], 
    'cHbox':[-20,20], 
    'cHl1':[-50,50], 
    'cHl3':[-30,30], 
    'cHq1':[-30,30], 
    'cHq3':[-30,30], 
    'cW':[-30,30], 
    'cll1':[-30,30], 
    'cll':[-70,70], 
    'cqq11':[-30,30], 
    'cqq1':[-30,30], 
    'cqq31':[-30,30], 
    'cqq3':[-30,30]
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
    f.write('      #for model in [{}]:\n'.format(",".join("\"{}\"".format(i) for i in models)))
    f.write('      #print("[INFO] Running for op: {}, model: {}".format(op, model))\n')
    f.write('      os.chdir(dir)\n')
    f.write('      os.system("bash t2w.sh")\n')

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
    f.write('      #for model in [{}]:\n'.format(",".join("\"{}\"".format(i) for i in models)))
    f.write('         #print("[INFO] Running for op: {}, model: {}".format(op, model))\n')
    f.write('      os.chdir(dir )\n')
    f.write('      os.system("bash fit.sh")\n')

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)


def makeExecRunt(model, variables, ops, outdir, tag):
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
        f.write("cd {}/{}\n".format(model,var))
        to_w = "text2workspace.py  {}.txt  -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCoupling{}:analiticAnomalousCoupling{}  -o   model.root \
        --X-allow-no-signal --PO eftOperators={}".format(tag, mod, mod, ",".join(op for op in ops))        
        if "alt" in model: to_w += " --PO  eftAlternative"
        
        to_w += "\n"
        f.write(to_w)
        f.write("cd ../..\n\n\n")

    f.close()
    #convert to executable
    st = os.stat(file_name)
    os.chmod(file_name, st.st_mode | stat.S_IEXEC)


def combineCards(processes, variables):
    t = "combineCards.py"
    for proc, v in zip(processes, variables):
        t += " {}_{}=datacard_{}.txt".format(proc, v, proc)

    t += " > datacard.txt"
    return t



def makeExecRunc(variables, ops, outdir ):
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
        f.write("cd {}/{}\n".format(model, var))
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser for model testing')
    parser.add_argument('--cfg',     dest='cfg',     help='the config file', required = True)
    args = parser.parse_args()

    combinations = {}
    output = {}

    execfile(args.cfg)

    all_dict = {}
    variables = {}

    print(" @ @ @ Retrieving shapes and datacards @ @ @")
    
    #retrieve files and shapes
    for process in tqdm(combinations.keys()):


        subf = glob(combinations[process]["folder"] + "/" + combinations[process]["prefix"] + "*/")
        all_dict[process] = {}

        for s in subf:

            op = (s.split("/")[-2])
            op = op.split(combinations[process]["prefix"])[-1]
            op = op.split(process + "_")[-1]
             
            if op in combinations[process]["ignore_ops"]: continue
            
              
            if op not in variables.keys() : 
                if "_".join(i for i in  op.split("_")[::-1]) in variables.keys():
                  op = "_".join(i for i in  op.split("_")[::-1])
                else:
                  variables[op] = {}
            if process not in  variables[op].keys():
                variables[op][process] = []

            all_dict[process][op] = {}

            for model in combinations[process]["models"]:
                all_dict[process][op][model] = {}

                for var in glob(s + "/" + model + "/datacards/*/*"):

                    v = var.split("/")[-1]
                    if v in combinations[process]["ignore_vars"]:  continue
                    if combinations[process]["vars"] != '*':
                        if v not in combinations[process]["vars"] : continue

                    if v not in variables[op][process]:
                        variables[op][process].append(v)
                    all_dict[process][op][model][v] = {}
                    all_dict[process][op][model][v]['datacard'] = glob(var + "/{}.txt".format(combinations[process]["datacard_tag"]))[0]
                    all_dict[process][op][model][v]['shapes'] = glob(var + "/shapes/*.root")[0]


    #find common operators
    processes = combinations.keys()
    common_ops = []
    
    for i,op in enumerate(variables.keys()):
        proc = variables[op].keys()
        if all(i in proc for i in processes): common_ops.append(op) 
    
    print(" @ @ @ Making vars combo @ @ @")

    global_path = os.getcwd()
    out = output["name"]
    prefix = output["prefix"]
    models = output["models"]

    mkdir(out)

    for op in tqdm(common_ops):
        cp = out + "/" + prefix + "_" + "_".join(p for p in processes) + "_" + op
        bash_scripts = cp
        mkdir(cp)
        makeActivations(out, models, prefix + "_" + "_".join(p for p in processes) + "_")
        
        var_comb = list(itertools.product(*(variables[op].values())))  
        
        for model in models:
            cp = out + "/" + prefix + "_" + "_".join(p for p in processes) + "_" + op + "/" + model
            mkdir(cp)
            cp = out + "/" + prefix + "_" + "_".join(p for p in processes) + "_" + op + "/" + model + "/datacards"
            mkdir(cp)
            cp = out + "/" + prefix + "_" + "_".join(p for p in processes) + "_" + op + "/" + model + "/datacards" + "/" + "_".join(p for p in processes) + "_" + op
            mkdir(cp)
            var_fol_name = []

            for wc in var_comb:
                var_name = "_".join(w for w in wc)
                mkdir(cp + "/" + var_name)
                mkdir(cp + "/" + var_name + "/shapes/")


                for process_, v in zip(variables[op].keys(), wc):
                    
                    os.system("cp {} {}/datacard_{}.txt".format(os.path.abspath(all_dict[process_][op][model][v]['datacard']), cp + "/" + var_name, process_))
                    os.system("cp {} {}".format(os.path.abspath(all_dict[process_][op][model][v]['shapes']), cp + "/" + var_name + "/shapes/"))

                var_fol_name.append(var_name)
                os.chdir(cp + "/" + var_name)
                combine_text = combineCards(variables[op].keys(), wc)
                os.system(combine_text)

                for process_ in processes:
                    os.system("rm datacard_{}.txt".format(process_))

                os.chdir(global_path)

            makeExecRunt(model, var_fol_name, op.split("_"), bash_scripts, "datacard")
            makeExecRunc(var_fol_name, op.split("_"), bash_scripts)
