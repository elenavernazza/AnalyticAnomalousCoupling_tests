import os
import sys
import ROOT
import argparse
from glob import glob
from copy import deepcopy
import plotter.PlotManager as PM
import numpy as np
from array import array

def getLSintersections (graphScan, val):

    xings = []
    n = graphScan.GetN ()
    x = list(graphScan.GetX ())
    y = list(graphScan.GetY ())
    x, y = zip(*sorted(zip(x, y)))
    found = False

    for i in range(n):
        if (y[i] == val):
            xings.append(x[i])
            continue
        if i > 0:
            if ((y[i] - val) * (y[i-1] - val) < 0):
                xings.append(x[i-1] +  abs ((y[i-1] - val) * (x[i] - x[i-1]) / (y[i] - y[i-1])) )

    if len(xings) == 0:
        print("@ @ @ WARNING @ @ @: returning graph x-axis range limits")
        xings.append(graphScan.GetXaxis ().GetXmin ()) 
        xings.append(graphScan.GetXaxis ().GetXmax ())
    
    elif len(xings) == 1:
        if (xings[0] < 0):
            print("@ @ @ WARNING @ @ @: returning graph x-axis higher limit")
            xings.append(graphScan.GetXaxis().GetXmax ()) 
        else :
            print("@ @ @ WARNING @ @ @: returning graph x-axis lower limit")
            xings.append (xings[0])
            xings[0] = graphScan.GetXaxis ().GetXmin ()
            
    if len(xings) == 3:
        print("@ @ @ WARNING @ @ @: more not all intersections found, change range of the fit")
        xings = xings[:2]

    return xings


