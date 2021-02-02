import os
import sys
import argparse
import numpy as np 
import itertools
from glob import glob
from tqdm import tqdm
import stat
import ROOT
from copy import deepcopy
from array import array
import math
from collections import OrderedDict

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
        'cqq11': 'Q_{qq}^{(1)}\'',
        'cHl1': 'Q_{Hl}^{(1)}',
        'cHl3': 'Q_{Hl}^{(3)}',
        'cHq1': 'Q_{Hq}^{(1)}',
        'cHq3': 'Q_{Hq}^{(3)}',
        'cHe': 'Q_{He}',
        'cHu': 'Q_{Hu}',
        'cHd': 'Q_{Hd}',
        'cqq3': 'Q_{qq}^{(3)}',
        'cqq31': 'Q_{qq}^{(3)}\'',

    }

    return d[op]

def Retrieve2DLikelihood(file, op, maxNLL, xscale, yscale):

    f = ROOT.TFile(file)
    t = f.Get("limit")

    for i, event in enumerate(t):
        if i == 0:
            x_min = getattr(event, "k_" + op[0])
            y_min = getattr(event, "k_" + op[1])

        else: break

    exp = ROOT.TGraph()
    exp.SetPoint(0, x_min, y_min)
    exp.SetMarkerSize(3)
    exp.SetMarkerStyle(34)
    exp.SetMarkerColor(ROOT.kGray +2)

    to_draw = ROOT.TString("{}:{}:2*deltaNLL".format("k_" + op[0], "k_" + op[1]))
    n = t.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(maxNLL),-30), "l")

    x = np.ndarray((n), 'd', t.GetV1())
    y = np.ndarray((n), 'd', t.GetV2())
    z_ = np.ndarray((n), 'd', t.GetV3())

    z = np.array([i-min(z_) for i in z_]) #shifting likelihood toward 0
    x = np.array([i*xscale for i in x])
    y = np.array([i*yscale for i in y])

    graphScan = ROOT.TGraph2D(n,x,y,z)

    graphScan.SetNpx(100)
    graphScan.SetNpy(100)

    graphScan.GetZaxis().SetRangeUser(0, float(maxNLL))
    graphScan.GetHistogram().GetZaxis().SetRangeUser(0, float(maxNLL))

    for i in range(graphScan.GetHistogram().GetSize()):
        if (graphScan.GetHistogram().GetBinContent(i+1) == 0):
            graphScan.GetHistogram().SetBinContent(i+1, 100)

    hist = graphScan.GetHistogram().Clone("arb_hist")
    hist.SetContour(2, np.array([2.30, 5.99]))
    hist.Draw("CONT Z LIST")
    ROOT.gPad.Update()

    conts = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    cont_graphs = [deepcopy(conts.At(i).First()) for i in range(2)]

    gs = deepcopy(graphScan)

    f.Close()

    return gs, cont_graphs, exp


