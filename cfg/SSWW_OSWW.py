combinations["SSWW"] = {
       
       'folder' : 'SSWW_1op_nuis102',
       'vars' : '*',
       'prefix' : 'to_Latinos',
       'models' : ["EFTNeg"],
       'datacard_tag' : 'datacard',
       'ignore_ops' : [],
       'ignore_vars' : ['etal1','etal2','phij1','phij2', 'etaj1', 'etaj2', 'ptll']
}

combinations["OSWW"] = {
       
       'folder' : 'OSWW_1op',
       'vars' : '*',
       'prefix' : 'to_Latinos',
       'models' : ["EFTNeg"],
       'datacard_tag' : 'datacard',
       'ignore_ops' : [],
       'ignore_vars' : ['etal1','etal2','phij1','phij2', 'etaj1', 'etaj2', 'ptll']
}

combinations["inWW"] = {
       
       'folder' : 'inWW_1op',
       'vars' : '*',
       'prefix' : 'to_Latinos',
       'models' : ["EFTNeg"],
       'datacard_tag' : 'datacard',
       'ignore_ops' : [],
       'ignore_vars' : ['etal1','etal2','phij1','phij2', 'etaj1', 'etaj2', 'ptll']
}
combinations["OSWWQCD"] = {
       
       'folder' : 'OSWWQCD_1op',
       'vars' : '*',
       'prefix' : 'to_Latinos',
       'models' : ["EFTNeg"],
       'datacard_tag' : 'datacard',
       'ignore_ops' : [],
       'ignore_vars' : ['etal1','etal2','phij1','phij2', 'etaj1', 'etaj2', 'ptll']
}

output["name"] = "SSWW_OSWW_inWW_OSWWQCD"
output["prefix"] = "combination"
output["models"] = ["EFTNeg"]