def convertName(name):
    d = {
        "deltaetajj": "#Delta#eta_{jj}",
        "deltaphijj": "#Delta#phi_{jj}",
        "deltaetaWZ": "#Delta#eta_{WZ}",
        "deltaphiWZ": "#Delta#phi_{WZ}",
        "Phiplanes" : "#Phi_{planes}",
        "ThetaWZ" : "#theta_{WZ}",
        "ThetalW" : "#theta_{lW}",
        "ThetalZ" : "#theta_{lZ}",
        "mll" : "m_{ll}",
        "mee" : "m_{ee}",
        "mjj" : "m_{jj}",
        "mWZ" : "m_{WZ}",
        "met" : "MET",
        "phij1" : "#phi_{j1}",
        "phij2" : "#phi_{j2}",
        "ptj1" : "p_{T,j1}",
        "ptj2" : "p_{T,j2}",
        "ptl1" : "p_{T,l1}",
        "ptl2" : "p_{T,l2}",
        "ptl3" : "p_{T,l3}",
        "ptll" : "p_{T,ll}",
        "ptee" : "p_{T,ee}",        
        "etaj1" : "#eta_{j1}",
        "etaj2" : "#eta_{j2}",
        "etal1" : "#eta_{l1}",
        "etal2" : "#eta_{l2}",
        "etal3" : "#eta_{l3}",
        " ": None
    }

    return d[name]

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
    parser.add_argument('--lumi',     dest='lumi',     help='Lumi', required = False, default="100")
    parser.add_argument('--o',     dest='o',     help='output folder', required = False, default="sensPlots")
    parser.add_argument('--ignore',     dest='ignore',     help='comma sep list of ignore variables', required = False, default="")
    parser.add_argument('--maxNLL',     dest='maxNLL',     help='NLL maximum sets precision of computation of intervals', required = False, default="100")
    parser.add_argument('--models',     dest='models',     help='Comma separated list of models: EFT,EFTNeg,EFTNeg-alt', required = False, default="EFT,EFTNeg,EFTNeg-alt")
    parser.add_argument('--prefix',     dest='prefix',     help='prefix of the subfolders, prefix_op', required = False, default="to_Latinos")
    parser.add_argument('--saveLL',     dest='saveLL',     help='Save likelihood plots or not, default is true', required = False, default=True, action = "store_false")
    parser.add_argument('--drawText',     dest='drawText',     help='Plot text of best variables in final plot', required = False, default=True, action = "store_false")
    parser.add_argument('--graphLimits',     dest='graphLimits',     help='comma separated list of final graph y axis limits, default is 2,2', required = False, default="2,2")

    args = parser.parse_args()

    ignore = args.ignore.split(",")
    mod = args.models.split(",")

    final_plot_y_min = -float(args.graphLimits.split(",")[0])
    final_plot_y_max = float(args.graphLimits.split(",")[1])

    ops = []
    limits = {}

    cpm = PM.CombinePlotManager()
    cpm.lumi = str(args.lumi + " fb^{-1}")

    cpm.generateAllBoxes()

    outputFolder = os.getcwd() + "/" + args.o
    mkdir(outputFolder)

    best = {}
    
    for model in mod:
        best[model] = {}
        best[model]["ops"] = []
        best[model]["best_var"]= []
        best[model]["one_s"] = []
        best[model]["two_s"] = []
        best[model]["best"] = []


    for dir in glob(args.baseFolder + "/*/"):

        process = dir.split("/")[-2]
        process = process.split(args.prefix + "_")[1]
        op = process.split("_")[-1]
        ops.append(op)
        process = process.split("_" + op)[0]

        print("\n\n")
        print(op)
        print("\n\n")

        mkdir(outputFolder + "/" + op)
        for model in mod:
            one_inf = []
            one_sup = []
            two_inf = []
            two_sup = []
            best_x = []
            best_y = []
            var = []
            x_counter = 0.5

            mkdir(outputFolder + "/" + op + "/" + model)
            if args.saveLL: mkdir(outputFolder + "/" + op + "/" + model + "/LLscans")

            for j,vars_ in enumerate(glob(dir + "/" + model + "/datacards/" + process + "_" + op + "/*/")) :

                viara = vars_.split("/")[-2]
                if viara in ignore:
                    print("@ @ @ Skipping {} @ @ @".format(viara))
                    continue

                ls_file = vars_ + "higgsCombineTest.MultiDimFit.mH125.root"
                if not os.path.isfile(ls_file): sys.exit("[ERROR] no fit for {}".format(vars_))

                f = ROOT.TFile(ls_file)
                t = f.Get("limit")
                
                print("@Retrieving likelihood...")
                to_draw = ROOT.TString("2*deltaNLL:{}".format("k_" + op))
                n = t.Draw( to_draw.Data() , "deltaNLL<{} && deltaNLL>{}".format(float(args.maxNLL),-30), "l")

                if n <= 1: 
                    print("[ATTENTION] no likelihood for {}".format(vars_))
                    print(np.ndarray((n), 'd', t.GetV2())[1:]) #removing first element (0,0)
                    continue

                
                x = np.ndarray((n), 'd', t.GetV2())[1:] #removing first element (0,0)
                y_ = np.ndarray((n), 'd', t.GetV1())[1:] #removing first element (0,0)

                x, ind = np.unique(x, return_index = True)
                y_ = y_[ind]
                y = np.array([i-min(y_) for i in y_]) #shifting likelihood toward 0

                graphScan = ROOT.TGraph(x.size,x,y)
                graphScan.GetXaxis().SetTitle(op)
                graphScan.GetYaxis().SetTitle("-2#DeltaLL")
                graphScan.SetTitle(viara)
                graphScan.SetLineColor(ROOT.kRed)
                graphScan.SetLineWidth(2)

                print("68 for {}".format(vars_))
                x_sixeight = getLSintersections(graphScan, 1.0)
                print("95 for {}".format(vars_))
                x_nintyfive = getLSintersections(graphScan, 3.84)

                if args.saveLL:

                    cs = ROOT.TCanvas("c_" + op + "_" + viara, "cs", 800, 800)
                    graphScan.Draw("AL")

                    min_x = graphScan.GetXaxis().GetXmin()
                    max_x = graphScan.GetXaxis().GetXmax()

                    o_sigma = ROOT.TLine(min_x, 1, max_x, 1)
                    o_sigma.SetLineStyle(2)
                    o_sigma.SetLineWidth(2)
                    o_sigma.SetLineColor(ROOT.kGray+2)
                    t_sigma = ROOT.TLine(min_x, 3.84, max_x, 3.84)
                    t_sigma.SetLineStyle(2)
                    t_sigma.SetLineWidth(2)
                    t_sigma.SetLineColor(ROOT.kGray+2)

                    o_sigma.Draw("L same")
                    t_sigma.Draw("L same")

                    os_ = ROOT.TLatex()
                    os_.SetTextFont(42)
                    os_.SetTextSize(0.035)
                    os_.DrawLatex(x_sixeight[1]+0.1, 1.05, '68%' )
                    ts = ROOT.TLatex()
                    ts.SetTextFont(42)
                    ts.SetTextSize(0.035)
                    ts.DrawLatex(x_nintyfive[1]+0.1, 3.89, '95%' )

                    if len(x_sixeight) > 2 :
                        os_.DrawLatex(x_sixeight[3]+0.1, 1.05, '68%' )
                    if len(x_nintyfive) > 2 :
                        ts.DrawLatex(x_nintyfive[3]+0.1, 3.89, '95%' )

                    cs.Draw()
                    cs.Print(outputFolder + "/" + op + "/" + model + "/LLscans/" + op + "_" + viara + ".png")

                if len(x_sixeight) == 2 and len(x_nintyfive) == 2:
                    one_inf.append(round(abs(x_sixeight[0]),4))
                    one_sup.append(round(abs(x_sixeight[1]),4))
                    two_inf.append(round(abs(x_nintyfive[0]),4))
                    two_sup.append(round(abs(x_nintyfive[1]),4))

                else :
                    if len(x_sixeight) > 2 and len(x_nintyfive) > 2 :
                        one_inf.append([round(x_sixeight[0],4),round(x_sixeight[2],4)])
                        one_sup.append([round(x_sixeight[1],4),round(x_sixeight[3],4)])
                        two_inf.append([round(x_nintyfive[0],4),round(x_nintyfive[2],4)])
                        two_sup.append([round(x_nintyfive[1],4),round(x_nintyfive[3],4)])
                    elif len(x_sixeight) > 2 and len(x_nintyfive) == 2 :
                        one_inf.append([round(x_sixeight[0],4),round(x_sixeight[2],4)])
                        one_sup.append([round(x_sixeight[1],4),round(x_sixeight[3],4)])
                        two_inf.append(round(abs(x_nintyfive[0]),4))
                        two_sup.append(round(abs(x_nintyfive[1]),4))
                    elif len(x_sixeight) == 2 and len(x_nintyfive) > 2 :
                        one_inf.append(round(abs(x_sixeight[0]),4))
                        one_sup.append(round(abs(x_sixeight[1]),4))
                        two_inf.append([round(x_nintyfive[0],4),round(x_nintyfive[2],4)])
                        two_sup.append([round(x_nintyfive[1],4),round(x_nintyfive[3],4)])

                best_x.append(x_counter)
                best_y.append(0)
                var.append(vars_.split("/")[-2])

                x_counter += 1

                f.Close()


            c = ROOT.TCanvas("c", "c", 800, 600)
            c.SetGrid()
            leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

            margins = 0.11
            ROOT.gPad.SetRightMargin(margins)
            ROOT.gPad.SetLeftMargin(margins)
            ROOT.gPad.SetBottomMargin(margins)
            ROOT.gPad.SetTopMargin(margins)
            ROOT.gPad.SetFrameLineWidth(3)

            if not len(best_x)  > 0 or not len(best_y) > 0: continue

            g1 = ROOT.TGraphAsymmErrors()
            g11 = ROOT.TGraphAsymmErrors()
            g2 = ROOT.TGraphAsymmErrors()
            g21 = ROOT.TGraphAsymmErrors()
            k = 0
            l = 0
            for j in range(len(best_x)) :
                ex = 0.16
                if type(one_inf[j]) == float :
                    g1.SetPoint(j, best_x[j], best_y[j])
                    g1.SetPointError(j, ex, ex, one_inf[j], one_sup[j])
                elif len(one_inf[j]) > 1 :
                    if abs(one_inf[j][0]) < abs(one_inf[j][1]) :
                        first = 0
                        second = 1
                    elif abs(one_inf[j][0]) > abs(one_inf[j][1]) :
                        first = 1
                        second = 0
                    g1.SetPoint(j, best_x[j], best_y[j])
                    g1.SetPointError(j, ex, ex, abs(one_inf[j][first]), abs(one_sup[j][first]))
                    c1 = (one_sup[j][second] + one_inf[j][second])/2
                    g11.SetPoint(k, best_x[j], c1)
                    g11.SetPointError(k, ex, ex, abs(one_inf[j][second]-c1), abs(one_sup[j][second]-c1))
                    k = k + 1

                if type(two_inf[j]) == float :
                    g2.SetPoint(j, best_x[j], best_y[j])
                    g2.SetPointError(j, ex, ex, two_inf[j], two_sup[j])
                elif len(two_inf[j]) > 1 :
                    if abs(two_inf[j][0]) < abs(two_inf[j][1]) :
                        first = 0
                        second = 1
                    elif abs(two_inf[j][0]) > abs(two_inf[j][1]) :
                        first = 1
                        second = 0
                    g2.SetPoint(j, best_x[j], best_y[j])
                    g2.SetPointError(j, ex, ex, abs(two_inf[j][first]), abs(two_sup[j][first]))
                    c2 = (two_sup[j][second] + two_inf[j][second])/2
                    g21.SetPoint(l, best_x[j], c2)
                    g21.SetPointError(l, ex, ex, abs(two_inf[j][second]-c2), abs(two_sup[j][second]-c2))
                    l = l + 1

            g1.SetMinimum(-10)
            g1.SetMaximum(15)
            g1.SetFillColor(ROOT.kOrange)
            g1.SetLineColor(ROOT.kOrange)
            g1.SetLineWidth(0)
            g1.SetMarkerStyle(24)
            g1.SetMarkerColor(ROOT.kBlue+1)
            g1.SetMarkerSize(2)
            g1.GetYaxis().SetRangeUser(-10,10)

            g11.SetMinimum(-10)
            g11.SetMaximum(15)
            g11.SetFillColor(ROOT.kOrange)
            g11.SetLineColor(ROOT.kOrange)
            g11.SetLineWidth(0)

            g2.SetFillColor(ROOT.kGreen+1)
            g2.SetLineWidth(0)
            g2.SetMarkerStyle(24)
            g2.SetMarkerColor(ROOT.kBlue+1)
            g2.SetMarkerSize(2)
            g2.GetYaxis().SetRangeUser(-15,15)

            g21.SetMinimum(-10)
            g21.SetMaximum(15)
            g21.SetFillColor(ROOT.kGreen+1)
            g21.SetLineColor(ROOT.kGreen+1)
            g21.SetLineWidth(0)

            leg.AddEntry(g1, "#pm 1#sigma Expected", "F")
            leg.AddEntry(g2, "#pm 2#sigma Expected", "F")
            leg.AddEntry(g1, "Best Fit", "P")
            leg.SetHeader("Operator: " + op)
            leg.SetBorderSize(2)

            h = ROOT.TH1F("h", "h", len(best_x)+2, -1, len(best_x)+1)
            h.SetFillColor(0)
            h.SetCanExtend(ROOT.TH1.kAllAxes)
            h.SetStats(0)
    
            for idx in  range(-1, h.GetNbinsX()):
                if idx == 0: h.GetXaxis().SetBinLabel(idx + 1, "")
                if idx < len(var)+1 and idx > 0: h.GetXaxis().SetBinLabel(idx + 1, convertName(var[idx - 1]))
                else: h.GetXaxis().SetBinLabel(idx + 1, "")
            h.GetYaxis().SetTitle(op + " Estimate")

            ROOT.gStyle.SetLabelSize(.05, "XY")

            max_ = 0
            min_ = 0
            for j in range(len(two_sup)) :
                if type(two_sup[j]) == float :
                    if two_sup[j] > max_ :
                        max_ = two_sup[j]
                elif len(two_sup[j]) > 1 :
                    ts = max(two_sup[j][0],two_sup[j][1])
                    if ts > max_ :
                        max_ = ts
                if type(two_inf[j]) == float :
                    if -1*two_inf[j] < min_ :
                        min_ = -1*two_inf[j]
                elif len(two_inf[j]) > 1 :
                    ti = min(two_inf[j][0],two_inf[j][1])
                    if ti < min_ :
                        min_ = ti

            best_v = 1000
            best_index = 0
            count = 0
            #best variable in 68% range + 95% range / 2
            # for k,z,l,m in zip(one_inf, one_sup, two_inf, two_sup):
            #     if (k+z+l+m)/2 < best_v:
            #         best_v = (k+z+l+m)/2
            #         best_index = count
            #     count += 1
            for k1,z1 in zip(two_inf, two_sup):
                if type(k1) == float :
                    k = k1
                if type(z1) == float :
                    z = z1
                elif len(k1) > 1 :
                    k = abs(z1[0] - k1[0])
                    z = abs(z1[1] - k1[1])
                if k+z < best_v:
                    best_v = k+z
                    best_index = count
                count += 1

            best[model]["ops"].append(op)
            best[model]["best_var"].append(var[best_index])
            if type(one_inf[best_index]) == float :
                best[model]["one_s"].append([-1*one_inf[best_index], one_sup[best_index]])
            elif len(one_inf[best_index]) > 1 :
                vec_1 = [[one_inf[best_index][0],one_sup[best_index][0]], [one_inf[best_index][1],one_sup[best_index][1]]]
                best[model]["one_s"].append(vec_1)
            if type(two_inf[best_index]) == float :
                best[model]["two_s"].append([-1*two_inf[best_index], two_sup[best_index]])
            elif len(two_inf[best_index]) > 1 :
                vec_2 = [[two_inf[best_index][0],two_sup[best_index][0]], [two_inf[best_index][1],two_sup[best_index][1]]]
                best[model]["two_s"].append(vec_2)
            best[model]["best"].append([0,0])

            #print("@[INFO] Best Var: {} for model: {}".format(var[best_index], model))

            h.LabelsDeflate("X")
            h.LabelsDeflate("Y")
            h.LabelsOption("v")

            ROOT.gStyle.SetLabelSize(.05, "XY")

            range_ = max_ - min_ 
            h.GetYaxis().SetRangeUser(min_-0.05*range_,max_+0.35*range_)

            ROOT.gStyle.SetOptStat(0)          

            h.Draw("AXIS")
            c.SetGrid()
            ROOT.gPad.RedrawAxis("g")
            g2.Draw("2 same")
            g1.Draw("2 same")
            g1.Draw("P same")

            g21.Draw("2 same")
            g11.Draw("2 same")

            c.SetTicks()
            leg.Draw()

            for item in cpm.optionals:
                item.Draw("same")

            c.Draw()
            c.Print(outputFolder + "/" + op + "/" + model + "/sensitivity_" + op + ".png")
    
    #open txt file to store results
    f_out = open(outputFolder + "/results.txt", "w")
    for model in best.keys():

        c = ROOT.TCanvas("c", "c", 800, 600)
        c.SetGrid()
        leg = ROOT.TLegend(0.15, 0.85, 0.4, 0.7)

        margins = 0.11
        ROOT.gPad.SetRightMargin(margins)
        ROOT.gPad.SetLeftMargin(margins)
        ROOT.gPad.SetBottomMargin(margins)
        ROOT.gPad.SetTopMargin(margins)
        ROOT.gPad.SetFrameLineWidth(3)

        vars_ = best[model]["best_var"]
        ops = best[model]["ops"]
        one_s = best[model]["one_s"]
        two_s = best[model]["two_s"]
        best_fit = best[model]["best"]

        one_s, two_s, ops, best_fit, vars_ = zip(*sorted(zip(one_s, two_s, ops, best_fit, vars_),reverse=True))

         #saving results to txt
        print("[MODEL RESULTS] {}".format(model))
        f_out.write("[MODEL RESULTS] {}\n".format(model))
        f_out.write("op \t best var \t 1 sigma \t 2 sigma\n")
        for v, o, os, ts in zip(vars_, ops, one_s, two_s):
            print("{} \t  {} \t [{},{}] \t [{},{}]".format(o,v,os[0],os[1],ts[0],ts[1]))
            f_out.write("{} \t  {} \t [{},{}] \t [{},{}]\n".format(o,v,os[0],os[1],ts[0],ts[1]))
        
        f_out.write("\n\n")     

        xs = []
        ys = []

        base = 0.5
        for j in range(len(best_fit)):
            xs.append(j+base)
            ys.append(0)

        g1 = ROOT.TGraphAsymmErrors()
        g11 = ROOT.TGraphAsymmErrors()
        g2 = ROOT.TGraphAsymmErrors()
        g21 = ROOT.TGraphAsymmErrors()
        k = 0
        l = 0
        for j in range(len(xs)) :
            ex = 0.16
            if type(one_s[j][0]) == float :
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s[j][0]), abs(one_s[j][1]))
            else :
                if abs(one_s[j][0][0]) < abs(one_s[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g1.SetPoint(j, xs[j], ys[j])
                g1.SetPointError(j, ex, ex, abs(one_s[j][first][0]), abs(one_s[j][first][1]))
                c1 = (one_s[j][second][1] + one_s[j][second][0])/2
                g11.SetPoint(k, xs[j], c1)
                g11.SetPointError(k, ex, ex, abs(one_s[j][second][0]-c1), abs(one_s[j][second][1]-c1))
                k = k + 1

            if type(two_s[j][0]) == float :
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s[j][0]), abs(two_s[j][1]))
            else :
                if abs(two_s[j][0][0]) < abs(two_s[j][1][0]) :
                    first = 0
                    second = 1
                else :
                    first = 1
                    second = 0
                g2.SetPoint(j, xs[j], ys[j])
                g2.SetPointError(j, ex, ex, abs(two_s[j][first][0]), abs(two_s[j][first][1]))
                c2 = (two_s[j][second][1] + two_s[j][second][0])/2
                g21.SetPoint(l, xs[j], c2)
                g21.SetPointError(l, ex, ex, abs(two_s[j][second][0]-c2), abs(two_s[j][second][1]-c2))
                l = l + 1

        g1.SetMinimum(-10)
        g1.SetMaximum(15)
        g1.SetFillColor(ROOT.kOrange)
        g1.SetLineColor(ROOT.kOrange)
        g1.SetLineWidth(0)
        g1.SetMarkerStyle(24)
        g1.SetMarkerColor(ROOT.kBlue+1)
        g1.SetMarkerSize(2)
        g1.GetYaxis().SetRangeUser(-10,10)

        g11.SetMinimum(-10)
        g11.SetMaximum(15)
        g11.SetFillColor(ROOT.kOrange)
        g11.SetLineColor(ROOT.kOrange)
        g11.SetLineWidth(0)

        g2.SetFillColor(ROOT.kGreen+1)
        g2.SetLineWidth(0)
        g2.SetMarkerStyle(24)
        g2.SetMarkerColor(ROOT.kBlue+1)
        g2.SetMarkerSize(2)
        g2.GetYaxis().SetRangeUser(-15,15)

        g21.SetMinimum(-10)
        g21.SetMaximum(15)
        g21.SetFillColor(ROOT.kGreen+1)
        g21.SetLineColor(ROOT.kGreen+1)
        g21.SetLineWidth(0)

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

        g21.Draw("2 same")
        g11.Draw("2 same")

        c.SetTicks()
        leg.Draw()

        for item in cpm.optionals:
            item.Draw("same")

        if args.drawText:
            count = 0
            for x in xs:
                y = max_
                y_ = y + 0.5
                #do not plot if the text pass the plot boundaries
                if y_ > final_plot_y_max - 0.1: continue
                var = vars_[count]
                count += 1
                latex = ROOT.TLatex()
                latex.SetTextSize(0.025)
                latex.SetTextAlign(12)
                latex.DrawLatex(x-0.14 - 0.02*len(convertName(var)),y_,"{}".format(convertName(var)))


#        c.Draw()
        c.Print(outputFolder + "/" + "{}.pdf".format(model))

    f_out.close()
  
