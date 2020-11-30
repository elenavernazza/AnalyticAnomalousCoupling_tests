import ROOT
import numpy as np
import sys 
import os
import plotter.PlotManager as PM
from itertools import combinations
from copy import deepcopy
from array import array

def generateColorDict(ops):
    d = {
        "histo_sm": 851,
        "histo_Data": 1,
        "histo_BSM": ROOT.kBlack
    }

    linear = [632, 433, 822]
    quadratic = [418, 908, 879]
    sm_lin_quad = [857, 618, 900]
    for i,op in enumerate(ops):
        d.update({"histo_lin_" + op: linear[i]})
        d.update({"histo_quad_" + op: quadratic[i]})
        d.update({"histo_sm_lin_quad_" + op: sm_lin_quad[i]})

    lin_mixed = [617, 897, 414, 859, 863, 421]
    quad_mixed = [810, 430, 402, 833, 875, 808]
    sm_lin_quad_mixed = [409, 823, 619, 877, 899, 420]

    op_comb = list(combinations(ops, 2))

    for z,i in enumerate(op_comb):
        d.update({"histo_lin_mixed_" + i[0] + "_" + i[1]: lin_mixed[z]})
        d.update({"histo_lin_mixed_" + i[1] + "_" + i[0]: lin_mixed[z]})

        d.update({"histo_quad_mixed_" + i[0] + "_" + i[1]: quad_mixed[z]})
        d.update({"histo_quad_mixed_" + i[1] + "_" + i[0]: quad_mixed[z]})

        d.update({"histo_sm_lin_quad_mixed_" + i[0] + "_" + i[1]: sm_lin_quad_mixed[z]})
        d.update({"histo_sm_lin_quad_mixed_" + i[1] + "_" + i[0]: sm_lin_quad_mixed[z]})

    
    return d


def proc2leg(comp_name):


    d = { "sm": "SM",
          "lin": "L ",
          "quad": "Q ",
          "lin_mixed": "M ",
          "sm_lin_quad": "SM+L+Q ",
          "quad_mixed": "Q+Q+M ",
          "sm_lin_quad_mixed": "SM+L+L+Q+Q+M ",
          "Data": "DATA"
        }

    type_ = comp_name.split("_c")[0]
    newName = d[type_]

    if type_ != "sm" and type_!= "Data": #need to account for operators here
        ops = comp_name.split(type_ + "_")[1]
        if len(ops.split("_")) == 2: 
            ops = ops.split("_")
            newName += ops[0] + "_" + ops[1]
        else:
            newName += ops

    return newName

def givecoeff(comp_name, k):

    #only 1d atm
    d = { "lin": k,
          "quad": k*k,
          "sm_lin_quad": k,
        }

    return d[comp_name]



