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

    d = { "lin": k,
          "quad": k*k,
          "sm_lin_quad": k,
          "lin_mixed": k*k,
        }

    return d[comp_name]

def givecoeff2D(ops, op_name, comp_name, k, l):

    if op_name == ops[0]:
        d = { "lin": k,
              "quad": k*k,
              "lin_mixed": k*l,
            }
    elif op_name == ops[1]:
        d = { "lin": l,
              "quad": l*l,
              "lin_mixed": k*l,
            }

    return d[comp_name]

def givecoeff2DEFTNeg(comp_name, k, l):

    d = { #"S": 1-k-l+k*l,
          "S+L1+Q1": k*(1-l),
          "S+L2+Q2": l*(1-k),
          "Q1": k*(k-1),
          "Q2": l*(l-1),
          "S+L1+Q1+L2+Q2+2M": k*l,
        }

    return d[comp_name]

def givecoeff2DEFTNegalt(comp_name, k, l):

    d = { #"S": 1-k-l,
          "S+L1+Q1": k,
          "S+L2+Q2": l,
          "Q1": k*(k-1-l),
          "Q2": l*(l-1-k),
          "Q1+Q2+2M": k*l,
        }

    return d[comp_name]

def mkhistoEFTNeg(histos, ops):

    h_1 = deepcopy(histos["histo_sm"])
    h_1.Add(histos["histo_lin_"+ops[0]])
    h_1.Add(histos["histo_quad_"+ops[0]])
    h_2 = deepcopy(histos["histo_sm"])
    h_2.Add(histos["histo_lin_"+ops[1]])
    h_2.Add(histos["histo_quad_"+ops[1]])
    h_3 = deepcopy(histos["histo_quad_"+ops[0]])
    h_4 = deepcopy(histos["histo_quad_"+ops[1]])
    h_5 = deepcopy(histos["histo_sm"])
    h_5.Add(histos["histo_lin_"+ops[0]])
    h_5.Add(histos["histo_quad_"+ops[0]])
    h_5.Add(histos["histo_lin_"+ops[1]])
    h_5.Add(histos["histo_quad_"+ops[1]])
    h_5.Add(histos["histo_lin_mixed_"+ops[0]+"_"+ops[1]])

    histosEFTNeg = { "S+L1+Q1": h_1,
                     "S+L2+Q2": h_2,
                     "Q1": h_3,
                     "Q2": h_4,
                     "S+L1+Q1+L2+Q2+2M": h_5,
                   }

    return histosEFTNeg

def mkhistoEFTNegalt(histos, ops):

    h_1 = deepcopy(histos["histo_sm"])
    h_1.Add(histos["histo_lin_"+ops[0]])
    h_1.Add(histos["histo_quad_"+ops[0]])
    h_2 = deepcopy(histos["histo_sm"])
    h_2.Add(histos["histo_lin_"+ops[1]])
    h_2.Add(histos["histo_quad_"+ops[1]])
    h_3 = deepcopy(histos["histo_quad_"+ops[0]])
    h_4 = deepcopy(histos["histo_quad_"+ops[1]])
    h_5 = deepcopy(histos["histo_lin_mixed_"+ops[0]+"_"+ops[1]])
    h_5.Add(histos["histo_quad_"+ops[0]])
    h_5.Add(histos["histo_quad_"+ops[1]])

    histosEFTNegalt = { "S+L1+Q1": h_1,
                        "S+L2+Q2": h_2,
                        "Q1": h_3,
                        "Q2": h_4,
                        "Q1+Q2+2M": h_5,
                   }

    return histosEFTNegalt

def drawEFTNeg(ks, histos, ops, Legend):

    histosEFTNeg = mkhistoEFTNeg(histos, ops)

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    bsm_cols = ROOT.TColor.GetPalette()

    st_ = int(len(bsm_cols)/len(ks)/(len(ks)+1))

    for j,k in enumerate(ks):
        for i,l in enumerate(ks):
            h_bsm = deepcopy(histos["histo_sm"])
            h_bsm.Scale(1-k-2*l+2*k*l)
            for sh in histosEFTNeg.keys():
                fact = givecoeff2DEFTNeg(sh, k, 2*l)
                h_ = deepcopy(histosEFTNeg[sh])
                h_.Scale(fact)
                h_bsm.Add(h_)

            h_bsm.SetFillColor(0)
            h_bsm.SetLineColor(bsm_cols[(j+2)*(i+1)*st_])
            h_bsm.SetMarkerSize(0)
            h_bsm.SetMarkerStyle(0)
            h_bsm.SetLineWidth(2)
            h_bsm.GetYaxis().SetTitle("Events")
            h_bsm.SetTitle("")
            x_tit = "var"
            if len(sys.argv) > 2: x_tit = sys.argv[2]
            h_bsm.GetXaxis().SetTitle(x_tit)
            Legend.AddEntry(h_bsm, "BSM k={:.3} l={:.3}".format(k,2*l))
            histos["BSM{:.3} l={:.3}".format(k,l)] = h_bsm

    return histos

