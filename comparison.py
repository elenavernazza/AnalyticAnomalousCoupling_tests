from CombUtils import CombUtils
import argparse
import sys
import os
from itertools import combinations
import copy
import plotter.PlotManager as PM
import ROOT

def mkdir(dir_name):
    try:
        os.mkdir(dir_name)
    except:
        print("dir already present")

    return 

def build_dummy_syst(n_sis, ops_dict, sys_val = 1.002):
    syst = {}
    sm = 0
    for j in range(len(ops_dict["Name"])): 
        if ops_dict["Name"][j] == "sm":
            sm = ops_dict["Rate"][j]

    for i in range(n_sis):
        syst["bla" + str(i)] = ['lnN']
        for j in range(len(ops_dict["Name"])): 
            if ops_dict["Name"][j] == "sm":
                syst["bla" + str(i)].append((ops_dict["Name"][j], str(sys_val)))
            elif "sm_" in ops_dict["Name"][j]:
                composite_sys = (sys_val-1)*(float(sm)/ops_dict["Rate"][j]) +1
                syst["bla" + str(i)].append((ops_dict["Name"][j], '%.*f' % (5, composite_sys)))
            else:
                syst["bla" + str(i)].append((ops_dict["Name"][j], "-"))

    return syst


parser = argparse.ArgumentParser(description='Command line parser for model testing')
parser.add_argument('--rmdat',     dest='rmdat',     help='Remove all datacards',    default = True, action="store_false")
parser.add_argument('--sysbox',     dest='sysbox',     help='Plot latex box with syst value',    default = False, action="store_true")
parser.add_argument('--nopbox',     dest='nopbox',     help='Plot latex box with Nops value',    default = False, action="store_true")
parser.add_argument('--rmws',     dest='rmws',     help='Remove all binary workspaces',    default = True, action="store_false")
parser.add_argument('--npoints',     dest='npoints',     help='Points for combine fit',    default = 10000, type=int)
parser.add_argument('--sysval',     dest='sysval',     help='systematic value',    default = 1.002, type=float)
parser.add_argument('--ops',     dest='ops',     help='comma separated operators', required = False)
parser.add_argument('--fit2D',     dest='fit2D',     help='comma separated list of two operators for simultaneous fit', required = False)
parser.add_argument('--fit1D',     dest='fit1D',     help='operator for 1D fit', required = False)
parser.add_argument('--out',     dest='out',     help='comma separated out name for 1D-2D plots',    default = "mVSm_2D.png,mVSm_1D.png")

args = parser.parse_args()

if args.ops != None: op_comb = args.ops.split(',')
else: op_comb = ['cG', 'cGtil']

if args.fit2D != None: fit = args.fit2D.split(',')
else: fit = ['cG', 'cGtil']

if args.fit1D != None: fit1d = args.fit1D.split(',')
else: fit1d = ['cG']

#OUTPUT NAMES
out = args.out.split(',')
#assert len(out) - len(op_comb) == 0, "Invalid out names, should be 1/2 comma separated names"

#INITIALIZING COMBINE HELPER
combine_helper = CombUtils()


#PLOTTING HELPER
cpm = PM.CombinePlotManager()
cpm.NLL_lims = [10, -30]
cpm.setGradient()
cpm.xtit = fit[0]
cpm.ytit = fit[1]

plot_dict = {
    "Graph":{
        'SetTitle': "",
        'SetLineWidth': 2,
        'SetLineColor': ROOT.kBlack,
        'Draw': 'colz'
    },
    "Contour":{
        cpm.contours[0]:{
            'SetTitle': "",
            'SetLineWidth': 3,
            'SetLineColor': ROOT.kBlack,
            'SetLineStyle': 1
        },
        cpm.contours[1]:{
            'SetTitle': "",
            'SetLineWidth': 3,
            'SetLineColor': ROOT.kBlack,
            'SetLineStyle': 7
        }
    }, 
    "Min":{
        'SetTitle': '',
        'SetMarkerColor': ROOT.kBlack,
        'SetMarkerStyle': 20,
        'SetMarkerSize': 2
    }
}


#DATACARD NAMES
d_name = "datacardPos.txt"
d_name_1 = "datacardNeg.txt"
d_name_2 = "datacardNegAlt.txt"

#BUILD FIRST THE SM,LIN,QUAD,MIXED DATACARD
dict_EFT = combine_helper.EFT(op_comb)
dict_EFT = combine_helper.addBkg(dict_EFT, count=30)

#EFT NEG DICT NO ALTERNATIVE
dict_EFTN = combine_helper.EFTNegative(dict_EFT, op_comb)

