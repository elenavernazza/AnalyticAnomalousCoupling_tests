mkdir ShapesPlots
mkdir ShapesPlots/$2_EFT_shapes

min=-1
max=1
step=0.5

if [ $# -gt 2 ] 
then 
   min=$3 
fi
if [ $# -gt 3 ] 
then 
   max=$4 
fi
if [ $# -gt 4 ] 
then
   echo "Ciao" 
   step=$5 
fi
echo $max
echo $min
echo $step

#path_to_shapes #xtitle #outputfile #k_min(none) #k_max(none) #step(none)

#EFT
python plot_shapes.py $1/EFT/datacards/$2/deltaphijj/shapes/histos_$2.root "#Delta#phi_{jj}" ShapesPlots/$2_EFT_shapes/EFT_deltaphijj.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/deltaetajj/shapes/histos_$2.root "#Delta#eta_{jj}" ShapesPlots/$2_EFT_shapes/EFT_deltaetajj.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/met/shapes/histos_$2.root "MET [GeV]" ShapesPlots/$2_EFT_shapes/EFT_met.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/mll/shapes/histos_$2.root "m_{ll} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_mll.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/phij1/shapes/histos_$2.root "phi_{j1}" ShapesPlots/$2_EFT_shapes/EFT_phij1.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/phij2/shapes/histos_$2.root "phi_{j2}" ShapesPlots/$2_EFT_shapes/EFT_phij2.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/ptj1/shapes/histos_$2.root "p_{T,j1} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_ptj1.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/ptj2/shapes/histos_$2.root "p_{T,j2} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_ptj2.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/ptl1/shapes/histos_$2.root "p_{T,l1} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_ptl1.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/ptl2/shapes/histos_$2.root "p_{T,l2} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_ptl2.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/ptll/shapes/histos_$2.root "p_{T,ll} [GeV]" ShapesPlots/$2_EFT_shapes/EFT_ptll.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/etaj1/shapes/histos_$2.root "#eta_{j1}" ShapesPlots/$2_EFT_shapes/EFT_etaj1.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/etaj2/shapes/histos_$2.root "#eta_{j2}" ShapesPlots/$2_EFT_shapes/EFT_etaj2.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/etal1/shapes/histos_$2.root "#eta_{l1}" ShapesPlots/$2_EFT_shapes/EFT_etal1.png $min $max $step
python plot_shapes.py $1/EFT/datacards/$2/etal2/shapes/histos_$2.root "#eta_{l2}" ShapesPlots/$2_EFT_shapes/EFT_etal2.png $min $max $step