def mkdir(path):
    try:
        os.mkdir(path)
    except:
        pass 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser for 2D plotting scans')
    parser.add_argument('--cfg',     dest='cfg',     help='the config file', required = True)
    parser.add_argument('--maxNLL',     dest='maxNLL',     help='Max likelihood', required = False, default = "20")
    parser.add_argument('--outf',     dest='outf',     help='out folder name', required = False, default = "summary2D")
    parser.add_argument('--lumi',     dest='lumi',     help='lumi to plot', required = False, default = "100")
    args = parser.parse_args()

    is_combo = False
    operators = OrderedDict()
    plt_options = {}


    execfile(args.cfg)

    mkdir(args.outf)

    if not is_combo:

        for op in operators.keys():
            canvas_d = {
                '1sg' : [],
                '2sg' : [],
                'min' : [],
                'names' : [],
                'base_op' : op,
                'n_op' : [],
                'scale' : [],
            }

            mkdir(args.outf + "/" + op)

            for proc in operators[op].keys():
                gs, cont_graphs, exp = Retrieve2DLikelihood(operators[op][proc]['path'], 
                                                                [operators[op][proc]['op'],op], args.maxNLL, 
                                                                        float(operators[op][proc]['xscale']), float(operators[op][proc]['yscale']) )
                
                print(operators[op][proc]['op'],op)
                color = operators[op][proc]['linecolor']
                size = operators[op][proc]['linesize']

                cont_graphs[0].SetLineWidth(size)

                cont_graphs[0].SetLineColor(color)
                #x_min, x_max, y_min, y_max = cont_graphs[0].GetXaxis().GetXmin(), cont_graphs[0].GetXaxis().GetXmax(), cont_graphs[0].GetYaxis().GetXmin(), cont_graphs[0].GetYaxis().GetXmax()


                canvas_d['1sg'].append(cont_graphs[0])
                canvas_d['min'].append(exp)
                canvas_d['names'].append(operators[op][proc]['name'])
                canvas_d['n_op'].append(operators[op][proc]['op'])
                canvas_d['scale'].append([float(operators[op][proc]['xscale']), float(operators[op][proc]['yscale'])])

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

                linestyles = [1,2,3,5,6] * int(n_)
                

                c.SetGrid()
                y_min_new = canvas_d['1sg'][idx*5].GetYaxis().GetXmin() - abs(0.2*canvas_d['1sg'][idx*5].GetYaxis().GetXmin())
                y_max_new = canvas_d['1sg'][idx*5].GetYaxis().GetXmax() + abs(0.2*canvas_d['1sg'][idx*5].GetYaxis().GetXmax()) 
                canvas_d['1sg'][idx*5].GetYaxis().SetRangeUser(y_min_new, y_max_new)
                canvas_d['1sg'][idx*5].GetYaxis().SetTitleOffset(1.5)
                canvas_d['1sg'][idx*5].GetYaxis().SetTitle(op)
                canvas_d['1sg'][idx*5].GetXaxis().SetTitle("2nd Operator")
                canvas_d['1sg'][idx*5].SetTitle("")
                canvas_d['1sg'][idx*5].SetLineStyle(linestyles[0])
                canvas_d['1sg'][idx*5].Draw("AL")
                canvas_d['min'][idx*5].Draw("P")

                name = canvas_d['n_op'][idx*5]
                if canvas_d['scale'][idx*5][0] != 1: name =  str(canvas_d['scale'][idx*5][0]) + " #times " + name

                leg.AddEntry(canvas_d['1sg'][idx*5], name, "L")

                for i,j, n, ls, scale in zip(canvas_d['1sg'][idx*5 +1:  (idx*5) + 5], canvas_d['min'][idx*5 +1:  (idx*5) + 5], canvas_d['n_op'][idx*5 +1:  (idx*5) + 5], linestyles[idx*5 +1:  (idx*5) + 5], canvas_d['scale'][idx*5 +1:  (idx*5) + 5]):
                    i.SetLineStyle(ls)
                    i.Draw("L same")
                    j.Draw("P same")
                    name = n 
                    if scale[0]!=1 : name =  str(scale[0]) + " #times " + n
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

                leg.Draw()
                c.Draw()
                c.Print(args.outf + "/" + op + "/" + op + "{}.pdf".format(idx))

        
    else:

        for op_pair in operators.keys():

            #mkdir(args.outf + "/" + op_pair)

            ops = op_pair.split("_")
            op_x = ops[0]
            op_y = ops[1]

            channels = operators[op_pair].keys()


            graphs = []

            for key in channels:
                gs, cont_graphs, exp = Retrieve2DLikelihood(operators[op_pair][key]['path'], 
                                                                [op_x, op_y], args.maxNLL, 
                                                                        1., 1. )

                cont_graphs[0].SetLineWidth(3)

                cont_graphs[0].SetLineColor(int(operators[op_pair][key]['color']))
                cont_graphs[0].SetLineStyle(int(operators[op_pair][key]['linestyle']))

                graphs.append([key, cont_graphs[0], exp])

            c = ROOT.TCanvas("c_{}".format(op_pair), "c_{}".format(op_pair), 1000, 1000)

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

            c.SetGrid()

            #first graph
            graphs[0][1].GetYaxis().SetTitleOffset(1.5)
            graphs[0][1].GetXaxis().SetTitleOffset(1.2)
            graphs[0][1].GetYaxis().SetTitle(ConvertOptoLatex(op_y))
            graphs[0][1].GetXaxis().SetTitle(ConvertOptoLatex(op_x))
            graphs[0][1].SetTitle("")
            #graphs[0][1].SetLineStyle(linestyles[0])
            graphs[0][1].Draw("AL")
            graphs[0][2].Draw("P same")

            name = graphs[0][0]
            leg.AddEntry(graphs[0][1], name, "L")

            for i in graphs[1:]:
                    i[1].Draw("L same")
                    i[2].Draw("P same")
                    name = i[0]
                    #if scale[0]!=1 : name =  str(scale[0]) + " #times " + n
                    leg.AddEntry(i[1], name, "L")

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

            leg.Draw()
            c.Draw()
            c.Print(args.outf + "/" + "_".join(i for i in channels) + "_" + op_pair + ".pdf")

