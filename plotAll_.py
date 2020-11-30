import glob
import sys
import os

if __name__ == "__main__":

    if len(sys.argv) < 2: sys.exit("Provide target directory")
    target = sys.argv[1]

    t_prefix = "to_Latinos_"
    if len(sys.argv) > 2:
        t_prefix = sys.argv[2]

    outpath = "prova/"
    os.mkdir(outpath)

    all_of = glob.glob(target + "/*/")

    for folder in all_of:
        print(folder)
        op = "k_"+ ((folder.split("/")[-2]).split(t_prefix)[1]).split("_")[1]
        os.mkdir(outpath + "/" + folder.split("/")[-2])
        p = (folder.split("/")[-2]).split(t_prefix)[1]
        for var in  ['met','mjj','mll','phij1','phij2','ptj1','ptj2','ptl1','ptl2','ptll','deltaetajj','deltaphijj','etaj1','etaj2','etal1','etal2']:
        
            os.system("python plot.py --inFiles {folder}/EFT/datacards/{prefix_}/{var_}/higgsCombineTest.MultiDimFit.mH125.root,{folder}/EFTNeg/datacards/{prefix_}/{var_}/higgsCombineTest.MultiDimFit.mH125.root,{folder}/EFTNeg-alt/datacards/{prefix_}/{var_}/higgsCombineTest.MultiDimFit.mH125.root \
            --ops {ops} --labels {ops} --leg EFT,EFTNeg,EFTNeg-alt --legtit {var_} --outFolder {of} --outFile {var_}.png --lumi '100 fb-1'".format(folder = folder, prefix_ = p, var_ = var, ops = op, of = outpath + "/" + folder.split("/")[-2]))