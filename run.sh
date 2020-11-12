python comparison.py --ops cG --npoints 20000 --rmdat --out plots/Simple_1D_1op.pdf,plots/Simple_1D_1op.pdf
python comparison.py --npoints 20000 --rmdat --out plots/All_1D_2op_sys0p2p.pdf,plots/All_2D_2op_sys0p2p.pdf
python comparison.py --npoints 20000 --ops 'cG','cGtil','cH','cHB' --out plots/All_1D_4op_sys0p2p.pdf,plots/All_2D_4op_sys0p2p.pdf
python comparison.py --npoints 20000 --ops 'cG','cGtil','cH','cHB','cHBtil','cHDD' --out plots/All_1D_6op_sys0p2p.pdf,plots/All_2D_6op_sys0p2p.pdf
python comparison.py --npoints 20000 --ops 'cG','cGtil','cH','cHB','cHBtil','cHDD','cHG','cHGtil' --out plots/All_1D_8op_sys0p2p.pdf,plots/All_2D_8op_sys0p2p.pdf

python comparison.py --npoints 20000 --sysval 1.01 --out plots/All_1D_2op_sys2p0.pdf,plots/All_2D_2op_sys1p0.pdf
python comparison.py --npoints 20000 --sysval 1.05 --out plots/All_1D_2op_sys6p0.pdf,plots/All_2D_2op_sys2p0.pdf
python comparison.py --npoints 20000 --sysval 1.1 --out plots/All_1D_2op_sys8p0.pdf,plots/All_2D_2op_sys4p0.pdf