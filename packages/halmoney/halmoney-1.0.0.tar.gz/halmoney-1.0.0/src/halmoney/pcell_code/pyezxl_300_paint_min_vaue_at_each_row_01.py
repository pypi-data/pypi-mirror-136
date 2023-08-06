#  -*- coding: utf-8 -*-

import pyezxl
excel = pyezxl.pyezxl("activeworkbook")
activesheet_name = excel.read_activesheet_name()
[x1, y1, x2, y2] = excel.read_range_select()

all_data=excel.read_range_value("", [x1, y1, x2, y2])

#읽어온 값중에서 열별로 최소값구한후 색칠 하기
if not(x1==x2 and y1==y2) :
	for line_no in range(len(all_data)):
		line_data = all_data[line_no]
		filteredList = list(filter(lambda x: type(x) == type(1) or type(x) == type(1.0), line_data))
		if filteredList == []:
			pass
		else:
			max_value = min(filteredList)
			x_location = x1 + line_no
			for no in range(len(line_data)):
				y_location = y1 + no
				if (line_data[no]) == max_value:
					excel.set_cell_color(activesheet_name, [x_location, y_location], 16)
else:
	print("Please re-check selection area")








#for num_garo in range(len(datas)):
#	#리스트를 정렬하여 제일 처음의 자료와 비교를 해서, 그것과 같은 셀의값에 색깔을 넣는다
#	temp=list(datas[num_garo])
#	min_value = sorted(temp)
#	for num_sero in range(len(datas[0])):
#			if datas[num_garo][num_sero]==min_value[0]:
#				print(min_value)
#				garo = selection_range[1]+num_garo
#				sero = selection_range[0]+num_sero
#				excel.set_range_color(activesheet_name, [garo, sero], 6)

