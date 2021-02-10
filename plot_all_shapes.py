import ROOT
import numpy as np
import sys 
import os
import plotter.PlotManager as PM
from itertools import combinations
from copy import deepcopy
from array import array
from glob import glob
import argparse


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


def givecoeff(comp_name, k, model):

    #only 1d atm
    if model == "EFT":
        d = { "lin": k,
            "quad": k*k,
            "sm_lin_quad": k,
            }
    else:
        d = { "lin": 0,
          "quad": k*k - k,
          "sm_lin_quad": k,
          "sm": 1. - k
        }

    return d[comp_name]


def plot_shapes (model, shapes_file, k_min, k_max, step, x_tit, save_name, root):

    cpm = PM.CombinePlotManager()

    #colors = [851, 921, 418, 857, 617, 810, 409, 418]

    f = ROOT.TFile(shapes_file)
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

    ks = np.arange(k_min, k_max, step)
    if len(ks) > 4: Legend.SetNColumns(3)

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    bsm_cols = ROOT.TColor.GetPalette()
    
    st_ = int(len(bsm_cols)/len(ks))

    for j,k in enumerate(ks):
        h_bsm = deepcopy(histos["histo_sm"])
        if not model == "EFT":
            h_bsm.Scale(givecoeff("sm", k, model))
        h_bsm.SetFillColor(0)
        for sh in histos.keys():
            if sh != "histo_sm" and sh != "histo_Data" and "BSM" not in sh:
                type_ = (sh.split("histo_")[1]).split("_c")[0]
                fact = givecoeff(type_, k, model)
                h_ = deepcopy(histos[sh])
                h_.Scale(fact)
                h_bsm.Add(h_)

        h_bsm.SetLineColor(bsm_cols[j*st_])
        h_bsm.SetMarkerSize(0)
        h_bsm.SetMarkerStyle(0)
        h_bsm.SetLineWidth(2)
        h_bsm.GetYaxis().SetTitle("Events")
        h_bsm.SetTitle("")
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
    Legend.Draw("same")

    c.SaveAs(save_name + '.pdf')
    if root: c.SaveAs(save_name + '.root')


if __name__ == '__main__':

    print("""
 ____________________ 
  Plot distributions 
 --------------------""")

    parser = argparse.ArgumentParser(description='Command line parser')
    parser.add_argument('--baseFolder', dest='baseFolder', help='Base folder containing all shapes', required=True)
    parser.add_argument('--kmin', dest='kmin', help='Min for the Wilson coefficient', type=float, required=True)
    parser.add_argument('--kmax', dest='kmax', help='Max for the Wilson coefficient', type=float, required=True)
    parser.add_argument('--kstep', dest='kstep', help='Step between min and max', type=float, required=True)
    parser.add_argument('--prefix', dest='prefix', help='Prefix of operators folders contained in baseFolder', default='to_Latinos', required=False)
    parser.add_argument('--root', dest='root', help='Save also .root files', default=False, action='store_true', required=False)
    args = parser.parse_args()

    baseDirIn = os.path.abspath(args.baseFolder).rstrip('/')
    baseDirOut = baseDirIn + '_ShapesPlots'
    if os.path.isdir(baseDirOut):
        print ('\n[ERROR] {0} folder already exists'.format(os.path.basename(baseDirOut)))
        sys.exit(1)
    else:
        os.mkdir(baseDirOut)

    opsDirs = [o for o in glob(baseDirIn + '/*') if (args.prefix in o and os.path.isdir(o))]

    for od in opsDirs:
        models = [m for m in glob(od + '/*') if os.path.isdir(m)]
        for model in models:
            dc = model + '/datacards'
            operators = [op for op in glob(dc + '/*') if os.path.isdir(op)]
            if len(operators) == 1:
                histoSuffix = os.path.basename(operators[0])
                opDirOut = baseDirOut + '/' + histoSuffix
                if not os.path.isdir(opDirOut):
                    os.mkdir(opDirOut)
                modelName = os.path.basename(model)
                modDirOut = opDirOut + '/' + modelName
                os.mkdir(modDirOut)
                # assuming that the convention is any_prefix_operatorname
                operator = histoSuffix.split('_')[-1]
                print ('\n=== working on operator ' + operator + ' ===\n')
            else:
                print ('[ERROR] more than one operator contained in ' + dc)
                continue

            variables = [v for v in glob(operators[0] + '/*') if os.path.isdir(v)]
            for varDir in variables:
                var = os.path.basename(varDir)
                varFileOut = modDirOut + '/' + var
                print ('[INFO] working on variable ' + var)
                histos = varDir + '/shapes/histos_{0}.root'.format(histoSuffix)
                if '_' in var:
                    sub = var.split('_')[-1]
                    x_title = var.replace(sub, '{'+sub+'}')
                else:
                    x_title = var
                x_title = x_title.replace('j1','^{j1}').replace('j2','^{j2}')
                x_title = x_title.replace('l1','^{l1}').replace('l2','^{l2}')
                x_title = x_title.replace('l3','^{l3}').replace('l4','^{l4}')
                x_title = x_title.replace('jj','^{jj}').replace('ll','^{ll}')
                x_title = x_title.replace('delta','#Delta')
                x_title = x_title.replace('eta','#eta')
                x_title = x_title.replace('phi','#phi')
                if any(x in var.lower() for x in ['mjj','mll', 'pt', 'met']):
                    x_title = x_title + ' [GeV]'
                plot_shapes (modelName, histos, args.kmin, args.kmax, args.kstep,
                                x_title , varFileOut, args.root)