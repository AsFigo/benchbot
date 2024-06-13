clean:
	rm -fr work *.log *.wlf *.asdb compile* *.yml
mti: clean
	vlib work
	vcom -2008 -f ../dut_src/dut.f -f tb.f -l af_sim_comp.log
	vsim -c tb_af_up_dn_counter -do "run -all;exit" -l af_sim_run.log
