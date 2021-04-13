#python mkCombinationConfig2D.py --combo /afs/cern.ch/work/g/gboldrin/public/public/CMSSW_10_2_13/src/HiggsAnalysis/AnalyticAnomalousCoupling/test/SSWW_OSWW_2op --prefix combination_SSWW_OSWW --process SSWW_OSWW --ch /afs/cern.ch/work/g/gboldrin/public/public/CMSSW_10_2_13/src/HiggsAnalysis/AnalyticAnomalousCoupling/test/SSWW_2op_best,/afs/cern.ch/work/g/gboldrin/public/public/CMSSW_10_2_13/src/HiggsAnalysis/AnalyticAnomalousCoupling/test/OSWW_2op_best --chprefix to_Latinos,to_Latinos --chprocess SSWW,OSWW --model EFTNeg --out 2DPlotConfig/SSWW_OSWW_2D.py

from glob import glob 
import os 
import argparse 
import ROOT
import sys

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser for 2D plotting scans')
    parser.add_argument('--combo',     dest='combo',     help='target folder with combined fits', required = True)
    parser.add_argument('--prefix',     dest='prefix',     help='target folder prefix', required = True)
    parser.add_argument('--process',     dest='process',     help='target folder process name', required = True)

    parser.add_argument('--ch',     dest='ch',     help='comma separated list target folder with channel fits', required = True)
    parser.add_argument('--chprefix',     dest='chprefix',     help='comma separated list channel folder prefix', required = True)
    parser.add_argument('--chprocess',     dest='chprocess',     help='comma separated list channel folder process name', required = True)

    parser.add_argument('--model',     dest='model',     help='target folder model name', required = True)

    parser.add_argument('--colors',     dest='colors',     help='Colors for each channel, last one is the combination', required = False, default = "870,797,829,909,797,909,1")
    parser.add_argument('--linestyles',     dest='linestyles',     help='Linestyle for each channel, last one is the combination', required = False, default = "2,3,5,6,3,6,1")

    parser.add_argument('--out',     dest='out',     help='output name', required = True)
    parser.add_argument('--verbose',     dest='verbose',     help='verbosity', required = False, default = False, action = "store_true")
    args = parser.parse_args()


    #splitting channels lists
    ch_ = args.ch.split(",")
    chp_ = args.chprefix.split(",")
    chprocess_ =args.chprocess.split(",")
    colors = [int(i) for i in args.colors.split(",")]
    lines_ = [int(i) for i in args.linestyles.split(",")]


    # full 15 operators of interest
    ops = ['cqq3', 'cqq31', 'cHl3', 'cqq1', 'cqq11', 'cll1', 'cW', 'cHq3', 'cHbox', 'cHq1', 'cHW', 'cHWB', 'cHDD', 'cHl1', 'cll']

    # final dict will contain: 
    # op combo as key
    # combination path to fit
    # for all channels, path to their fit
    final_dict = {}

    for op in ops:
        
        ls  = glob(args.combo+ "/" + args.prefix + "_" + op + "_*") 
        if len(ls) == 0:
            ls  = glob(args.combo+ "/" + args.prefix + "_" + op + "*") 


        for path in ls:

            subop = path.split(args.combo+ "/" + args.prefix + "_")[1]
            final_dict[subop] = {}


            dc = glob(path + "/" + args.model +  "/datacards/" + args.process + "_" + subop + "/*/datacard.txt")
            fit = glob(path + "/" + args.model +  "/datacards/" + args.process + "_" + subop + "/*/higgs*.root")

            if len(dc) != 1 or len(fit) != 1: sys.exit("[ERROR] too  many things in {}".format(path + "/" + args.model +  "/datacards/" + args.process + "_" + subop))
            best_var = dc[0].split("/")[-2] #last is datacard.txt, before var1_var2_...

            final_dict[subop]["combined"] = fit[0] #path to the combined fit

            #now retrieving each channel fit

            datacard = open(dc[0], 'r')
            lines = datacard.readlines()

            #all vars is a list of the type
            # [['SSWW', 'ptl2'], ['OSWW', 'ptl2']] 
            #1st entry is the channel name, second is the beest variable in the datacard
            all_vars = []
            for line in lines:
                if "bin     " in line:
                    ch_var = (line.split("bin     ")[1:])[0]
                    ch_var = (ch_var.strip(" ")).split(" ")
                    for i in ch_var:
                        if i != '' and i != "\n":
                            all_vars.append([i.strip("\n").split("_")[0], "_".join(i.strip("\n").split("_")[1:])]) #in case of variables with underscores
                    break

            channels = [i[0] for i in all_vars]
            bestv = [i[1] for i in all_vars]


            if not all([i for i in channels for i in args.ch]): sys.exit("[ERROR] not all channels in datacards are specified in input")
            
            for channel, var in zip(channels, bestv):
                # retrieve the fit
                idx = chprocess_.index(channel)
                ch_path = ch_[idx]
                ch_prefix = chp_[idx]

                subfit = glob(ch_path + "/" + ch_prefix + "_" + channel + "_" + subop + "/" + args.model +  "/datacards/" + channel + "_" + subop + "/{}/higgs*.root".format(var))

                if len(subfit) != 1: 
                    prova = "_".join(i for i in subop.split("_")[::-1])
                    subfit = glob(ch_path + "/" + ch_prefix + "_" + channel + "_" + prova + "/" + args.model +  "/datacards/" + channel + "_" + prova + "/{}/higgs*.root".format(var))

                    if len(subfit) != 1:
                        sys.exit("[ERROR] Missing fit for channel in combination, searched at: {}".format(ch_path + "/" + ch_prefix + "_" + channel + "_" + subop + "/" + args.model +  "/datacards/" + channel + "_" + subop + "/{}/higgs*.root".format(var)))

                final_dict[subop][channel] = subfit[0]


    if args.verbose:
        for key in final_dict.keys():
            print("OP: " + key)
            print("combined: " + final_dict[key]["combined"].split("/")[-2])

            for ch in final_dict[key].keys():
                if ch != "combined": 
                    print("{}: {}".format(ch, final_dict[key][ch].split("/")[-2]))
            print(" ")

    
    #Now writing everything into the config file
    file_ = open(args.out, 'w')
    file_.write("from collections import OrderedDict \n\n\n")
    file_.write("operators = OrderedDict()\n\n\n")

    file_.write("is_combo = True\n\n\n")

    for sub in final_dict.keys():
        file_.write("operators['{}'] = OrderedDict()\n".format(sub))

        idx = 0
        for key in final_dict[sub].keys():
            if key != "combined":
                file_.write("operators['{}']['{}']  = OrderedDict()\n".format(sub, key))
                file_.write("operators['{}']['{}']['path'] =  '{}'\n".format(sub, key, final_dict[sub][key]))
                file_.write("operators['{}']['{}']['color'] =  '{}'\n".format(sub, key, colors[idx]))
                file_.write("operators['{}']['{}']['linestyle'] =  '{}'\n".format(sub, key, lines_[idx]))
                idx += 1


        comb_color = colors[-1]
        comb_ls = lines_[-1]

        file_.write("operators['{}']['combined']  = OrderedDict()\n".format(sub, 'combined'))
        file_.write("operators['{}']['combined']['path'] =  '{}'\n".format(sub, final_dict[sub]['combined']))
        file_.write("operators['{}']['combined']['color'] =  '{}'\n".format(sub, comb_color))
        file_.write("operators['{}']['combined']['linestyle'] =  '{}'\n".format(sub, comb_ls))

        file_.write("\n\n")


    


