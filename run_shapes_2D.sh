mkdir $2
mkdir $2/$3_$4_shapes

min=-1
max=1
step=0.5

if [ $# -gt 4 ] 
then 
   min=$5 
fi
if [ $# -gt 5 ] 
then 
   max=$6 
fi
if [ $# -gt 6 ] 
then
   step=$7 
fi
echo $max
echo $min
echo $step

#path_to_shapes #xtitle #outputfolder #outputfile #model #k_min(none) #k_max(none) #step(none)

#EFT
python plot_shapes_2D.py $1/EFT/datacards/$3/deltaphijj/shapes/histos_$3.root "#Delta#phi_{jj}" $2/$3_$4_shapes/$4_deltaphijj.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/deltaetajj/shapes/histos_$3.root "#Delta#eta_{jj}" $2/$3_$4_shapes/$4_deltaetajj.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/met/shapes/histos_$3.root "MET [GeV]" $2/$3_$4_shapes/$4_met.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/mll/shapes/histos_$3.root "m_{ll} [GeV]" $2/$3_$4_shapes/$4_mll.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/mjj/shapes/histos_$3.root "m_{jj} [GeV]" $2/$3_$4_shapes/$4_mjj.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/phij1/shapes/histos_$3.root "phi_{j1}" $2/$3_$4_shapes/$4_phij1.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/phij2/shapes/histos_$3.root "phi_{j2}" $2/$3_$4_shapes/$4_phij2.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/ptj1/shapes/histos_$3.root "p_{T,j1} [GeV]" $2/$3_$4_shapes/$4_ptj1.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/ptj2/shapes/histos_$3.root "p_{T,j2} [GeV]" $2/$3_$4_shapes/$4_ptj2.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/ptl1/shapes/histos_$3.root "p_{T,l1} [GeV]" $2/$3_$4_shapes/$4_ptl1.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/ptl2/shapes/histos_$3.root "p_{T,l2} [GeV]" $2/$3_$4_shapes/$4_ptl2.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/ptll/shapes/histos_$3.root "p_{T,ll} [GeV]" $2/$3_$4_shapes/$4_ptll.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/etaj1/shapes/histos_$3.root "#eta_{j1}" $2/$3_$4_shapes/$4_etaj1.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/etaj2/shapes/histos_$3.root "#eta_{j2}" $2/$3_$4_shapes/$4_etaj2.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/etal1/shapes/histos_$3.root "#eta_{l1}" $2/$3_$4_shapes/$4_etal1.png $min $max $step $4
python plot_shapes_2D.py $1/EFT/datacards/$3/etal2/shapes/histos_$3.root "#eta_{l2}" $2/$3_$4_shapes/$4_etal2.png $min $max $step $4
