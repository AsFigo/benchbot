all: clean comp run

clean:
	rm -fr work* *.log transc* *.wlf

comp:
	vlib work
	vcom -f flist -l afComp.log

gui:
	vsim +acc tb_af_up_dn_counter -l afRun.log 

run:
	vsim -c tb_af_up_dn_counter -do "run -a; exit" -l afRun.log


