#  -*- coding: utf-8 -*-

import pyezxl
excel = pyezxl.pyezxl("activeworkbook")
activesheet_name = excel.read_activesheet_name()
[x1, y1, x2, y2] = excel.read_range_select()

#선택한 영역에서 고유한값을 만들어서
#열 하나를 선택한후 나열하도록 한다

py_dic={}
for x in range(x1, x2+1):
	for y in range(y1, y2+1):
		current_data = excel.read_cell_value(activesheet_name,[x, y])

		#사전안에 현재 자료가 있는지 확인하는것
		if not(current_data in py_dic) and not(current_data==""): py_dic[current_data]=""

excel.insert_line_y("", 1)
list_dic = list(py_dic.keys())
for no in range(len(list_dic)):
	excel.write_cell_value(activesheet_name, [no+1, 1], list_dic[no])
