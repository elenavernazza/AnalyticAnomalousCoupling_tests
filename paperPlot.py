import ROOT
import numpy as np
import sys 
import os
from itertools import combinations
from copy import deepcopy
from array import array
from glob import glob
import argparse

def GetProcess(proc):

    d = {
        'SSWW': "W^{#pm}W^{#pm}+2j (EWK)",
        'OSWW': "W^{#pm}W^{#mp}+2j (EWK)",
        'WZeu': "W^{#pm}Z+2j (EWK)",
        'inWW': "W^{#pm}W^{#mp}+0j",
        'WZQCD': "W^{#pm}Z+2j (QCD)",
        'OSWWQCD': "W^{#pm}W^{#mp}+2j (QCD)",
    }

    return d[proc]

def GetColor(name):
    d = {
        'sm': ROOT.kGray,
        'lin': ROOT.kRed-4,
        'quad': ROOT.kGreen+2,
        'BSM': [ROOT.kOrange-3, ROOT.kAzure+1, ROOT.kPink+6],
    }

    return d[name]

def convertName(name):
    d = {
        "deltaphijj" : "#Delta#phi_{jj}",
        "mll" : "m_{ll} [GeV]",
        "mee" : "m_{ee} [GeV]",
        "mjj" : "m_{jj} [GeV]",
        "met" : "MET [GeV]",
        "phij1" : "#phi_{j1}",
        "phij2" : "#phi_{j2}",
        "ptj1" : "p_{T,j1} [GeV]",
        "ptj2" : "p_{T,j2} [GeV]",
        "ptl1" : "p_{T,l1} [GeV]",
        "ptl2" : "p_{T,l2} [GeV]",
        "ptl3" : "p_{T,l3} [GeV]",
        "ptll" : "p_{T,ll} [GeV]",
        "ptee" : "p_{T,ee} [GeV]",
        "deltaetajj": "#Delta#eta_{jj}",
        "etaj1" : "#eta_{j1}",
        "etaj2" : "#eta_{j2}",
        "etal1" : "#eta_{l1}",
        "etal2" : "#eta_{l2}",
        " ": None
    }

    return d[name]

def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass 