if __name__ == "__main__":

    cpm = PM.CombinePlotManager()

    #colors = [851, 921, 418, 857, 617, 810, 409, 418]

    if len(sys.argv) < 2: sys.exit("Provide shapes file...")

    f = ROOT.TFile(sys.argv[1])
    shapes = [i.GetName() for i in f.GetListOfKeys()]

    #detect number of operators
    ops = []
    for s in shapes:
        if s != "histo_sm" and s != "histo_Data":
            s = s.split("histo_")[1]
            type_ = s.split("_c")[0]
            ops_ = s.split(type_ + "_")[1]
            ops_ = ops_.split("_")
            for op in ops_:
                if op not in ops:
                    ops.append(op)


    cd = generateColorDict(ops)

    c = ROOT.TCanvas("c", "c", 800, 800)

    margins = 0.11
    ROOT.gPad.SetRightMargin(margins)
    ROOT.gPad.SetLeftMargin(margins)
    ROOT.gPad.SetBottomMargin(margins)
    ROOT.gPad.SetTopMargin(margins)
    ROOT.gPad.SetFrameLineWidth(3)

    ROOT.gStyle.SetOptStat(0)

    Legend = ROOT.TLegend(0.85, 0.85, 0.5, 0.65)
    Legend.SetNColumns(2)
    Legend.SetBorderSize(0)

    histos = {}

    h_sm = f.Get("histo_sm")

    h_sm.SetLineColor(cd["histo_sm"])
    h_sm.SetLineWidth(2)
    
    h_sm.GetYaxis().SetTitle("Events")
    h_sm.SetTitle("")
    x_tit = "var"
    if len(sys.argv) > 2: x_tit = sys.argv[2]
    h_sm.GetXaxis().SetTitle(x_tit)
    h_sm.SetFillColor(cd["histo_sm"])
    Legend.AddEntry(h_sm, "SM")

    histos["histo_sm"] =  h_sm


    for idx, shap in enumerate(shapes):
        if shap != "histo_sm" and shap != "histo_Data":
            h = f.Get(shap)
            h.SetLineColor(cd[shap])
            
            h.SetLineWidth(2)
            h.SetMarkerSize(0)
            h.SetMarkerStyle(0)

            leg_name = proc2leg(shap.split("histo_")[1])

            if shap == "histo_sm": 
                #h.SetFillColor(cd[shap])
                Legend.AddEntry(h, leg_name)
            else:
                Legend.AddEntry(h, leg_name, "L")

            histos[shap] = h

        elif shap == "histo_Data":
            h = f.Get(shap)
            h.SetLineColor(1)
            h.SetMarkerStyle(8)
            h.SetMarkerColor(1)
            h.SetMarkerSize(1)

            leg_name = "Data"
            h.Draw("hist same")
            Legend.AddEntry(h, leg_name)

            histos[shap] = h


    #bsm component
    k_min = 1
    k_max = 2
    step = 1

    if len(sys.argv) > 6: 
        k_min = float(sys.argv[4])
        k_max = float(sys.argv[5])
        step = float(sys.argv[6])

    ks = np.arange(k_min, k_max, step)
    if len(ks) > 4: Legend.SetNColumns(3)

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    bsm_cols = ROOT.TColor.GetPalette()
    
    st_ = int(len(bsm_cols)/len(ks))

    for j,k in enumerate(ks):
        h_bsm = deepcopy(histos["histo_sm"])
        h_bsm.SetFillColor(0)
        for sh in histos.keys():
            if sh != "histo_sm" and sh != "histo_Data" and "BSM" not in sh:
                type_ = (sh.split("histo_")[1]).split("_c")[0]
                fact = givecoeff(type_, k)
                h_ = deepcopy(histos[sh])
                h_.Scale(fact)
                h_bsm.Add(h_)

        h_bsm.SetLineColor(bsm_cols[j*st_])
        h_bsm.SetMarkerSize(0)
        h_bsm.SetMarkerStyle(0)
        h_bsm.SetLineWidth(2)
        h_bsm.GetYaxis().SetTitle("Events")
        h_bsm.SetTitle("")
        x_tit = "var"
        if len(sys.argv) > 2: x_tit = sys.argv[2]
        h_bsm.GetXaxis().SetTitle(x_tit)
        Legend.AddEntry(h_bsm, "BSM k={:.3f}".format(k))
        histos["BSM{:.3f}".format(k)] = h_bsm

    
    min_ = 0
    max_ = 0

    for key in histos.keys():
        if histos[key].GetMaximum() > max_: max_ = histos[key].GetMaximum()
        if histos[key].GetMinimum() < min_: min_ = histos[key].GetMinimum()

    histos["histo_sm"].SetMinimum(min_ - abs(0.5*min_))
    histos["histo_sm"].SetMaximum(max_ + abs(0.5*max_))

    histos["histo_sm"].Draw("hist")

    for key in histos.keys():
        if key != "histo_sm":
            histos[key].Draw("hist same")


    cpm.generateAllBoxes()
    for item in cpm.optionals:
        item.Draw("same")

    c.Draw()
    
    save_name = "shapes.png"
    if len(sys.argv) > 3: save_name = sys.argv[3]
    
    Legend.Draw("same")
    c.SaveAs(save_name)