#EFT NEG DICT ALTERNATIVE
dict_EFTN_alt = combine_helper.EFTNegative(dict_EFT, op_comb, alt = True)

#DEFINE RANGE FOR FIT PARS OF INTEREST
range_2D = ""
for c in fit:
    range_2D += "k_"+c + "=" +  str(-10) + "," + str(10) + ":" 
range_2D = range_2D[:-1]

#2D fit POSITIVE MODEL
d_sys = build_dummy_syst(1, dict_EFT, args.sysval)
combine_helper.makedatacard(dict_EFT, d_sys, d_name)
t2w_ = combine_helper.t2w(d_name, op_comb, model = "EFT", out = "EFT_model.root")
print("[RUNNING] text2workspace")
print(t2w_)
os.system(t2w_)

comb = combine_helper.comb(op_comb, fit, range_2D, npoints=args.npoints, root = "EFT_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Pos.root")

#EXTRACTING PLOT INFOS 
cpm.configureOpPlot("Pos", plot_dict)
if len(op_comb) >= 2: cpm.createLS2D(['k_' + i for i in fit], "higgsCombineTest.MultiDimFit.mH125.Pos.root", inclass="Pos", FillHigh=True)

#2D fit NO ALTERNATIVE MODEL
d_sys = build_dummy_syst(1, dict_EFTN, args.sysval)
combine_helper.makedatacard(dict_EFTN, d_sys, d_name_1)
t2w_ = combine_helper.t2w(d_name_1, op_comb, model = "EFTNegative", out = "EFTNeg_model.root")
print("[RUNNING] text2workspace")
print(t2w_)
os.system(t2w_)

comb = combine_helper.comb(op_comb, fit, range_2D, npoints=args.npoints, root = "EFTNeg_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Neg.root")

#EXTRACTING PLOT INFOS 
plot_dict["Contour"][cpm.contours[0]]['SetLineColor'] = ROOT.kBlue
plot_dict["Contour"][cpm.contours[1]]['SetLineColor'] = ROOT.kBlue
plot_dict["Min"]['SetMarkerColor'] = ROOT.kBlue
plot_dict["Min"]['SetMarkerStyle'] = 22

cpm.configureOpPlot("Neg", plot_dict)
if len(op_comb) >= 2: cpm.createLS2D(['k_' + i for i in fit], "higgsCombineTest.MultiDimFit.mH125.Neg.root", inclass="Neg", FillHigh=True)

#2D fit ALTERNATIVE MODEL
d_sys = build_dummy_syst(1, dict_EFTN_alt, args.sysval)
combine_helper.makedatacard(dict_EFTN_alt, d_sys, d_name_2)
t2w_ = combine_helper.t2w(d_name_2, op_comb, model = "EFTNegative", out = "EFTNeg_alt_model.root", alt = True)
print("[RUNNING] text2workspace")
print(t2w_)
os.system(t2w_)

comb = combine_helper.comb(op_comb, fit, range_2D, npoints=args.npoints,  root = "EFTNeg_alt_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Negalt.root")

#EXTRACTING PLOT INFOS 

plot_dict["Contour"][cpm.contours[0]]['SetLineColor'] = ROOT.kMagenta
plot_dict["Contour"][cpm.contours[1]]['SetLineColor'] = ROOT.kMagenta
plot_dict["Min"]['SetMarkerColor'] = ROOT.kMagenta
plot_dict["Min"]['SetMarkerStyle'] = 34

cpm.configureOpPlot("Neg_alt", plot_dict)
if len(op_comb) >= 2: cpm.createLS2D(['k_' + i for i in fit], "higgsCombineTest.MultiDimFit.mH125.Negalt.root", inclass="Neg_alt", FillHigh=True)

#PLOTTING

