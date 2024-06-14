clean:
	rm -fr work *.log *.wlf *.asdb compile* *.yml osvvm*
osvvm: 
	vlib osvvm
	vcom -work osvvm -2008 -f lvOsvvmFlistFname -l af_osvvm_comp.log
mti: clean osvvm
	vlib work
	vcom -2008 -f ../dut_src/dut.f -f tb.f -l af_sim_comp.log
	vsim -c tb_af_up_dn_counter -do "run -all;exit" -l af_sim_run.log
