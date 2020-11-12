from fnmatch import fnmatch
import sys
import copy
from itertools import combinations

class CombUtils:

    def writeln (self, f, txt):
        f.write(txt + '\n')
        return

    def writelnarr(self, f, txtarr, align='{:>12}', firstAlign = '{:<12}', secondAlign = '{:<6}', addEmptyAtIdx = None):
        if addEmptyAtIdx:
            txtarr = txtarr[0:addEmptyAtIdx] + [''] + txtarr[addEmptyAtIdx:]
        str_proto = ''
        for idx, txt in enumerate(txtarr):
            str_proto += '%s ' % (firstAlign if idx == 0 else secondAlign if idx == 1 else align)
        str_proto = str_proto[:-1] ## remove trailing space
        the_str = str_proto.format(*txtarr)
        self.writeln(f, the_str)

        return

    def affects(self, processes, syst):
        for proc in processes:
            for sys in syst:
                if fnmatch(proc, sys):
                    return True
        return False

    def makedatacard(self, ops_dict, sys_dict, card_name="out.txt", obs=100):

        print(ops_dict)
        print(sys_dict)
        print(card_name)
        fcard = open(card_name, 'w')

        self.writeln    (fcard, 'imax *  number of channels')
        self.writeln    (fcard, 'jmax *  number of backgrounds')
        self.writeln    (fcard, 'kmax *  number of nuisance parameters (sources of systematical uncertainties)')
        self.writeln    (fcard, '----------------------------------------------------------------------------------------------------------------------------------')
        
        ## observation
        self.writelnarr (fcard, ('bin', 'test'))
        self.writelnarr (fcard, ('observation', '%.0f' % obs))
        self.writeln    (fcard, '----------------------------------------------------------------------------------------------------------------------------------')
        self.writeln    (fcard, '# list the expected events for signal and all backgrounds in that bin')
        self.writeln    (fcard, '# the second process line must have a positive number for backgrounds, and 0 or neg for signal')

        n_comp = len(ops_dict["Name"])

        #rates
        self.writelnarr (fcard, ['bin'] + (['test',]*n_comp) , addEmptyAtIdx=1)
        self.writelnarr (fcard, ['process'] + ops_dict["Name"] ,  addEmptyAtIdx=1)
        self.writelnarr (fcard, ['process'] + ops_dict["Type"], addEmptyAtIdx=1)
        self.writelnarr (fcard, ['rate'] + ["%.6f" % r for r in ops_dict["Rate"]], addEmptyAtIdx=1)
        self.writeln    (fcard, '----------------------------------------------------------------------------------------------------------------------------------')

        #Systematics

        for syst_source in sys_dict.keys():
            processes = []
            sytype = sys_dict[syst_source][0]
            elemts = sys_dict[syst_source][1:]

            line_tokens = [syst_source, sytype]

            if self.affects(ops_dict["Name"], elemts): continue

            for proc in ops_dict["Name"]:
                iaffect = []
                for idx, el in enumerate(elemts):
                    if fnmatch(proc, el[0]):
                        iaffect.append(idx)

                if len(iaffect) == 0:
                    line_tokens.append('-')
                else:
                    if len(iaffect) > 1:
                        print ">> [WARNING] << process", proc, "matches twice the syst source", syst_source, ', using the 1st occurrence'
                    the_idx = iaffect[0]
                    line_tokens.append(elemts[the_idx][1])
                    
            self.writelnarr (fcard, line_tokens)

        return


    def EFT(self, ops):
        """
            Creates dummy EFT dict with as many op as you want (SM, Lin, Quad, Mixed)
        """

        data_dict_EFT = {"Nops": len(ops), "Name": None, "Rate": None, "Type": None}
        data_dict_EFT["Nops"] = len(ops)

        #sm = randrange(30,200) #30, 80 counts for sm... Arbitrary maximum 
        sm = 30
        names_eft = []
        rates_eft = []
        type_ = []

        names_eft.append("sm")
        rates_eft.append(sm)
        type_.append(0)

        #operator specific
        idx = 1
        for op in ops:
            
            #quad = randrange(1,10)
            quad = 2
            names_eft.append("quad_{}".format(op))
            rates_eft.append(quad)
            type_.append(idx)
            idx+=1

            #lin = randrange(1,10)
            lin = 1
            names_eft.append("lin_{}".format(op))
            rates_eft.append(lin)
            type_.append(idx)
            idx+=1

        #mixing 
        for i,j in combinations(ops, 2):
            #mix = randrange(1,10)
            mix = 1
            names_eft.append("lin_mixed_{}_{}".format(i,j))
            rates_eft.append(mix)
            type_.append(idx)
            idx+=1

        data_dict_EFT["Name"] = names_eft
        data_dict_EFT["Rate"] = rates_eft
        data_dict_EFT["Type"] = type_

        return data_dict_EFT


    def EFTNegative(self, full_dict, ops, alt = False):
        """
            The dict to build the datacard to test the negative model
            starts from the dict output from EFT...This may be redundant
        """

        sm = full_dict["Rate"][0]
        new_dict = copy.deepcopy(full_dict)

        if not alt:
            
            for op in ops:
                lin_idx = full_dict["Name"].index("lin_{}".format(op))
                quad_idx = full_dict["Name"].index("quad_{}".format(op))
                new_dict["Name"][lin_idx] = "sm_lin_quad_{}".format(op)
                new_dict["Rate"][lin_idx] = sm + full_dict["Rate"][lin_idx] + full_dict["Rate"][quad_idx]
            
            
            #mixing  -> s + l + l + q + q + M
            for i,j in combinations(ops, 2):
                lin_1 = full_dict["Name"].index("lin_{}".format(i))
                quad_1 = full_dict["Name"].index("quad_{}".format(i))
                lin_2 = full_dict["Name"].index("lin_{}".format(j))
                quad_2 = full_dict["Name"].index("quad_{}".format(j))
                mij =  full_dict["Name"].index("lin_mixed_{}_{}".format(i,j))

                new_dict["Name"][mij] = "sm_lin_quad_mixed_{}_{}".format(i,j)
                new_dict["Rate"][mij] = sm + full_dict["Rate"][lin_1] + full_dict["Rate"][quad_1] + \
                                            full_dict["Rate"][lin_2] + full_dict["Rate"][quad_2] + full_dict["Rate"][mij]

        else:

            for op in ops:
                lin_idx = full_dict["Name"].index("lin_{}".format(op))
                quad_idx = full_dict["Name"].index("quad_{}".format(op))
                new_dict["Name"][lin_idx] = "sm_lin_quad_{}".format(op)
                new_dict["Rate"][lin_idx] = sm + full_dict["Rate"][lin_idx] + full_dict["Rate"][quad_idx]

            #mixing  -> q + q + M
            for i,j in combinations(ops, 2):
                quad_1 = full_dict["Name"].index("quad_{}".format(i))
                quad_2 = full_dict["Name"].index("quad_{}".format(j))
                mij =  full_dict["Name"].index("lin_mixed_{}_{}".format(i,j))

                new_dict["Name"][mij] = "quad_mixed_{}_{}".format(i,j)
                new_dict["Rate"][mij] = full_dict["Rate"][quad_1] + full_dict["Rate"][quad_2] + full_dict["Rate"][mij]


        return new_dict

    def addBkg(self, dict_, count=100):
        
        dict_["Name"].append("others")
        dict_["Rate"].append(count)
        dict_["Type"].append(dict_["Type"][-1]+1)

        return dict_



    def t2w(self, d_name, ops, model = "EFT", alt=False, out="model_test.root"):
        if model != "EFT" and model != "EFTNegative": sys.exit("[ERROR] Wrong EFT model")
        if model == "EFT":
            t2w_ = "text2workspace.py {} -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCoupling{}:analiticAnomalousCoupling{} \
                    --X-allow-no-signal -o {} --PO eftOperators=".format(d_name, model, model, out)

            #for op in ops: t2w_ +=  "," + "k_" + op
            for op in ops: t2w_ +=  op + ","
            t2w_ = t2w_[:-1]
        else:
            t2w_ = "text2workspace.py {} -P HiggsAnalysis.AnalyticAnomalousCoupling.AnomalousCoupling{}:analiticAnomalousCoupling{} \
                -o model_test.root --X-allow-no-signal -o {} --PO eftOperators=".format(d_name, model, model, out)
        
            for op in ops: t2w_ +=  op + ","
            t2w_ = t2w_[:-1]

            if alt: t2w_ += " --PO eftAlternative"

        return t2w_

    def comb(self, ops, fit, range_, npoints=2000, root = "model_test.root"):
        
        if len(fit) == 0: sys.exit("[ERROR] No fit parameter...")

        comb = "combine -M MultiDimFit {}  --algo=grid --points {}  -m 125   -t -1 --verbose -1 ".format(root, npoints)
        pp   =  "  --redefineSignalPOIs "
        fp   = " --freezeParameters r"
        sp   = " --setParameters r=1"

        for op in ops: 
            if op in fit:
                pp += "k_" + str(op) + ","
            else:
                fp += ",k_" + str(op)
                sp += ",k_" + str(op) + "=0"
        


        comb += pp[:-1] + fp + sp + " --setParameterRanges {}".format(range_)

        return comb

        



