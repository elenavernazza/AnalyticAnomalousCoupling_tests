import ROOT
import argparse
import numpy as np 

parser = argparse.ArgumentParser(description='Command line parser for model testing')
parser.add_argument('--rf',     dest='rf',     help='Result file .txt', required = True)
parser.add_argument('--m',     dest='m',     help='models default ETNeg', required = False, default="EFTNeg")
parser.add_argument('--lumi',     dest='lumi',     help='Lumi to plot', required = False, default="100")

args = parser.parse_args()

f = open(args.rf, 'r')
contents = f.readlines()
f.close()

contents = [i.strip("\n") for i in contents]
contents.pop(1)

print(contents)


models = args.m.split(',')


for model in models:
    try:
        start = contents.index("[MODEL RESULTS] {}".format(model))
    except:
        print("[ERROR] model {} not in results ... ".format(model))
        continue

    i = start + 1
    ops = []
    best_v = []
    area_1 = []
    area_2 = []
    while "[MODEL RESULTS]" not in contents[i]:
        line = contents[i]
        print(line)
        #ops, best var, 1s, 2s
        line = line.split("\t")
        line = [j.strip(" ") for j in line]
        if len(line) > 1: #avoid empty lines at the end of file
            ops.append(line[0])
            best_v.append(line[1])
            os = [float(j) for j in line[2][1:-1].split(',')]
            area_1.append(abs(os[0]) + abs(os[1]))
            ts = [float(j) for j in line[3][1:-1].split(',')]
            area_2.append(abs(ts[0]) + abs(ts[1]))
        i+=1

        if i == len(contents): break

    area_1.reverse()
    area_2.reverse()
    best_v.reverse()
    ops.reverse()
    print(ops)

    log_splits = [0, 1, 11, 100, 1000, 10000]
    histos_splits_stacked = []
    leg = ROOT.TLegend(0.95, 0.95, 0.75, 0.8)
    leg.SetBorderSize(1)

    for l_i in range(len(log_splits)-1):
        ar1_ = []
        ar2_ = []
        op_ = []
        for ao, at, o in zip(area_1, area_2, ops):
            if at <= log_splits[l_i + 1] and at > log_splits[l_i]:
                ar1_.append(ao)
                ar2_.append(at)
                op_.append(o)

        if len(ar1_) != 0:

            h_1 = ROOT.TH1F("h1_{}".format(log_splits[l_i]), "h1", len(ar1_), 0, len(ar1_))
            h_1.SetBarWidth(0.75)
            for b in range(1, h_1.GetNbinsX()+1):
                h_1.SetBinContent(b, ar1_[b-1])
                h_1.GetXaxis().SetBinLabel(b, op_[b-1])

            h_1.SetMinimum()

            h_2 = ROOT.TH1F("h2_{}".format(log_splits[l_i]), "h2", len(ar2_), 0, len(ar2_) )
            h_2.SetBarWidth(0.75)
            for b in range(1, h_2.GetNbinsX()+1):
                h_2.SetBinContent(b, ar2_[b-1] - ar1_[b-1])
                h_2.GetXaxis().SetBinLabel(b, op_[b-1])

            h_2.SetMinimum()

            #h_2.SetFillColor(ROOT.kGreen+1)
            #h_2.SetLineColor(ROOT.kGreen+1)
            h_2.SetFillColor(ROOT.kAzure+7)
            h_2.SetLineColor(ROOT.kAzure+7)
            h_2.SetMarkerStyle(0)
            h_2.SetMarkerColor(0)

            #h_1.SetFillColor(ROOT.kOrange)
            #h_1.SetLineColor(ROOT.kOrange)
            h_1.SetFillColor(ROOT.kViolet)
            h_1.SetLineColor(ROOT.kViolet)
            h_1.SetMarkerStyle(0)
            h_1.SetMarkerColor(0)

            stack = ROOT.THStack("stack_{}".format(log_splits[l_i]), "")
            stack.Add(h_1)
            stack.Add(h_2)

            histos_splits_stacked.append(stack)

        else: continue

        if l_i == 0:
            leg.AddEntry(h_1, "#pm 1#sigma C.L", "F")
            leg.AddEntry(h_2, "#pm 2#sigma C.L", "F")

    c_length = 900*len(histos_splits_stacked)
    c_height = 1200
    c = ROOT.TCanvas("c_{}".format(model), "c", c_height, c_length)
    ROOT.gPad.SetTopMargin(0.15)
    c.Divide(1, len(histos_splits_stacked), 0., 0.)

    tex = ROOT.TLatex(0.13,.99 - (float(6)/len(histos_splits_stacked)-1)/100,"CMS")
    tex.SetNDC()
    tex.SetTextFont(61)
    tex.SetTextSize(0.05)
    tex.SetLineWidth(2)
    tex.SetTextAlign(13)
    tex.Draw()

    tex2 = ROOT.TLatex  (0.25, .987 - (float(6)/len(histos_splits_stacked)-1)/80, "Preliminary")
    tex2.SetNDC()
    tex2.SetTextSize(0.76 * 0.05)
    tex2.SetTextFont(52)
    tex2.SetTextColor(ROOT.kBlack)
    tex2.SetTextAlign(13)
    tex2.Draw()

    tex3 = ROOT.TLatex(0.9,.978 - (float(6)/len(histos_splits_stacked)-1)/60,"(13 TeV)")
    tex3.SetNDC()
    tex3.SetTextAlign(31)
    tex3.SetTextFont(42)
    tex3.SetTextSize(0.04)
    tex3.SetLineWidth(2)
    tex3.Draw()

    tex4 = ROOT.TLatex(0.75,.978 - (float(6)/len(histos_splits_stacked)-1)/60, args.lumi + " fb^{-1}")
    tex4.SetNDC()
    tex4.SetTextAlign(31)
    tex4.SetTextFont(42)
    tex4.SetTextSize(0.04)
    tex4.SetLineWidth(2)
    tex4.Draw()

    lines = []
    for i in range(1, len(histos_splits_stacked)+1):
        c.cd(i)  
        ROOT.gStyle.SetGridWidth(1)
        ROOT.gStyle.SetGridColor(ROOT.kGray)
        c.cd(i).SetGrid()   
        c.cd(i).SetBottomMargin(0.1)
        ROOT.gPad.SetLeftMargin(0.15)
        histos_splits_stacked[i-1].Draw("hbar")
        leg.Draw()
        ROOT.gPad.Update()
        #lines to draw on top of the frame
        tl_h = ROOT.TLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymax(),
                         ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymax())
        tl_l = ROOT.TLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymin(),
                         ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymin())
        tl_left = ROOT.TLine(ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymin(),
                         ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymax())
        tl_right = ROOT.TLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymin(),
                         ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymax())

        lines.append([tl_h, tl_l, tl_left, tl_right])

    for i in range(1, len(histos_splits_stacked)+1):
        c.cd(i)
        for it in lines[i-1]:
            it.Draw()

    c.Modified()
    c.Update()
    c.Draw()
    c.Print("{}.pdf".format(model))