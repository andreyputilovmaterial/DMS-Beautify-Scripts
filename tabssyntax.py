import os, time, re
from datetime import datetime

def beautify(t):
    return t


if __name__ == "__main__":
	start_time = datetime.utcnow()
	print("Starting...\n")
	
	inp_file_name = None
	if len(sys.argv)>1:
		inp_file_name = sys.argv[0]
	else:
	    inp_file_name = 'T_Tables.mrs'
	
	inp_file = open(input_json_lmdd)
	
	print("Reading file...\n")
	t = inp_file.read()
	
	inp_file = None
	
	print("Replacements...\n")
	t_converted = beautify(t)
	
	print("Writing results...\n")
	with open(out_file_name,'w') as out_file:
		out_file.write(output)
	end_time = datetime.utcnow()
	#elapsed_time = end_time - start_time
	print("Finished") # + str(elapsed_time)
	