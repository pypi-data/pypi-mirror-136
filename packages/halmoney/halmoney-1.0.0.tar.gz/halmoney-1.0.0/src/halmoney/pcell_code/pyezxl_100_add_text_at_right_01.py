#  -*- coding: utf-8 -*-

import pyezxl
excel = pyezxl.pyezxl("activeworkbook")
activesheet_name = excel.read_activesheet_name()
rng_select = excel.read_range_select()
print (rng_select)
#선택한 영역의 각셀의 값에 글자를 추가하는것

x1, y1, x2, y2= excel.read_range_select()
bbb=excel.read_messagebox_value("Please input text")


for y in range(int(y1), int(y2+1)):
	for x in range(int(x1), int(x2+1)):
		current_data = str(excel.read_cell_value(activesheet_name,[x, y]))
		if current_data == "None" : current_data = ""
		excel.write_cell_value(activesheet_name,[x, y],(str(current_data)+str(bbb)))