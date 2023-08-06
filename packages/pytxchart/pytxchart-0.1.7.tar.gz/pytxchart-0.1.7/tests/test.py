import pytxchart as m

crt = m.PyTxChart()
crt.read(r"A3934.CRT")
crt_data = crt.get_data()
if (crt_data['desc']['Chart_name'] != '3934'):
	print("gavno")
else:
	print("ouu eee")
assert crt_data['desc']['File_name'] == 'A3934'
assert crt_data['desc']['Date_corr'] == '07-02-2002'