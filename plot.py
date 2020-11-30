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

def convertName(name):
    d = {
        "deltaphijj" : "#Delta#phi_{jj}",
        "mll" : "m_{ll}",
        "mjj" : "m_{jj}",
        "met" : "MET",
        "phij1" : "#phi_{j1}",
        "phij2" : "#phi_{j2}",
        "ptj1" : "p_{T,j1}",
        "ptj2" : "p_{T,j2}",
        "ptl1" : "p_{T,l1}",
        "ptl2" : "p_{T,l2}",
        "ptll" : "p_{T,ll}",
        "deltaetajj": "#Delta#eta_{jj}",
        "etaj1" : "#eta_{j1}",
        "etaj2" : "#eta_{j2}",
        "etal1" : "#eta_{l1}",
        "etal2" : "#eta_{l2}",
        " ": None
    }

    return d[name]


parser = argparse.ArgumentParser(description='Command line parser for model testing')
parser.add_argument('--inFiles',     dest='inFiles',     help='comma separated list of files. 2 files', required = False, default="EFTNeg,EFTNeg-alt")
parser.add_argument('--leg',     dest='leg',     help='comma separated list of legend name (pairing with files)', required = False, default="EFTNeg,EFTNeg-alt")
parser.add_argument('--legtit',     dest='legtit',     help='Legend header', required = False, default=" ")
parser.add_argument('--lumi',     dest='lumi',     help='lumi', required = False, default="XX.XX")
parser.add_argument('--ops',     dest='ops',     help='comma separated list of ops names. Have to be the same for the files', required = False, default="k_cG")
parser.add_argument('--labels',     dest='labels',     help='comma separated list of axis labels. If 1d then only one, if 2d 2', required = False, default="c1,c2")
parser.add_argument('--outFolder',     dest='outFolder',     help='outfolder in which to store plots',    default = ".")
parser.add_argument('--outFile',     dest='outFile',     help='name of the out file',    default = "ll.png")

args = parser.parse_args()

if len(sys.argv) < 3:
    sys.exit("[ERROR] please provide two files ... ")


files = args.inFiles.split(",")

fitted_ops = args.ops.split(",")
is2D = len(fitted_ops) == 2
leg = args.leg.split(",")

#PLOTTING HELPER
cpm = PM.CombinePlotManager()
cpm.NLL_lims = [100, -30]
cpm.setGradient()
cpm.lumi = args.lumi
if convertName(args.legtit) != None:
    cpm.legtit = convertName(args.legtit)

cpm.xtit = args.labels.split(",")[0]
if is2D:
   cpm.ytit = args.labels.split(",")[1]


mkdir(args.outFolder)


colors = [ROOT.kMagenta, ROOT.kBlue, ROOT.kBlack, ROOT.kGreen, ROOT.kOrange, ROOT.kPink]
markerstyles = [20, 21, 22, 23, 24, 25, 26, 27]


if is2D: 
    plot_dict = {
        "Graph":{
            'SetTitle': "",
            'SetLineWidth': 2,
            'SetLineColor': ROOT.kMagenta,
            'Draw': 'colz'
        },
        "Contour":{
            cpm.contours[0]:{
                'SetTitle': "",
                'SetLineWidth': 3,
                'SetLineColor': ROOT.kMagenta,
                'SetLineStyle': 1
            },
            cpm.contours[1]:{
                'SetTitle': "",
                'SetLineWidth': 3,
                'SetLineColor': ROOT.kMagenta,
                'SetLineStyle': 7
            }
        }, 
        "Min":{
            'SetTitle': '',
            'SetMarkerColor': ROOT.kMagenta,
            'SetMarkerStyle': 20,
            'SetMarkerSize': 2
        }
    }

    canv = ROOT.TCanvas("main canvas", "main canvas", 1000, 1000)
    cpm.generateAllBoxes()

    legend = ROOT.TLegend(0.85, 0.85, 0.6, 0.6)
    legend.SetBorderSize(0)
    if convertName(args.legtit) != None:
        legend.SetHeader(convertName(args.legtit))
    #legend.SetFillStyle(0)

    for i,file_ in enumerate(files):

        plot_dict["Contour"][cpm.contours[0]]['SetLineColor'] = colors[i]
        plot_dict["Contour"][cpm.contours[1]]['SetLineColor'] = colors[i]
        plot_dict["Min"]['SetMarkerColor'] = colors[i]
        plot_dict["Min"]['SetMarkerStyle'] = 22

        cpm.configureOpPlot(leg[i], plot_dict)
        cpm.createLS2D(fitted_ops,file_ , inclass=leg[i], FillHigh=True)


    for i,name in enumerate(leg):

        c_1s = cpm.LS2D[name]["Contour"][cpm.contours[0]]
        c_2s = cpm.LS2D[name]["Contour"][cpm.contours[1]]
        min_1 = cpm.LS2D[name]["Min"]

        legend.AddEntry(c_1s, "{} #pm 1#sigma".format(name), "L")
        legend.AddEntry(c_2s, "{} #pm 2#sigma".format(name), "L")

        if i == 0:
            c_2s.GetXaxis().SetLimits(-1,2)
            c_2s.SetMaximum(2)
            c_2s.SetMinimum(-1)
            c_2s.Draw("AC")
        else:
            c_2s.Draw("C same")

        c_1s.Draw("C same")
        min_1.Draw("P same")



    legend.Draw()

    for item in cpm.optionals:
        item.Draw("same")

    margins = 0.11
    ROOT.gPad.SetRightMargin(margins)
    ROOT.gPad.SetLeftMargin(margins)
    ROOT.gPad.SetBottomMargin(margins)
    ROOT.gPad.SetTopMargin(margins)
    ROOT.gPad.SetFrameLineWidth(3)

    canv.SetGrid()
    canv.SetTicks()
    canv.Draw()

    canv.Print(args.outFolder + "/" + args.outFile)

else:

    plot_dict = {
        'SetTitle': "",
        'SetMarkerStyle': 21,
        'SetLineWidth': 3,
        'SetMarkerColor': ROOT.kMagenta,
        'SetLineColor': ROOT.kMagenta,
    }

    legend = {}
    for i,file_ in enumerate(files):

        plot_dict['SetLineColor'] = colors[i]
        cpm.configureOpPlot(leg[i], plot_dict)
        cpm.createLS1D(fitted_ops[0], file_, inclass=leg[i])
        legend[leg[i]] = "{}:l".format(leg[i])
    

    cpm.CanvasCreator([800,800], margins=0.1)
    cpm.setCanvOptions({"SetGrid": True})
    cpm.generateAllBoxes()
    cpm.createLegend(legend, legcoord = (0.35, 0.88, 0.65, 0.65))

    cpm.saveName = args.outFolder + "/" + args.outFile
    cpm.plot1D(save=True)











