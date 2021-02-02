from glob import glob
import os
import argparse

def mkdir(p):
   try:
      os.mkdir(p)
   except:
      return 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Command line parser for model testing')
    parser.add_argument('--b',     dest='b',     help='Base folder e.g. OSWW_1op', required = True)
    parser.add_argument('--t',     dest='t',     help='the txt with the results after varsens', required = True)
    parser.add_argument('--pn',     dest='pn',     help='process name (folder after datacards in basefolder)', required = True)
    parser.add_argument('--m',     dest='m',     help='process name (folder after datacards in basefolder)', required = False, default = "EFTNeg")
    parser.add_argument('--o',     dest='o',     help='output folder name', required = False)
    parser.add_argument('--pr',     dest='pr',     help='base folder prefix name', required = False, default = "to_Latinos")
    args = parser.parse_args()
    
    subf = glob("{}/*/".format(args.b))
    outf = args.o
    if outf == None:
       outf = args.b + "_best"
    
    os.mkdir(outf) 
    #reading the txt
    
    f = open(args.t, 'r')
    
    
    content = f.readlines()
   
    best = {}
   
    for lines in content:
      if "[MODEL RESULTS]" in lines:
        model = (lines.split("[MODEL RESULTS] ")[1]).strip("\n")
        best[model] = {}
      elif "c" in lines:
        parts = lines.split("\t")
        parts = [i.strip(" ") for i in parts]
        op = parts[0].replace(" ", "_")
        
        best[model][op] = parts[1].strip(" ")
    
    for s in subf:
      f_name = s.split("/")[-2]
      ops = f_name.split(args.pr+ "_" + args.pn + "_")[1]
      
      for model in args.m.split(","):
        try:
          best_v = best[model][ops]
        except:
          ops_temp = ops.split("_")
          print(ops_temp)
          ops_temp = "_".join(i for i in ops_temp[::-1])
          best_v = best[model][ops_temp]

        mkdir(outf + "/" + f_name)
        mkdir(outf + "/" + f_name + "/" + model)
        mkdir(outf + "/" + f_name + "/{}/datacards".format(model) )
        mkdir(outf + "/" + f_name + "/{}/datacards/{}_".format(model, args.pn) + ops )
    	mkdir(outf + "/" + f_name + "/{}/datacards/{}_".format(model, args.pn) + ops + "/" + best_v)
        os.system("cp -r {}/* {}".format(s + "/{}/datacards/{}_".format(model, args.pn) + ops + "/" + best_v, outf + "/" + f_name + "/{}/datacards/{}_".format(model, args.pn) + ops + "/" + best_v))

