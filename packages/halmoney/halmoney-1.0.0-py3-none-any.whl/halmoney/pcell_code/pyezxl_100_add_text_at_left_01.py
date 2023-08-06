#  -*- coding: utf-8 -*-

#선택한 영역의 각셀의 값에 글자를 추가하는것

import pyezxl
excel = pyezxl.pyezxl("activeworkbook")
activesheet_name = excel.read_activesheet_name()
[x1, y1, x2, y2] = excel.read_range_select()

bbb=excel.read_messagebox_value("Please input text")

for x in range(x1, x2+1):
	for y in range(y1, y2+1):
		current_data = str(excel.read_cell_value(activesheet_name,[x, y]))
		if current_data == "None" : current_data = ""


		excel.write_cell_value(activesheet_name,[x, y],(str(bbb) + str(current_data)))