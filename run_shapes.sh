mkdir ShapesPlots
mkdir ShapesPlots/EFTNeg_shapes
mkdir ShapesPlots/EFTNeg-alt_shapes
mkdir ShapesPlots/EFT_shapes

#path_to_shapes #xtitle #outputfile #k_min(none) #k_max(none) #step(none)

#EFTNeg
python plot_shapes.py $1/EFTNeg/datacards/$2/deltaphijj/shapes/histos_$2.root "#Delta#phi_{jj}" ShapesPlots/EFTNeg_shapes/EFTNeg_deltaphijj.png
python plot_shapes.py $1/EFTNeg/datacards/$2/deltaetajj/shapes/histos_$2.root "#Delta#eta_{jj}" ShapesPlots/EFTNeg_shapes/EFTNeg_deltaetajj.png
python plot_shapes.py $1/EFTNeg/datacards/$2/met/shapes/histos_$2.root "MET [GeV]" ShapesPlots/EFTNeg_shapes/EFTNeg_met.png
python plot_shapes.py $1/EFTNeg/datacards/$2/mll/shapes/histos_$2.root "m_{ll} [GeV]" ShapesPlots/EFTNeg_shapes/EFTNeg_mll.png
python plot_shapes.py $1/EFTNeg/datacards/$2/mjj/shapes/histos_$2.root "m_{jj} [GeV]" ShapesPlots/EFTNeg_shapes/EFTNeg_mjj.png
python plot_shapes.py $1/EFTNeg/datacards/$2/phij1/shapes/histos_$2.root "phi_{j1}" ShapesPlots/EFTNeg_shapes/EFTNeg_phij1.png
python plot_shapes.py $1/EFTNeg/datacards/$2/phij2/shapes/histos_$2.root "phi_{j2}" ShapesPlots/EFTNeg_shapes/EFTNeg_phij2.png
python plot_shapes.py $1/EFTNeg/datacards/$2/ptj1/shapes/histos_$2.root "p_{T,j1}" ShapesPlots/EFTNeg_shapes/EFTNeg_ptj1.png
python plot_shapes.py $1/EFTNeg/datacards/$2/ptj2/shapes/histos_$2.root "p_{T,j2}" ShapesPlots/EFTNeg_shapes/EFTNeg_ptj2.png
python plot_shapes.py $1/EFTNeg/datacards/$2/ptl1/shapes/histos_$2.root "p_{T,l1}" ShapesPlots/EFTNeg_shapes/EFTNeg_ptl1.png
python plot_shapes.py $1/EFTNeg/datacards/$2/ptl2/shapes/histos_$2.root "p_{T,l2}" ShapesPlots/EFTNeg_shapes/EFTNeg_ptl2.png
python plot_shapes.py $1/EFTNeg/datacards/$2/ptll/shapes/histos_$2.root "p_{T,ll}" ShapesPlots/EFTNeg_shapes/EFTNeg_ptll.png
python plot_shapes.py $1/EFTNeg/datacards/$2/etaj1/shapes/histos_$2.root "#eta_{j1}" ShapesPlots/EFTNeg_shapes/EFTNeg_etaj1.png
python plot_shapes.py $1/EFTNeg/datacards/$2/etaj2/shapes/histos_$2.root "#eta_{j2}" ShapesPlots/EFTNeg_shapes/EFTNeg_etaj2.png
python plot_shapes.py $1/EFTNeg/datacards/$2/etal1/shapes/histos_$2.root "#eta_{l1}" ShapesPlots/EFTNeg_shapes/EFTNeg_etal1.png
python plot_shapes.py $1/EFTNeg/datacards/$2/etal2/shapes/histos_$2.root "#eta_{l2}" ShapesPlots/EFTNeg_shapes/EFTNeg_etal2.png