if len(op_comb) >= 2:
    cpm.generateAllBoxes()
    if args.nopbox: cpm.generateNopsBox(len(op_comb))
    if args.sysbox: cpm.generateSystBox(args.sysval)

    c = ROOT.TCanvas("c", "c", 1000, 1000)

    c_1s = cpm.LS2D["Neg"]["Contour"][cpm.contours[0]]
    c_2s = cpm.LS2D["Neg"]["Contour"][cpm.contours[1]]
    min_EFT = cpm.LS2D["Neg"]["Min"]
    min_Neg = cpm.LS2D["Neg_alt"]["Min"]
    min_Pos = cpm.LS2D["Pos"]["Min"]
    c_1sn = cpm.LS2D["Neg_alt"]["Contour"][cpm.contours[0]]
    c_2sn = cpm.LS2D["Neg_alt"]["Contour"][cpm.contours[1]]
    c_1sp = cpm.LS2D["Pos"]["Contour"][cpm.contours[0]]
    c_2sp = cpm.LS2D["Pos"]["Contour"][cpm.contours[1]]


    leg = ROOT.TLegend(0.85, 0.85, 0.6, 0.6)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.AddEntry(c_1sp, "EFTPos #pm 1#sigma", "L")
    leg.AddEntry(c_1s, "EFTNeg #pm 1#sigma", "L")
    leg.AddEntry(c_1sn, "EFTNeg-alt #pm 1#sigma", "L")
    leg.AddEntry(c_2sp, "EFTPos #pm 2#sigma", "L")
    leg.AddEntry(c_2s, "EFTNeg #pm 2#sigma", "L")
    leg.AddEntry(c_2sn, "EFTNeg-alt #pm 2#sigma", "L")

    margins = 0.11
    ROOT.gPad.SetRightMargin(margins)
    ROOT.gPad.SetLeftMargin(margins)
    ROOT.gPad.SetBottomMargin(margins)
    ROOT.gPad.SetTopMargin(margins)
    ROOT.gPad.SetFrameLineWidth(3)

    c_2sn.GetXaxis().SetLimits(-6, 7)
    c_2sn.GetYaxis().SetRangeUser(-6, 7)

    c_2sn.Draw("AC")
    c_2sp.Draw("C same")
    c_2s.Draw("C same")
    c_1sn.Draw("C same")
    c_1sp.Draw("C same")
    c_1s.Draw("C same")


    min_Pos.Draw("P")
    min_EFT.Draw("P")
    min_Neg.Draw("P")

    leg.Draw()

    for item in cpm.optionals:
        item.Draw("same")

    c.SetGrid()
    c.SetTicks()
    c.Draw()

    c.Print(out[0])

#-------------- 1D ----------------
plot_dict = {
    'SetTitle': "",
    'SetMarkerStyle': 21,
    'SetLineWidth': 3,
    'SetMarkerColor': ROOT.kBlack,
    'SetLineColor': ROOT.kBlack,
}
cpm2 = PM.CombinePlotManager()
cpm2.xtit = fit1d[0]

#1D RANGE FOR FIT PAR
range_1D = ""
for c in fit1d:
    range_1D += "k_"+c + "=" +  str(-10) + "," + str(10) + ":" 
range_1D = range_1D[:-1]

#1D FIT POSITIVE MODEL

comb = combine_helper.comb(op_comb, fit1d, range_1D, npoints=args.npoints, root = "EFT_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Pos.root")

cpm2.configureOpPlot("Pos", plot_dict)
cpm2.createLS1D("k_cG", "higgsCombineTest.MultiDimFit.mH125.Pos.root", inclass="Pos")

leg = {"Pos": "EFTPos:l"}

#1D FIT NO ALTERNATIVE MODEL

comb = combine_helper.comb(op_comb, fit1d, range_1D, npoints=args.npoints, root = "EFTNeg_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Neg.root")

plot_dict['SetLineColor'] = ROOT.kMagenta
cpm2.configureOpPlot("Neg", plot_dict)
cpm2.createLS1D("k_cG", "higgsCombineTest.MultiDimFit.mH125.Neg.root", inclass="Neg")


leg["Neg"] =  "EFTNeg:l"

#1D FIT ALTERNATIVE MODEL

comb = combine_helper.comb(op_comb, fit1d, range_1D, npoints=args.npoints, root = "EFTNeg_alt_model.root")
print("[RUNNING] Combine")
print(comb)
os.system(comb)

os.system("mv higgsCombineTest.MultiDimFit.mH125.root higgsCombineTest.MultiDimFit.mH125.Negalt.root")

plot_dict['SetLineColor'] = ROOT.kBlue
cpm2.configureOpPlot("Neg_alt", plot_dict)
cpm2.createLS1D("k_cG", "higgsCombineTest.MultiDimFit.mH125.Neg.root", inclass="Neg_alt")

leg['Neg_alt'] = "EFTNeg-alt:l"

cpm2.CanvasCreator([800,800], margins=0.1)
cpm2.setCanvOptions({"SetGrid": True})
cpm2.generateAllBoxes()
if args.nopbox: cpm.generateNopsBox(len(op_comb))
if args.sysbox: cpm.generateSystBox(args.sysval)
cpm2.createLegend(leg, legcoord = (0.35, 0.88, 0.65, 0.65))

cpm2.saveName = out[1]
cpm2.plot1D(save=True)

if args.rmdat: os.system("rm  {} {} {}".format(d_name, d_name_1, d_name_2)) #deleting datacards
if args.rmws: os.system("rm EFT_model.root EFTNeg_model.root EFTNeg_alt_model.root")

