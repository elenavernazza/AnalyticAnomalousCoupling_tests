import os
import sys
import ROOT
import argparse
from glob import glob
from copy import deepcopy
import plotter.PlotManager as PM
import numpy as np
from array import array

def convertName(name):
    d = {
        "deltaphijj" : "#delta#phi_{jj}",
        "mll" : "m_{ll}",
        "mjj" : "m_{jj}",
        "met" : "MET",
        "phij1" : "#phi_{j1}",
        "phij2" : "#phi_{j2}",
        "ptj1" : "p_{T,j1}",
        "ptj2" : "p_{T,j2}",
        "ptl1" : "p_{T,l1}",
        "ptl2" : "p_{T,l2}",
        "ptl3" : "p_{T,l3}",
        "ptll" : "p_{T,ll}",
        "deltaetajj": "#delta#eta_{jj}",
        "etaj1" : "#eta_{j1}",
        "etaj2" : "#eta_{j2}",
        "etal1" : "#eta_{l1}",
        "etal2" : "#eta_{l2}",
        " ": None
    }

    if "_" in name:
        name = name.split("_")
        l = [convertName(i) for i in name]
        return ":".join(i for i in l)

    else:
        return d[name]
def mkdir(path):
    try:
        os.mkdir(path)
    except:
        print("Dir already present")

if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

    parser = argparse.ArgumentParser(description='Command line parser for model testing')
    parser.add_argument('--baseFolder',     dest='baseFolder',     help='Base folder', required = True)
    parser.add_argument('--graphLimits',     dest='graphLimits',     help='comma separated list of final graph y axis limits, default is 2,2', required = False, default="2,2")
    parser.add_argument('--drawText',     dest='drawText',     help='Plot text of best variables in final plot', required = False, default=True, action = "store_false")

    args = parser.parse_args()

    final_plot_y_min = -float(args.graphLimits.split(",")[0])
    final_plot_y_max = float(args.graphLimits.split(",")[1])

    outputFolder = os.getcwd() + "/" + args.baseFolder

    f_in = open(outputFolder + "/results.txt", "r")

    best = {}
    mod = []
    mod = ["EFT", "EFTNeg", "EFTNeg-alt"]

    for models in mod:
        best[models] = {}
        best[models]["ops"] = []
        best[models]["best_var"]= []
        best[models]["one_s"] = []
        best[models]["two_s"] = []
        best[models]["best"] = []

    for lines in f_in.readlines():
        if "[MODEL RESULTS]" in lines:
            model = (lines.split("[MODEL RESULTS] ")[1]).split("\n")[0]
        elif "c" in lines:
            parts = lines.split(" 	 ")
            best[model]["ops"].append(parts[0])
            best[model]["best_var"].append(parts[1].split(" ")[1])
            p2_inf = -float(parts[2].split(",")[0].split("[")[1])
            p2_sup = float(parts[2].split(",")[1].split("]")[0])
            best[model]["one_s"].append([p2_inf, p2_sup])
            p3_inf = -float(parts[3].split(",")[0].split("[")[1])
            p3_sup = float(parts[3].split(",")[1].split("]")[0])
            best[model]["two_s"].append([p3_inf, p3_sup])
            best[model]["best"].append([0,0])

    for model in best.keys():

        c = ROOT.TCanvas("c", "c", 800, 600)
        c.SetGrid()
        leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

        margins = 0.11
        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins+0.08)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        vars_ = best[model]["best_var"]
        ops = best[model]["ops"]
        one_s = best[model]["one_s"]
        two_s = best[model]["two_s"]
        best_fit = best[model]["best"]

        two_s, one_s, ops, best_fit, vars_ = zip(*sorted(zip(two_s, one_s, ops, best_fit, vars_)))

        xs = []
        ys = []
        one_inf = []
        one_sup = []
        two_inf = []
        two_sup = []

        base = 0.5
        for j in range(len(best_fit)):
            xs.append(j+base)
            ys.append(0)

        for m,n in zip(one_s, two_s):
            one_inf.append(m[0])
            one_sup.append(m[1])
            two_inf.append(n[0])
            two_sup.append(n[1])

        max_ = max(two_sup)
        min_ = -max(two_inf)

        g1 = ROOT.TGraphAsymmErrors(len(xs), array('d', xs), array('d', ys), array('d', [0.16]*len(xs)), array('d', [0.16]*len(xs)),  array('d', one_inf), array('d', one_sup))
    
        g1.SetMinimum(-10)
        g1.SetMaximum(15)
        g1.SetFillColor(ROOT.kOrange)
        g1.SetLineColor(ROOT.kOrange)
        g1.SetLineWidth(0)
        g1.SetMarkerStyle(24)
        g1.SetMarkerColor(ROOT.kBlue+1)
        g1.SetMarkerSize(1)
        g1.GetYaxis().SetRangeUser(-10,10)


        g2 = ROOT.TGraphAsymmErrors(len(xs), array('d', xs), array('d', ys), array('d', [0.16]*len(xs)), array('d', [0.16]*len(xs)),  array('d', two_inf), array('d', two_sup))
        g2.SetFillColor(ROOT.kGreen+1)
        g2.SetLineWidth(0)
        g2.SetMarkerStyle(24)
        g2.SetMarkerColor(ROOT.kBlue+1)
        g2.SetMarkerSize(1)
        g2.GetYaxis().SetRangeUser(-15,15)

        leg.AddEntry(g1, "#pm 1#sigma Expected", "F")
        leg.AddEntry(g2, "#pm 2#sigma Expected", "F")
        leg.AddEntry(g1, "Best Fit", "P")
        leg.SetBorderSize(2)

        h = ROOT.TH1F("h_{}".format(model), "h_".format(model), len(xs)+2, -1, len(xs)+1)
        h.SetFillColor(0)
        h.SetCanExtend(ROOT.TH1.kAllAxes)
        h.SetStats(0)
        for idx in  range(h.GetNbinsX()):
            if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
            if idx < len(ops)+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, ops[idx-1])
            else: h.GetXaxis().SetBinLabel(idx + 1, "")
        h.GetYaxis().SetTitle("Best Confidence Interval")

        h.LabelsDeflate("X")
        h.LabelsDeflate("Y")
        h.LabelsOption("v")

        ROOT.gStyle.SetLabelSize(.05, "XY")

        h.GetYaxis().SetRangeUser(final_plot_y_min,final_plot_y_max)
        g1.SetHistogram(h)


        ROOT.gStyle.SetOptStat(0)
        

        h.Draw("AXIS")
        c.SetGrid()
        ROOT.gPad.RedrawAxis("g")
        g2.Draw("2 same")
        g1.Draw("2 same")
        g1.Draw("P same")

        c.SetTicks()
        leg.Draw()

        cpm = PM.CombinePlotManager()
#        cpm.lumi = str(args.lumi + " fb^{-1}")

        cpm.generateAllBoxes()

        for item in cpm.optionals:
             item.Draw("same")

        if args.drawText:
            count = 0
            for x,y in zip(xs, two_sup):
                y_ = y + 0.2
                #do not plot if the text pass the plot boundaries
                #if y_ > final_plot_y_max - 0.1: continue
                var = vars_[count]
                count += 1
                latex = ROOT.TLatex()
                latex.SetTextSize(0.025)
                latex.SetTextAlign(12)
                latex.DrawLatex(x-0.14 - 0.02*len(convertName(var)),y_,"{}".format(convertName(var)))

        c.Draw()
        c.Print(outputFolder + "/" + "{}.png".format(model))

    f_in.close()