#EFTNeg-alt
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/deltaphijj/shapes/histos_$2.root "#Delta#phi_{jj}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_deltaphijj.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/deltaetajj/shapes/histos_$2.root "#Delta#eta_{jj}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg_deltaetajj.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/met/shapes/histos_$2.root "MET [GeV]" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_met.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/mll/shapes/histos_$2.root "m_{ll} [GeV]" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_mll.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/mjj/shapes/histos_$2.root "m_{jj} [GeV]" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_mjj.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/phij1/shapes/histos_$2.root "phi_{j1}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_phij1.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/phij2/shapes/histos_$2.root "phi_{j2}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_phij2.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/ptj1/shapes/histos_$2.root "p_{T,j1}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_ptj1.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/ptj2/shapes/histos_$2.root "p_{T,j2}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_ptj2.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/ptl1/shapes/histos_$2.root "p_{T,l1}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_ptl1.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/ptl2/shapes/histos_$2.root "p_{T,l2}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_ptl2.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/ptll/shapes/histos_$2.root "p_{T,ll}" ShapesPlots/EFTNeg-alt_shapes/EFTNeg-alt_ptll.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/etaj1/shapes/histos_$2.root "#eta_{j1}" ShapesPlots/EFTNeg_shapes/EFTNeg-alt_etaj1.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/etaj2/shapes/histos_$2.root "#eta_{j2}" ShapesPlots/EFTNeg_shapes/EFTNeg-alt_etaj2.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/etal1/shapes/histos_$2.root "#eta_{l1}" ShapesPlots/EFTNeg_shapes/EFTNeg-alt_etal1.png
python plot_shapes.py $1/EFTNeg-alt/datacards/$2/etal2/shapes/histos_$2.root "#eta_{l2}" ShapesPlots/EFTNeg_shapes/EFTNeg-alt_etal2.png

#EFT
python plot_shapes.py $1/EFT/datacards/$2/deltaphijj/shapes/histos_$2.root "#Delta#phi_{jj}" ShapesPlots/EFT_shapes/EFT_deltaphijj.png
python plot_shapes.py $1/EFT/datacards/$2/deltaetajj/shapes/histos_$2.root "#Delta#eta_{jj}" ShapesPlots/EFT_shapes/EFT_deltaetajj.png
python plot_shapes.py $1/EFT/datacards/$2/met/shapes/histos_$2.root "MET [GeV]" ShapesPlots/EFT_shapes/EFT_met.png
python plot_shapes.py $1/EFT/datacards/$2/mll/shapes/histos_$2.root "m_{ll} [GeV]" ShapesPlots/EFT_shapes/EFT_mll.png
python plot_shapes.py $1/EFT/datacards/$2/mjj/shapes/histos_$2.root "m_{jj} [GeV]" ShapesPlots/EFT_shapes/EFT_mjj.png
python plot_shapes.py $1/EFT/datacards/$2/phij1/shapes/histos_$2.root "phi_{j1}" ShapesPlots/EFT_shapes/EFT_phij1.png
python plot_shapes.py $1/EFT/datacards/$2/phij2/shapes/histos_$2.root "phi_{j2}" ShapesPlots/EFT_shapes/EFT_phij2.png
python plot_shapes.py $1/EFT/datacards/$2/ptj1/shapes/histos_$2.root "p_{T,j1}" ShapesPlots/EFT_shapes/EFT_ptj1.png
python plot_shapes.py $1/EFT/datacards/$2/ptj2/shapes/histos_$2.root "p_{T,j2}" ShapesPlots/EFT_shapes/EFT_ptj2.png
python plot_shapes.py $1/EFT/datacards/$2/ptl1/shapes/histos_$2.root "p_{T,l1}" ShapesPlots/EFT_shapes/EFT_ptl1.png
python plot_shapes.py $1/EFT/datacards/$2/ptl2/shapes/histos_$2.root "p_{T,l2}" ShapesPlots/EFT_shapes/EFT_ptl2.png
python plot_shapes.py $1/EFT/datacards/$2/ptll/shapes/histos_$2.root "p_{T,ll}" ShapesPlots/EFT_shapes/EFT_ptll.png
python plot_shapes.py $1/EFT/datacards/$2/etaj1/shapes/histos_$2.root "#eta_{j1}" ShapesPlots/EFT_shapes/EFT_etaj1.png
python plot_shapes.py $1/EFT/datacards/$2/etaj2/shapes/histos_$2.root "#eta_{j2}" ShapesPlots/EFT_shapes/EFT_etaj2.png
python plot_shapes.py $1/EFT/datacards/$2/etal1/shapes/histos_$2.root "#eta_{l1}" ShapesPlots/EFT_shapes/EFT_etal1.png
python plot_shapes.py $1/EFT/datacards/$2/etal2/shapes/histos_$2.root "#eta_{l2}" ShapesPlots/EFT_shapes/EFT_etal2.png
