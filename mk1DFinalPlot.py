import os
import sys
import argparse
import numpy as np 
import itertools
from glob import glob
import stat
import ROOT
from copy import deepcopy
from array import array
import math
from collections import OrderedDict
from operator import itemgetter

def ConvertOptoLatex(op):

    d = {
        'cHDD': 'Q_{HD}',
        'cHbox': 'Q_{H#Box}',
        'cW': 'Q_{W}',
        'cHB': 'Q_{HB}',
        'cHW': 'Q_{HW}',
        'cHWB': 'Q_{HWB}',
        'cll': 'Q_{ll}',
        'cll1': 'Q_{ll}\'',
        'cqq1': 'Q_{qq}^{(1)}',
        'cqq11': 'Q_{qq}^{(1,1)}',
        'cHl1': 'Q_{Hl}^{(1)}',
        'cHl3': 'Q_{Hl}^{(3)}',
        'cHq1': 'Q_{Hq}^{(1)}',
        'cHq3': 'Q_{Hq}^{(3)}',
        'cHe': 'Q_{He}',
        'cHu': 'Q_{Hu}',
        'cHd': 'Q_{Hd}',
        'cqq3': 'Q_{qq}^{(3)}',
        'cqq31': 'Q_{qq}^{(3,1)}',

    }

    return d[op]

def ConvertProc(proc):

    d = {
        "SSWW": "W^{#pm}W^{#pm}+2j",
        "OSWW_OSWWQCD": "W^{#pm}W^{#mp}+2j",
        "OSWW": "W^{#pm}W^{#mp}+2j",
        "OSWWQCD": "W^{#pm}W^{#mp}+2j",
        "WZ_WZQCD": "W^{#pm}Z+2j",
        "WZ": "W^{#pm}Z+2j",
        "WZQCD": "W^{#pm}Z+2j",
        "inWW": "W^{#pm}W^{#mp}+0j",
        "WW": "W^{#pm}W^{#mp}+0j",
        "ZZ": "ZZ+2j",
        "ZV": "ZV+2j",
        "combined": "Combined",
    }

    if proc in d.keys(): return d[proc]
    else: return proc

def RetrieveLL(path, op, maxNLL):

    
    f = ROOT.TFile(path)
    limit = f.Get("limit")
    
    to_draw = ROOT.TString("2*deltaNLL:{}".format("k_" + op))
    n = limit.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(maxNLL), -30), "l")
    print(path, n)

    x = np.ndarray((n), 'd', limit.GetV2())[1:] #removing first element (0,0)
    y_ = np.ndarray((n), 'd', limit.GetV1())[1:] #removing first element (0,0)

    x, ind = np.unique(x, return_index = True)
    y_ = y_[ind]
    y = np.array([i-min(y_) for i in y_])

    graphScan = ROOT.TGraph(x.size,x,y)

    graphScan.GetYaxis().SetTitle("-2 #Delta LL")
    graphScan.GetXaxis().SetTitle(ConvertOptoLatex(op))
    graphScan.GetYaxis().SetTitleSize(0.04)
    graphScan.GetXaxis().SetTitleSize(0.04)

    return graphScan


def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass 

