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


parser = argparse.ArgumentParser(description='Command line parser for model testing')
parser.add_argument('--inFiles',     dest='inFiles',     help='comma separated list of files. 2 files', required = False, default="EFTNeg,EFTNeg-alt")
parser.add_argument('--leg',     dest='leg',     help='comma separated list of legend name (pairing with files)', required = False, default="EFTNeg,EFTNeg-alt")
parser.add_argument('--ops',     dest='ops',     help='comma separated list of ops names. Have to be the same for the files', required = False, default="k_cG")
parser.add_argument('--labels',     dest='labels',     help='comma separated list of axis labels. If 1d then only one, if 2d 2', required = False, default="cG")
parser.add_argument('--outFolder',     dest='outFolder',     help='outfolder in which to store plots',    default = ".")
parser.add_argument('--outFile',     dest='outFile',     help='name of the out file',    default = "ll.png")

args = parser.parse_args()

if len(sys.argv) < 3:
    sys.exit("[ERROR] please provide two files ... ")


first_file = args.inFiles.split(",")[0]
second_file = args.inFiles.split(",")[1]

fitted_ops = args.ops.split(",")
is2D = len(fitted_ops) == 2
leg = args.leg.split(",")

#PLOTTING HELPER
cpm = PM.CombinePlotManager()
cpm.NLL_lims = [10, -30]
cpm.setGradient()

cpm.xtit = args.labels.split(",")[0]
if is2D:
   cpm.ytit = args.labels.split(",")[1]


mkdir(args.outFolder)


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

    cpm.configureOpPlot(leg[0], plot_dict)
    cpm.createLS2D(fitted_ops,first_file , inclass=leg[0], FillHigh=True)
    plot_dict["Contour"][cpm.contours[0]]['SetLineColor'] = ROOT.kBlue
    plot_dict["Contour"][cpm.contours[1]]['SetLineColor'] = ROOT.kBlue
    plot_dict["Min"]['SetMarkerColor'] = ROOT.kBlue
    plot_dict["Min"]['SetMarkerStyle'] = 22
    cpm.configureOpPlot(leg[1], plot_dict)
    cpm.createLS2D(fitted_ops,second_file , inclass=leg[1], FillHigh=True)

    cpm.generateAllBoxes()

    c = ROOT.TCanvas("c", "c", 1000, 1000)

    c_1s = cpm.LS2D[leg[0]]["Contour"][cpm.contours[0]]
    c_2s = cpm.LS2D[leg[0]]["Contour"][cpm.contours[1]]

    c_1sn = cpm.LS2D[leg[1]]["Contour"][cpm.contours[0]]
    c_2sn = cpm.LS2D[leg[1]]["Contour"][cpm.contours[1]]

    min_1 = cpm.LS2D[leg[0]]["Min"]
    min_2 = cpm.LS2D[leg[1]]["Min"] 


    legend = ROOT.TLegend(0.85, 0.85, 0.6, 0.6)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(c_1s, "{} #pm 1#sigma".format(leg[0]), "L")
    legend.AddEntry(c_1sn, "{} #pm 1#sigma".format(leg[1]), "L")
    legend.AddEntry(c_2s, "{} #pm 2#sigma".format(leg[0]), "L")
    legend.AddEntry(c_2sn, "{} #pm 2#sigma".format(leg[1]), "L")

    margins = 0.11
    ROOT.gPad.SetRightMargin(margins)
    ROOT.gPad.SetLeftMargin(margins)
    ROOT.gPad.SetBottomMargin(margins)
    ROOT.gPad.SetTopMargin(margins)
    ROOT.gPad.SetFrameLineWidth(3)

    #c_2s.GetXaxis().SetLimits(-20, 20)
    #c_2s.GetYaxis().SetRangeUser(-20, 100)
    
    c_2s.Draw("AC")
    c_2sn.Draw("C same")
    c_1s.Draw("C same")
    c_1s.Draw("C same")

    min_1.Draw("P")
    min_2.Draw("P")

    legend.Draw()

    for item in cpm.optionals:
        item.Draw("same")

    c.SetGrid()
    c.SetTicks()
    c.Draw()

    c.Print(args.outFolder + "/" + args.outFile)

else:

    plot_dict = {
        'SetTitle': "",
        'SetMarkerStyle': 21,
        'SetLineWidth': 3,
        'SetMarkerColor': ROOT.kMagenta,
        'SetLineColor': ROOT.kMagenta,
    }

    cpm.configureOpPlot(leg[0], plot_dict)
    cpm.createLS1D(fitted_ops[0], first_file, inclass=leg[0])
    legend = {leg[0]: "{}:l".format(leg[0])}

    plot_dict['SetLineColor'] = ROOT.kBlue
    cpm.configureOpPlot(leg[1], plot_dict)
    cpm.createLS1D(fitted_ops[0], first_file, inclass=leg[1])
    legend[leg[1]] = "{}:l".format(leg[1])

    cpm.CanvasCreator([800,800], margins=0.1)
    cpm.setCanvOptions({"SetGrid": True})
    cpm.generateAllBoxes()
    cpm.createLegend(legend, legcoord = (0.35, 0.88, 0.65, 0.65))

    cpm.saveName = args.outFolder + "/" + args.outFile
    cpm.plot1D(save=True)











