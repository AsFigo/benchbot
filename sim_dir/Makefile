clean:
	rm -fr work* *.log

comp:
	vlib work
	vcom -f flist -l afComp.log

run:
	vsim -c tb_af_up_dn_counter -c -do "run -a; exit" -l afRun.log

all: clean comp run