if __name__ == '__main__':

    print("""
    ____________________ 
    Plot distributions 
    --------------------""")

    parser = argparse.ArgumentParser(description='Command line parser')
    parser.add_argument('--baseFolder', dest='baseFolder', help='Base mkDCInputs folder e.g. SSWW_1op', required=True)
    parser.add_argument('--ks', dest='ks', help='comma separated list of three Wilson coeffs. Default 0.1,1,10', required=False, default = "0.1,1,10")
    parser.add_argument('--prefix', dest='prefix', help='Everything before the op name e.g if to_Latinos_SSWW_cHq3-> to_Latinos_SSWW', default='to_Latinos', required=False)
    parser.add_argument('--model', dest='model', help='Model for which you want to retrieve and build shapes. Default EFT', default='EFT', required=False)
    parser.add_argument('--root', dest='root', help='Save also .root files', default=False, action='store_true', required=False)
    parser.add_argument('--legpos', dest='legpos', help='Legend position: 1 upper left, 2: upper right, default 2 ', required=False, default = "2")
    parser.add_argument('--out', dest='out', help='outfolder path', required=False, default = "distributions")
    parser.add_argument('--linscale', dest='linscale', help='Scale linear component in the plot', required=False, default = "1")
    parser.add_argument('--quadscale', dest='quadscale', help='Scale quadratic component in the plot', required=False, default = "1")
    parser.add_argument('--drawstat', dest='drawstat', help='Draw sedcond pair of plots with SM stat unc', required=False, action="store_true", default=False)
    parser.add_argument('--ymaxdigits', dest='ymaxdigits', help='Argument on y axis MaxDigits', required=False, default = "3")
    parser.add_argument('--xposchannel', dest='xposchannel', help='xposition of the channel label on the upper left corner', required=False, default = "0.42")

    args = parser.parse_args()

    ROOT.gROOT.SetBatch(1)

    ks = [float(i) for i in args.ks.split(",")]
    legpos = int(args.legpos)

    subfs = glob(args.baseFolder + "/" + args.prefix + "*")
    ops = [i.split("/")[-1].split(args.prefix + "_" )[1] for i in subfs ]

    mkdir(args.out)

    lin_scale = float(args.linscale)
    quad_scale = float(args.quadscale)
    model = args.model
    maxd = int(args.ymaxdigits)

    if model not in ["EFT","EFTNeg"]:
        sys.exit("[ERROR] Not the right model")

    xpos_proc = float(args.xposchannel)

    #suppose one single shape file for variable folder:

    for folder, op in zip(subfs, ops):
        
        variables = glob(folder + "/" + model + "/datacards/*/*")

        the_process = variables[0].split("/")[-2].split("_{}".format(op))[0]

        vars_ = [i.split("/")[-1] for i in variables]

        for var_f, var_n in zip(variables, vars_):

            #retireve shape:

            shape_file = glob(var_f + "/shapes/*.root")[0]
            print(shape_file)

            f = ROOT.TFile(shape_file)

            if model == "EFT":

                h_sm = f.Get("histo_sm")
                h_lin = f.Get("histo_lin_{}".format(op))
                h_quad = f.Get("histo_quad_{}".format(op))

            if model == "EFTNeg":

                h_sm = f.Get("histo_sm")
                h_sm_lin_quad = f.Get("histo_sm_lin_quad_{}".format(op))
                h_quad = f.Get("histo_quad_{}".format(op))
                h_sm_neg = deepcopy(h_sm)
                h_sm_neg.Scale(-1.)
                h_quad_neg = deepcopy(h_quad)
                h_quad_neg.Scale(-1.)
                
                h_lin = h_sm_lin_quad
                h_lin.Add(h_sm_neg)
                h_lin.Add(h_quad_neg)

            h_bsm = []

            for i in ks:
                h_bsm.append(deepcopy(h_sm))

            for i,j in enumerate(ks):
                h_l = deepcopy(h_lin)
                h_l.Scale(j)

                h_q = deepcopy(h_quad)
                h_q.Scale(j*j)

                h_bsm[i].Add(h_l)
                h_bsm[i].Add(h_q)
                #print("k = {}, bsm min: {}".format(j, h_bsm[i].GetMinimum()))

                h_lin.Scale(lin_scale)
                h_quad.Scale(quad_scale)

            

            #plotting
            ROOT.gStyle.SetOptStat(0)
            c = ROOT.TCanvas("c_{}".format(op), "c_{}".format(op), 700, 800)
            ROOT.gPad.SetFrameLineWidth(3)

            pad1 = ROOT.TPad("pad", "pad", 0, 0.3, 1, 1)
            pad1.SetFrameLineWidth(2)
            pad1.SetBottomMargin(0.005)
            pad1.Draw()

            pad2 = ROOT.TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
            pad2.SetFrameLineWidth(2)
            pad2.SetTopMargin(0.05)

            pad2.SetFrameBorderMode(0)
            pad2.SetBorderMode(0)
            pad2.SetBottomMargin(0.4)
            pad2.Draw()


            pad1.cd()
            h_sm.SetFillColor(GetColor("sm"))
            h_sm.SetLineColor(0)

            #take as inf the minimum lin. If > 0 then min = 0

            y_min = h_lin.GetMinimum()
            if y_min > 0: y_min = 0
            y_min = y_min - 0.1 * abs(y_min)

            y_max = h_sm.GetMaximum() + 0.4* h_sm.GetMaximum()

            h_sm.SetTitle("")
            h_sm.GetYaxis().SetRangeUser(y_min, y_max)
            h_sm.GetXaxis().SetTitle(convertName(var_n))
            h_sm.GetXaxis().SetTitleSize(1)
            h_sm.GetXaxis().SetTitleOffset(1.2)
            h_sm.GetYaxis().SetTitle("Events")
            h_sm.GetYaxis().SetTitleSize(0.05)
            h_sm.GetYaxis().SetLabelSize(0.05)
            h_sm.GetYaxis().SetTitleOffset(1)
            h_sm.GetYaxis().SetMaxDigits(maxd)
            h_sm.Draw("hist")

            h_quad.SetLineColor(GetColor("quad"))
            h_quad.SetLineWidth(3)
            h_quad.SetLineStyle(7)
            h_quad.Draw("hist same")


            h_lin.SetLineColor(GetColor("lin"))
            h_lin.SetLineWidth(3)
            h_lin.SetLineStyle(7)
            h_lin.Draw("hist same")

            for i,j in enumerate(h_bsm):
                j.SetLineColor(GetColor("BSM")[i])
                j.SetLineWidth(3)
                j.Draw("hist same")
            
            if legpos == 1:
                leg = ROOT.TLegend(0.15, 0.55, 0.4, 0.86)
            elif legpos == 2:
                leg = ROOT.TLegend(0.6, 0.5, 0.89, 0.86)
            leg.SetBorderSize(0)
            leg.SetNColumns(1)
            leg.SetTextSize(0.045)

            leg.AddEntry(h_sm, "SM", "F")

            if quad_scale != 1:
                leg.AddEntry(h_quad, "Quad {} #times {}".format(op, quad_scale), "F")
            else:
                leg.AddEntry(h_quad, "Quad {}".format(op), "F")
                
            if lin_scale != 1:
                leg.AddEntry(h_lin, "Lin {} #times {}".format(op, lin_scale), "F")
            else:
                leg.AddEntry(h_lin, "Lin {}".format(op), "F")

            for i,j in zip(h_bsm, ks):
                leg.AddEntry(i, "SM + EFT {}={}".format(op, j), "F")

            leg.Draw()
            
            #Fancy stuffs
            tex3 = ROOT.TLatex(0.90,.915,"100 fb^{-1}   (13 TeV)")
            tex3.SetNDC()
            tex3.SetTextAlign(31)
            tex3.SetTextFont(42)
            tex3.SetTextSize(0.06)
            tex3.SetLineWidth(3)
            tex3.Draw()


            tex4 = ROOT.TLatex(xpos_proc,.915, GetProcess(the_process))
            tex4.SetNDC()
            tex4.SetTextAlign(31)
            tex4.SetTextFont(42)
            tex4.SetTextSize(0.06)
            tex4.SetLineWidth(3)
            tex4.Draw()

            pad2.cd()

            h_bsm_r = []

            for i,j in enumerate(ks):
                h_ = deepcopy(h_sm)
                h_.Divide(h_bsm[i])

                h_.SetFillColor(0)
                h_.SetLineColor(GetColor("BSM")[i])
                h_.SetLineWidth(2)
                h_bsm_r.append(h_)

            h_bsm_r[0].GetYaxis().SetRangeUser(0.5,1.5)

            h_bsm_r[0].GetYaxis().SetTitle("SM / BSM")
            h_bsm_r[0].GetYaxis().SetTitleSize(0.1)
            h_bsm_r[0].GetYaxis().SetTitleOffset(0.5)
            h_bsm_r[0].GetYaxis().SetNdivisions(4)

            h_bsm_r[0].GetXaxis().SetTitle(convertName(var_n))
            h_bsm_r[0].GetXaxis().SetTitleSize(0.13)
            h_bsm_r[0].GetYaxis().SetLabelSize(0.08)
            h_bsm_r[0].GetXaxis().SetLabelSize(0.1)

            h_bsm_r[0].Draw("hist")
            for i in h_bsm_r[1:]: i.Draw("hist same")



            l = ROOT.TLine(h_sm.GetXaxis().GetXmin(), 1, h_sm.GetXaxis().GetXmax(), 1)
            l.SetLineColor(ROOT.kGray+1)
            l.SetLineWidth(2)
            l.Draw("same")

            c.Update()
            c.Draw()
            c.Print(args.out + "/" + op + "_" + var_n + ".pdf")
            c.Print(args.out + "/" + op + "_" + var_n + ".png")
            if args.root: c.Print(args.out + "/" + op + "_" + var_n + ".root")


            #Now draw the same but with uncertainties on the sm
            if args.drawstat:
                c1 = ROOT.TCanvas("c_{}_stat".format(op), "c_{}_stat".format(op), 700, 800)
                ROOT.gPad.SetFrameLineWidth(3)

                pad3 = ROOT.TPad("pad3", "pad3", 0, 0.3, 1, 1)
                pad3.SetFrameLineWidth(2)
                pad3.SetBottomMargin(0.005)
                pad3.Draw()

                pad4 = ROOT.TPad("pad4", "pad4", 0, 0.0, 1, 0.3)
                pad4.SetFrameLineWidth(2)
                pad4.SetTopMargin(0.05)

                pad4.SetFrameBorderMode(0)
                pad4.SetBorderMode(0)
                pad4.SetBottomMargin(0.4)
                pad4.Draw()


                pad3.cd()

                h_err = deepcopy(h_sm)
                h_err.Sumw2()
                h_err.SetMarkerSize(0)
                h_err.SetFillColor(ROOT.kBlack)
                h_err.SetFillStyle(3004)

                h_sm.Draw("hist")
                h_quad.Draw("hist same")
                h_lin.Draw("hist same")
                h_err.Draw("E2 same")

                for i,j in enumerate(h_bsm):
                    j.Draw("hist same")
                
                if legpos == 1:
                    leg1 = ROOT.TLegend(0.15, 0.51, 0.4, 0.86)
                elif legpos == 2:
                    leg1 = ROOT.TLegend(0.6, 0.5, 0.89, 0.86)
                leg1.SetBorderSize(0)
                leg1.SetNColumns(1)
                leg1.SetTextSize(0.045)

                leg1.AddEntry(h_sm, "SM", "F")
                leg1.AddEntry(h_err, "SM Stat. Unc.", "F")

                if quad_scale != 1:
                    leg1.AddEntry(h_quad, "Quad {} #times {}".format(op, quad_scale), "F")
                else:
                    leg1.AddEntry(h_quad, "Quad {}".format(op), "F")
                    
                if lin_scale != 1:
                    leg1.AddEntry(h_lin, "Lin {} #times {}".format(op, lin_scale), "F")
                else:
                    leg1.AddEntry(h_lin, "Lin {}".format(op), "F")

                for i,j in zip(h_bsm, ks):
                    leg1.AddEntry(i, "SM + EFT {}={}".format(op, j), "F")

                leg1.Draw()

                #Fancy stuffs
                tex5 = ROOT.TLatex(0.90,.915,"100 fb^{-1}   (13 TeV)")
                tex5.SetNDC()
                tex5.SetTextAlign(31)
                tex5.SetTextFont(42)
                tex5.SetTextSize(0.06)
                tex5.SetLineWidth(3)
                tex5.Draw()


                tex6 = ROOT.TLatex(xpos_proc,.915, GetProcess(the_process))
                tex6.SetNDC()
                tex6.SetTextAlign(31)
                tex6.SetTextFont(42)
                tex6.SetTextSize(0.06)
                tex6.SetLineWidth(3)
                tex6.Draw()

                pad4.cd()

                h_bsm_ratio_err = deepcopy(h_sm)
                h_bsm_ratio_err.Divide(h_sm)
                h_bsm_ratio_err.Sumw2()
                h_bsm_ratio_err.SetFillColor(ROOT.kBlack)
                h_bsm_ratio_err.SetFillStyle(3004)


                h_bsm_r_2 = []
                for i in h_bsm_r:
                    h_ = deepcopy(i)
                    h_.SetMarkerSize(2)
                    h_.SetMarkerColor(ROOT.kWhite)
                    #h_.SetLineColor(ROOT.kWhite)
                    #h_.SetLineWidth(2)
                    h_bsm_r_2.append(h_)


                h_bsm_ratio_err.GetYaxis().SetRangeUser(0.5,1.5)
                h_bsm_ratio_err.GetYaxis().SetTitle("SM / BSM")
                h_bsm_ratio_err.GetYaxis().SetTitleSize(0.1)
                h_bsm_ratio_err.GetYaxis().SetTitleOffset(0.5)
                h_bsm_ratio_err.GetYaxis().SetNdivisions(4)

                h_bsm_ratio_err.GetXaxis().SetTitle(convertName(var_n))
                h_bsm_ratio_err.GetXaxis().SetTitleSize(0.13)
                h_bsm_ratio_err.GetYaxis().SetLabelSize(0.08)
                h_bsm_ratio_err.GetXaxis().SetLabelSize(0.1)

                h_bsm_ratio_err.Draw("E2")

                l = ROOT.TLine(h_bsm_ratio_err.GetXaxis().GetXmin(), 1, h_bsm_ratio_err.GetXaxis().GetXmax(), 1)
                l.SetLineColor(ROOT.kBlack)
                l.SetLineWidth(1)
                l.Draw("same")

                #first draw white histos
                for i in h_bsm_r_2:
                    i.Draw("P same")
                    i.Draw("hist same")

                #then draw colored histos
                for j,i in enumerate(h_bsm_r):
                    i.SetFillStyle(0)
                    i.SetMarkerStyle(8)
                    i.SetMarkerSize(1)
                    i.SetMarkerColor(GetColor("BSM")[j])
                    
                    i.Draw("P same")
                    i.Draw("hist same")


                c1.Update()
                c1.Draw()
                c1.SaveAs(args.out + "/" + op + "_" + var_n + "_stat.pdf")
                c1.SaveAs(args.out + "/" + op + "_" + var_n + "_stat.png")
                if args.root: c1.SaveAs(args.out + "/" + op + "_" + var_n + "_stat.root")

            #finally copy the index in here:
            os.system("cp /afs/cern.ch/user/g/gboldrin/index.php " + args.out)

            f.Close()