def drawEFTNegalt(ks, histos, ops, Legend):

    histosEFTNegalt = mkhistoEFTNegalt(histos, ops)

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    bsm_cols = ROOT.TColor.GetPalette()

    st_ = int(len(bsm_cols)/len(ks)/(len(ks)+1))

    for j,k in enumerate(ks):
        for i,l in enumerate(ks):
            h_bsm = deepcopy(histos["histo_sm"])
            h_bsm.Scale(1-k-2*l)
            for sh in histosEFTNegalt.keys():
                fact = givecoeff2DEFTNegalt(sh, k, 2*l)
                h_ = deepcopy(histosEFTNegalt[sh])
                h_.Scale(fact)
                h_bsm.Add(h_)

            h_bsm.SetFillColor(0)
            h_bsm.SetLineColor(bsm_cols[(j+2)*(i+1)*st_])
            h_bsm.SetMarkerSize(0)
            h_bsm.SetMarkerStyle(0)
            h_bsm.SetLineWidth(2)
            h_bsm.GetYaxis().SetTitle("Events")
            h_bsm.SetTitle("")
            x_tit = "var"
            if len(sys.argv) > 2: x_tit = sys.argv[2]
            h_bsm.GetXaxis().SetTitle(x_tit)
            Legend.AddEntry(h_bsm, "BSM k={:.3} l={:.3}".format(k,2*l))
            histos["BSM{:.3} l={:.3}".format(k,l)] = h_bsm

    return histos

def drawEFT(ks, histos, ops, Legend):

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    bsm_cols = ROOT.TColor.GetPalette()

    st_ = int(len(bsm_cols)/len(ks)/(len(ks)+1))

    for j,k in enumerate(ks):
        for i,l in enumerate(ks):
            h_bsm = deepcopy(histos["histo_sm"])
            h_bsm.SetFillColor(0)
            for sh in histos.keys():
                if sh != "histo_sm" and sh != "histo_Data" and "BSM" not in sh:
                    op_name = "c" + sh.split("_c")[1]
                    type_ = (sh.split("histo_")[1]).split("_c")[0]
                    fact = givecoeff2D(ops, op_name, type_, k, 2*l)
                    h_ = deepcopy(histos[sh])
                    h_.Scale(fact)
                    h_bsm.Add(h_)

            h_bsm.SetLineColor(bsm_cols[(i+1)*(j+2)*st_])
            h_bsm.SetMarkerSize(0)
            h_bsm.SetMarkerStyle(0)
            h_bsm.SetLineWidth(2)
            h_bsm.GetYaxis().SetTitle("Events")
            h_bsm.SetTitle("")
            x_tit = "var"
            if len(sys.argv) > 2: x_tit = sys.argv[2]
            h_bsm.GetXaxis().SetTitle(x_tit)
            Legend.AddEntry(h_bsm, "BSM k={:.3} l={:.3}".format(k,2*l))
            histos["BSM{:.3} l={:.3}".format(k,l)] = h_bsm

    return histos


if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

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

    ops.sort()
    print(ops)

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
#            To draw only bsm
            elif "lin" not in shap and "quad" not in shap:
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

    if sys.argv[7] == "EFT":
        histos = drawEFT(ks, histos, ops, Legend)

    elif sys.argv[7] == "EFTNeg":
        histos = drawEFTNeg(ks, histos, ops, Legend)

    elif sys.argv[7] == "EFTNeg-alt":
        histos = drawEFTNegalt(ks, histos, ops, Legend)

    min_ = 0
    max_ = 0

    for key in histos.keys():
#       To draw only bsm
        if "lin" not in key and "quad" not in key:
            if histos[key].GetMaximum() > max_: max_ = histos[key].GetMaximum()
            if histos[key].GetMinimum() < min_: min_ = histos[key].GetMinimum()

    histos["histo_sm"].SetMinimum(min_ - abs(0.5*min_))
    histos["histo_sm"].SetMaximum(max_ + abs(0.5*max_))

    histos["histo_sm"].Draw("hist")

    for key in histos.keys():
#        To draw only bsm
        if key != "histo_sm" and "lin" not in key and "quad" not in key:
            histos[key].Draw("hist same")


    cpm.generateAllBoxes()
    for item in cpm.optionals:
        item.Draw("same")

    c.Draw()
    
    save_name = "shapes.png"
    if len(sys.argv) > 3: save_name = sys.argv[3]
    
    Legend.Draw("same")
    c.SaveAs(save_name)