if __name__ == "__main__":

    ROOT.gROOT.SetBatch(1)

    parser = argparse.ArgumentParser(description='Command line parser for 2D plotting scans')
    parser.add_argument('--cfg',     dest='cfg',     help='the config file', required = True)
    parser.add_argument('--maxNLL',     dest='maxNLL',     help='Max likelihood', required = False, default = "20")
    parser.add_argument('--outf',     dest='outf',     help='out folder name', required = False, default = "summary2D")
    parser.add_argument('--lumi',     dest='lumi',     help='lumi to plot', required = False, default = "100")
    parser.add_argument('--splitLeg',     dest='splitLeg',     help='Do not plot legend on canvas but in a sepaerate plot', action="store_true", default = False)
    args = parser.parse_args()

    is_combo = False
    operators = OrderedDict()
    plt_options = {}


    execfile(args.cfg)

    mkdir(args.outf)

    if not is_combo:

        for op in operators.keys():

            canvas_d = Retrieve2DLikelihood (operators, op, args.maxNLL)

            mkdir(args.outf + "/" + op)

            #create as many canvas as necessary each containing up to 5 contours
            n_ = math.ceil(float(len(canvas_d['1sg']))/5)

            for idx in range(0,int(n_)):

                c = ROOT.TCanvas("c_{}_{}".format(op, idx), "c_{}_{}".format(op, idx), 1000, 1000)

                margins = 0.13

                ROOT.gPad.SetRightMargin(margins)
                ROOT.gPad.SetLeftMargin(margins)
                ROOT.gPad.SetBottomMargin(margins)
                ROOT.gPad.SetTopMargin(margins)
                ROOT.gPad.SetFrameLineWidth(3)
                ROOT.gPad.SetTicks()

                leg = ROOT.TLegend(0.15, 0.8, 0.85, 0.85)
                leg.SetBorderSize(0)
                leg.SetNColumns(len(canvas_d['1sg'][ idx*5: (idx*5) + 5]))
                leg.SetTextSize(0.025)

                linestyles = [2,7,5,6,4] * int(n_)
#                ROOT.gStyle.SetPalette(ROOT.kRainBow)
#                col = ROOT.TColor.GetPalette()
#                step = len(col)/5
#                cols = []
#                for i in range (0,5):
#                    cols.append(col[int(step*i)])
#                cols = cols * int(n_)
                cols = [4,433,417,6,2] * int(n_)

                c.SetGrid()
                y_min = canvas_d['1sg'][idx*5].GetYaxis().GetXmin()
                y_max = canvas_d['1sg'][idx*5].GetYaxis().GetXmax()
                y_min_new = 1.1*canvas_d['1sg'][idx*5].GetYaxis().GetXmin()
                y_max_new = 1.1*canvas_d['1sg'][idx*5].GetYaxis().GetXmax() 
                canvas_d['1sg'][idx*5].GetXaxis().SetLimits(-1, 1)
                canvas_d['1sg'][idx*5].GetYaxis().SetRangeUser(y_min_new, y_max_new)
                canvas_d['1sg'][idx*5].GetYaxis().SetTitleOffset(1.5)
                canvas_d['1sg'][idx*5].GetYaxis().SetTitle(ConvertOptoLatex(op))
                canvas_d['1sg'][idx*5].GetXaxis().SetTitle("2nd Operator")
                canvas_d['1sg'][idx*5].SetTitle("")
                canvas_d['1sg'][idx*5].SetLineStyle(linestyles[0])
                canvas_d['1sg'][idx*5].SetLineColor(cols[0])
                canvas_d['1sg'][idx*5].Draw("AL")
                canvas_d['min'][idx*5].Draw("P")

                name = ConvertOptoLatex(canvas_d['n_op'][idx*5])
                if canvas_d['scale'][idx*5] != 1: name = str(canvas_d['scale'][idx*5]) + " #times " + name

                leg.AddEntry(canvas_d['1sg'][idx*5], name, "L")

                for i,j, n, ls, col, scale in zip(canvas_d['1sg'][idx*5 +1:  (idx*5) + 5], canvas_d['min'][idx*5 +1:  (idx*5) + 5], canvas_d['n_op'][idx*5 +1:  (idx*5) + 5], linestyles[idx*5 +1:  (idx*5) + 5], cols[idx*5 +1:  (idx*5) + 5], canvas_d['scale'][idx*5 +1:  (idx*5) + 5]):
                    i.SetLineStyle(ls)
                    i.SetLineColor(col)
                    i.Draw("L same")
                    j.Draw("P same")
                    if i.GetYaxis().GetXmin() < y_min : 
                        y_min = i.GetYaxis().GetXmin()
                    if i.GetYaxis().GetXmax() > y_max :
                        y_max = i.GetYaxis().GetXmax()
                    name = ConvertOptoLatex(n) 
                    if scale !=1 : name =  str(scale) + " #times " + ConvertOptoLatex(n)
                    leg.AddEntry(i, name, "L")

                #Draw fancy

                tex3 = ROOT.TLatex(0.86,.89,"100 fb^{-1}   (13 TeV)")
                tex3.SetNDC()
                tex3.SetTextAlign(31)
                tex3.SetTextFont(42)
                tex3.SetTextSize(0.04)
                tex3.SetLineWidth(2)
                tex3.Draw()

                if "process" in plt_options.keys():
                    if 'xpos' not in  plt_options.keys(): xpos = 0.35
                    else: xpos = plt_options['xpos']
                    if 'size' not in  plt_options.keys(): size = 0.04
                    else: size = plt_options['size']
                    tex4 = ROOT.TLatex(xpos,.89,plt_options['process'])
                    tex4.SetNDC()
                    tex4.SetTextAlign(31)
                    tex4.SetTextFont(42)
                    tex4.SetTextSize(size)
                    tex4.SetLineWidth(2)
                    tex4.Draw()

                if not args.splitLeg: leg.Draw()
                c.Draw()
                c.Print(args.outf + "/" + op + "/r_" + op + "{}.pdf".format(idx))

                canvas_d['1sg'][idx*5].GetYaxis().SetRangeUser(1.1*y_min, 1.1*y_max)
                c.Draw()
                c.Print(args.outf + "/" + op + "/" + op + "{}.pdf".format(idx))
        
    else:

        for op in operators.keys():

            channels = operators[op].keys()


            graphs = []
            
            #cycling on all the channels in the cfg
            for key in channels:

                #extrapolate gs (the full 2d scan), contours (2 graphs [1sigma and 2 sigma])
                # and the minimum (0,0) by construction
                print(op)
                LL = RetrieveLL(operators[op][key]['path'], op, args.maxNLL)


                min_x, max_x = LL.GetXaxis().GetXmin(), LL.GetXaxis().GetXmax() 
                #min_y, max_y = LL.GetYaxis().GetXmin(), LL.GetYaxis().GetXmax()
                min_y, max_y = LL.GetYaxis().GetXmin(), 2*float(args.maxNLL)

                #Because otherwise they wold overlap with the frame
                LL.GetYaxis().SetRangeUser(min_y - 0.05 , max_y)

                #set style
                #shaded combination 
                if key == "combined":
                    LL.SetLineWidth(4)
                    LL.SetLineColorAlpha(int(operators[op][key]['color']), 0.6)
                else:
                    LL.SetLineWidth(5)
                    LL.SetLineColor(int(operators[op][key]['color']))
                    
                LL.SetLineStyle(int(operators[op][key]['linestyle']))

                graphs.append([key, LL, [min_x, max_x]])

            #zoomed version
            c = ROOT.TCanvas("c_{}".format(op), "c_{}".format(op), 1000, 1000)

            margins = 0.13

            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)
            ROOT.gPad.SetTicks()

            leg = ROOT.TLegend(0.15, 0.8, 0.85, 0.85)
            leg.SetBorderSize(0)
            leg.SetNColumns(len(graphs))
            leg.SetTextSize(0.025)

            #c.SetGrid()

            #first graph
            graphs[0][1].GetYaxis().SetTitleOffset(1.1)
            #graphs[0][1].GetYaxis().SetTitleSize(0.05)
            graphs[0][1].GetXaxis().SetTitleOffset(1.1)
            #graphs[0][1].GetXaxis().SetTitleSize(0.05)
            graphs[0][1].SetTitle("")
            graphs[0][1].Draw("AL")

            axis_limits = graphs[0][2]

            #Draw 1sigma and 2sigma lines

            x_frac = axis_limits[0] + abs(0.05*(axis_limits[1]-axis_limits[0]))

            o_sigma = ROOT.TLine(axis_limits[0], 1, axis_limits[1], 1)
            o_sigma.SetLineStyle(2)
            o_sigma.SetLineWidth(2)
            o_sigma.SetLineColor(ROOT.kGray+2)
            t_sigma = ROOT.TLine(axis_limits[0], 3.84, axis_limits[1], 3.84)
            t_sigma.SetLineStyle(2)
            t_sigma.SetLineWidth(2)
            t_sigma.SetLineColor(ROOT.kGray+2)

            o_sigma.Draw("L same")
            t_sigma.Draw("L same")

            name = graphs[0][0]
            leg.AddEntry(graphs[0][1], name, "L")

            for i in graphs[1:]:
                i[1].Draw("L same")
                name = i[0]
                if name =="combined": name = "Combined"
                leg.AddEntry(i[1], name, "L")

            os = ROOT.TLatex()
            os.SetTextFont(42)
            os.SetTextSize(0.03)
            os.DrawLatex( x_frac, 1.05, '68%' )
            ts = ROOT.TLatex()
            ts.SetTextFont(42)
            ts.SetTextSize(0.03)
            ts.DrawLatex( x_frac, 3.89, '95%' )

            #Draw fancy

            tex3 = ROOT.TLatex(0.86,.89,"100 fb^{-1}   (13 TeV)")
            tex3.SetNDC()
            tex3.SetTextAlign(31)
            tex3.SetTextFont(42)
            tex3.SetTextSize(0.04)
            tex3.SetLineWidth(2)
            tex3.Draw()

            if "process" in plt_options.keys():
                if 'xpos' not in  plt_options.keys(): xpos = 0.35
                else: xpos = plt_options['xpos']
                if 'size' not in  plt_options.keys(): size = 0.04
                else: size = plt_options['size']
                if 'font' not in  plt_options.keys(): font = 42
                else: font = plt_options['font']
                tex4 = ROOT.TLatex(xpos,.89,plt_options['process'])
                tex4.SetNDC()
                tex4.SetTextAlign(31)
                tex4.SetTextFont(font)
                tex4.SetTextSize(size)
                tex4.SetLineWidth(2)
                tex4.Draw()

            if not args.splitLeg: leg.Draw()
            c.Draw()
            c.Print(args.outf + "/" + "_".join(i for i in channels) + "_" + op + ".pdf")
            c.Print(args.outf + "/" + "_".join(i for i in channels) + "_" + op + ".png")

        if args.splitLeg:

            c = ROOT.TCanvas("c_{}".format(op), "c_{}".format(op), 1000, 1000)
            margins = 0.13

            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)
            ROOT.gPad.SetTicks()

            leg = ROOT.TLegend(0.15, 0.15, 0.85, 0.85)
            leg.SetBorderSize(0)
            leg.SetNColumns(1)
            leg.SetTextSize(0.06)

            fakeG = deepcopy(graphs[0][1])
            fakeG.GetYaxis().SetTitleOffset(1.1)
            fakeG.GetYaxis().SetTitleOffset(1.1)
            fakeG.SetLineColor(0)
            fakeG.GetXaxis().SetLabelSize(0)
            fakeG.GetYaxis().SetLabelSize(0)
            fakeG.GetXaxis().SetTitle("")
            fakeG.GetYaxis().SetTitle("")
            fakeG.SetTitle("")
            fakeG.Draw("AL")

            name = graphs[0][0]
            leg.AddEntry(graphs[0][1], ConvertProc(name), "F")

            for i in graphs[1:]:
                name = i[0]
                leg.AddEntry(i[1], ConvertProc(name), "F")

            tex3 = ROOT.TLatex(0.86,.89,"100 fb^{-1}   (13 TeV)")
            tex3.SetNDC()
            tex3.SetTextAlign(31)
            tex3.SetTextFont(42)
            tex3.SetTextSize(0.04)
            tex3.SetLineWidth(2)
            tex3.Draw()

            leg.Draw()

            c.Draw()
            c.Print(args.outf + "/legend.pdf")
            c.Print(args.outf + "/legend.png")

            