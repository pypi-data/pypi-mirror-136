# -*- coding: utf-8 -*-

import win32com.client
import re
import string
import win32gui
import math
import halmoney_ccolor

# 2021-08-21 : x,y의 기준을 변경하여 적용하기로 한후에 최종적으로 끝냄
# 전반적으로 이름을 다시 정의 함
# set, draw, delete, write, read, add가 기본이다

class pcell:
	my_web_site = "www.halmoney.com"

	def __init__(self, filename=""):
		self.vars = {} #공통으로 사용할 변수들을 설정하는 것이다
		self.vars["active_sheet"] = ""
		self.vars["active_cell"] = [0,0]
		self.vars["select_range"] = [0,0,0,0]
		self.vars["used_range"] = [0,0,0,0]


		# 만약 화일의 경로가 있으면 그 화일을 열도록 한다
		self.xlApp = win32com.client.dynamic.Dispatch('Excel.Application')
		self.xlApp.Visible = 1

		if filename != None or filename != "":
			self.filename = filename.lower()

		if self.filename == 'activeworkbook' or self.filename == '':
			# activeworkbook으로 된경우는 현재 활성화된 workbook을 그대로 사용한다
			self.xlBook = self.xlApp.ActiveWorkbook
			if self.xlBook == None:
				# 만약 activework북을 부르면서도 화일이 존재하지 않으면 새로운 workbook을 만드는것이다
				try:
					self.xlApp.WindowState = -4137
					self.xlBook = self.xlApp.WorkBooks.Add()
				except:
					win32gui.MessageBox(0, "There is no Activeworkbook", self.my_web_site, 0)

		elif not (self.filename == 'activeworkbook') and self.filename:
			# 만약 화일이름이 따로 주어지면 그화일을 연다
			try:
				self.xlApp.WindowState = -4137
				self.xlBook = self.xlApp.Workbooks.Open(self.filename)
			except:
				win32gui.MessageBox(0, "Please check file path", self.my_web_site, 0)
		else:
			# 빈것으로 된경우는 새로운 workbook을 하나 열도록 한다
			self.xlApp.WindowState = -4137
			self.xlBook = self.xlApp.WorkBooks.Add()

	def add_button(self, sheet_name, xyxy, macro, title):
		# 버튼을 만들어서 그 버튼에 매크로를 연결하는 것이다
		# 매크로와 같은것을 특정한 버튼에 연결하여 만드는것을 보여주기위한 것이다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		new_btn = sheet.Buttons()
		new_btn.Add(x1, x2, y1, y2)
		new_btn.OnAction = "Macro2"
		new_btn.Text = title

	def add_picture(self):
		sh = self.xlBook.Worksheets("Sheet1")
		sh.Shapes.AddPicture("c:\icon_sujun.gif", 0, 1, 541.5, 92.25, 192.75, 180)

	def add_sheet(self):
		# 시트하나 추가하기
		self.xlBook.Worksheets.Add()

	def insert_sheet_new(self, new_name=""):
		# 시트하나 추가하기
		if new_name == "":
			self.xlBook.Worksheets.Add()
		else:
			self.xlBook.Worksheets.Add()
			old_name = self.xlApp.ActiveSheet.Name
			self.xlBook.Worksheets(old_name).Name = new_name

	def change_char_num(self, eng):
		no = 0
		result = 0
		for one in eng.lower()[::-1]:
			num = string.ascii_lowercase.index(one) + 1
			#print(num)
			result = result + 26 ** no * num
			no = no + 1
		return result


	def change_num_char(self, input_data):
		# input_data : 27 => result : aa
		# 숫자를 문자로 바꿔주는 것
		base_number = int(input_data)
		result_01 = ''
		result = []
		while base_number > 0:
			div = base_number // 26
			mod = base_number % 26
			if mod == 0:
				mod = 26
				div = div - 1
			base_number = div
			result.append(mod)
		for one_data in result:
			result_01 = string.ascii_lowercase[one_data - 1] + result_01
		return result_01


	def change_sheet_name(self, old_name, new_name):
		# 시트이름을 바꿉니다
		self.xlBook.Worksheets(old_name).Name = new_name


	def check_address_value(self, input_data):
		#입력된 주소값을 [x1, y1, x2, y2]의 형태로 만들어 주는 것이다
		input_type = self.check_data_type(input_data)

		if input_type != "list":
			aaa = re.compile("[a-zA-Z]*|\d*")
			temp_result = aaa.findall(str(input_data))
		else:
			temp_result = input_data

		result = []
		for two in temp_result:
			if two != "":
				result.append(str(two).lower())
		#print("정리된 결과 값 ===> ", result)

		input_cell_type = self.check_cell_type(result)

		if len(result) == 2 and input_type == "cell" and input_cell_type == "a1":
			changed_result = [result[1], self.change_char_num(result[0]), result[1], self.change_char_num(result[0])]

		elif len(result) == 2 and input_type == "range" and input_cell_type == "aa":
			changed_result = [self.change_char_num(result[0]), self.change_char_num(result[1]), self.change_char_num(result[0]),
							  self.change_char_num(result[1])]

		elif len(result) == 2 and input_type == "range" and input_cell_type == "11":
			changed_result = [result[0], "0", result[0], "0"]

		elif len(result) == 4 and input_type == "cell" and input_cell_type == "a1":
			changed_result = [self.change_char_num(result[0]), result[1], self.change_char_num(result[2]), result[3]]

		elif len(result) == 4 and input_type == "range" and input_cell_type == "a1":
			changed_result = [result[1], self.change_char_num(result[0]), result[3], self.change_char_num(result[2])]

		elif len(result) == 2 and input_type == "list":
			changed_result = [result[0], result[1], result[0], result[1]]

		elif len(result) == 4 and input_type == "list":
			changed_result = result

		else:
			changed_result = "error"
			#print(input_type)

		final_result = [int(changed_result[0]), int(changed_result[1]), int(changed_result[2]), int(changed_result[3])]
		return final_result


	def check_cell_type(self, input_data):
		# 하나의 영역으로 들어온 것이 어떤 형태인지를 알아 내는 것이다
		result = ""
		if input_data[0][0] in string.ascii_lowercase and input_data[1][0] in string.digits:
			result = "a1"
		if input_data[0][0] in string.ascii_lowercase and input_data[1][0] in string.ascii_lowercase:
			result = "aa"
		if input_data[0][0] in string.digits and input_data[1][0] in string.digits:
			result = "11"
		return result


	def check_data_type(self, input_data):
		# 영역으로 입력된 자료의 형태를 확인하는 것이다
		if type(input_data) == type([]):
			input_type = "list"
			result = input_data
		elif len(str(input_data).split(":")) > 1:
			input_type = "range"
		elif type(input_data) == type("aaa"):
			input_type = "cell"
		else:
			input_type = "error"
		# print(input_type)
		return input_type


	def check_sheet_name(self, sheet_name=""):
		# sheet이름을 확인해서 돌려준다.
		# 아무것도 없으면 현재 활성화된 activesheet를 돌려준다
		# 시트이름으로 확인하여 없다면, 일단 입력받은 시트이름으로 새로운 시트를 만든다
		# read와 check의 의미 차이는 check는 어떤 조건에서 2개이상의 다른 값을 보여줄때이며
		# read는 조건문등의 구문이 없이 단순히 값을 읽어올때 사용한다
		if str(sheet_name).lower() == "activesheet" or sheet_name == "":
			sheet = self.xlApp.ActiveSheet
		elif sheet_name in self.read_sheet_names():
			sheet = self.xlBook.Worksheets(sheet_name)
		else:
			self.add_sheet()
			old_sheet_name = self.read_activesheet_name()
			self.change_sheet_name(old_sheet_name, sheet_name)
			sheet = self.xlBook.Worksheets(sheet_name)
		return sheet


	def check_x_empty(self, sheet_name, x):
		# 열전체가 빈 것인지 확인해서 돌려준다
		# 전체가 비었을때는 0을 돌려준다
		sheet = self.check_sheet_name(sheet_name)
		result = self.xlApp.WorksheetFunction.CountA(sheet.Rows(x).EntireRow)
		return result

	def check_xy_address(self, xy):
		# 입력의 형태 : 3, [3], [2,3], D, [A,D], [D]
		# 출력 : [3,3], [2,3], [4,4,], [1,4]
		# x나 y의 하나를 확인할때 입력을 잘못하는 경우를 방지하기위해 사용
		x1, y1 = xy
		result = []
		if type([]) == type(xy):
			if len(xy) == 1:
				x1 = self.change_char_num(str(x1))
				result = [x1, x1]
			if len(xy) == 2:
				x1 = self.change_char_num(str(x1))
				y1 = self.change_char_num(str(y1))
				result = xy
		else:
			xy = str(xy)
			if re.match('[a-zA-Z0-9]', xy):
				if re.match('[a-zA-Z]', xy):
					xy = self.change_char_num(xy)
					result = [xy, xy]
				else:
					result = [xy, xy]
		return result

	def check_y_empty(self, sheet_name, y):
		# 세로열 전체가 빈 것인지 확인해서 돌려준다. 전체가 비었을때는 0을 돌려준다
		y_check = self.check_xy_address(y)
		y1 = self.change_char_num(str(y_check[0]))
		sheet = self.check_sheet_name(sheet_name)
		result = self.xlApp.WorksheetFunction.CountA(sheet.Columns(y1).EntireColumn)
		return result

	def close(self):
		# 현재는 close를 시키면 엑셀워크북만이 아니라 엑셀자체도 종료 시킵니다
		self.xlBook.Close(SaveChanges=0)
		del self.xlApp

	def copy_range(self, sheet_name, xyxy):
		# 복사하기 기능입니다
		x1, y1, x2, y2 = self.check_address_value(xyxy[0])
		sheet1 = self.xlBook.Worksheets(sheet_name[0])
		range1 = sheet1.Range(sheet1.Cells(x1, y1), sheet1.Cells(x2, y2))

		x3, y3, x4, y4 = self.check_address_value(xyxy[1])
		sheet2 = self.xlBook.Worksheets(sheet_name[1])
		range2 = sheet2.Range(sheet2.Cells(x3, y3), sheet2.Cells(x4, y4))

		self.xlBook.Worksheets(sheet1).Range(range1).Select()
		self.xlBook.Worksheets(sheet2).Range(range2).Paste()
		self.xlApp.CutCopyMode = 0


	def copy_x(self, sheet_name1, sheet_name2, xx0, xx1):
		# 세로의 값을 이동시킵니다
		sheet1 = self.check_sheet_name(sheet_name1)
		sheet2 = self.check_sheet_name(sheet_name2)

		xx0_1, xx0_2 = self.check_xy_address(xx0)
		xx1_1, xx1_2 = self.check_xy_address(xx1)

		xx0_1 = self.change_char_num(xx0_1)
		xx0_2 = self.change_char_num(xx0_2)
		xx1_1 = self.change_char_num(xx1_1)
		xx1_2 = self.change_char_num(xx1_2)

		sheet1.Select()
		sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Select()
		sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Copy()
		sheet2.Select()
		sheet2.Rows(str(xx1_1) + ':' + str(xx1_2)).Select()
		sheet2.Paste()


	def copy_y(self, sheet_name1, sheet_name2, yy0, yy1):
		# 세로의 값을 이동시킵니다
		sheet1 = self.check_sheet_name(sheet_name1)
		sheet2 = self.check_sheet_name(sheet_name2)

		yy0_1, yy0_2 = self.check_xy_address(yy0)
		yy1_1, yy1_2 = self.check_xy_address(yy1)

		yy0_1 = self.change_num_char(yy0_1)
		yy0_2 = self.change_num_char(yy0_2)
		yy1_1 = self.change_num_char(yy1_1)
		yy1_2 = self.change_num_char(yy1_2)
		# print(yy0_1, yy0_2, yy1_1, yy1_2)

		sheet1.Select()
		sheet1.Columns(str(yy0_1) + ':' + str(yy0_2)).Select()
		sheet1.Columns(str(yy0_1) + ':' + str(yy0_2)).Copy()
		sheet2.Select()
		sheet2.Columns(str(yy1_1) + ':' + str(yy1_2)).Select()
		sheet2.Paste()


	def count_sheet_shape(self, sheet_name=""):
		sheet = self.check_sheet_name(sheet_name)
		return sheet.Shapes.Count


	def cut_x(self, sheet_name1, sheet_name2, xx0, xx1):
		# 세로의 값을 이동시킵니다
		sheet1 = self.check_sheet_name(sheet_name1)
		sheet2 = self.check_sheet_name(sheet_name2)

		xx0_1, xx0_2 = self.check_xy_address(xx0)
		xx1_1, xx1_2 = self.check_xy_address(xx1)

		xx0_1 = self.change_char_num(xx0_1)
		xx0_2 = self.change_char_num(xx0_2)
		xx1_1 = self.change_char_num(xx1_1)
		xx1_2 = self.change_char_num(xx1_2)

		sheet1.Select()
		sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Select()
		sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Copy()
		sheet2.Select()
		sheet2.Rows(str(xx1_1) + ':' + str(xx1_2)).Select()
		sheet2.Rows(str(xx1_1) + ':' + str(xx1_2)).Insert()

		if sheet1 == sheet2:
			if xx0_1 <= xx1_1:
				sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Delete()
			else:
				new_xx0_1 = self.change_num_char(xx0_1 + xx1_2 - xx1_1)
				new_xx0_2 = self.change_num_char(xx0_2 + xx1_2 - xx1_1)
				sheet1.Rows(str(new_xx0_1) + ':' + str(new_xx0_2)).Delete()
		else:
			sheet1.Rows(str(xx0_1) + ':' + str(xx0_2)).Delete()


	def cut_y(self, sheet_name_1, sheet_name_2, y0, y1):
		# 가로의 값을 이동시킵니다
		sheet1 = self.check_sheet_name(sheet_name_1)
		sheet2 = self.check_sheet_name(sheet_name_2)

		y0_1, y0_2 = self.check_xy_address(y0)
		y1_1, y1_2 = self.check_xy_address(y1)

		y0_1 = self.change_num_char(y0_1)
		y0_2 = self.change_num_char(y0_2)
		y1_1 = self.change_num_char(y1_1)
		y1_2 = self.change_num_char(y1_2)

		sheet1.Select()
		sheet1.Rows(str(y0_1) + ':' + str(y0_2)).Select()
		sheet1.Rows(str(y0_1) + ':' + str(y0_2)).Cut()
		sheet2.Select()
		sheet2.Rows(str(y1_1) + ':' + str(y1_2)).Select()
		sheet2.Rows(str(y1_1) + ':' + str(y1_2)).Insert()


	def delete_memo(self, sheet_name, xyxy):
		# 메모를 삭제한는 것
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		sheet.Cells(x1, y1).ClearComments()

	def delete_only_one(self, xyxy):
		# 선택한 자료중에서 고유한 자료만을 골라내는 것이다
		# 1. 관련 자료를 읽어온다
		# 2. 자료중에서 고유한것을 찾아낸다
		# 3. 선택영역에 다시 쓴다

		temp_datas = self.read_range_value("", xyxy)

		temp_result = []
		for one_list_data in temp_datas:
			for one_data in one_list_data:
				if one_data in temp_result or type(one_data) == type(None):
					pass
				else:
					temp_result.append(one_data)
					print (type(one_data))

		self.delete_range_value("", xyxy)

		for num in range(len(temp_result)):
			mox, namuji = divmod(num, xyxy[2] - xyxy[0] + 1)
			print (temp_result[num])
			self.write_cell_value("", [xyxy[0] + namuji, xyxy[1] + mox], temp_result[num])


	def delete_range_color(self, sheet_name, xyxy):
		# 영역의 모든 색을 지운다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.Interior.Pattern = -4142
		my_range.Interior.TintAndShade = 0
		my_range.Interior.PatternTintAndShade = 0


	def delete_range_linecolor(self, sheet_name, xyxy):
		# 영역에 선의색을 다 없애는것
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.Interior.Pattern = 0
		my_range.Interior.PatternTintAndShade = 0


	def delete_range_line(self, sheet_name, xyxy):
		# 모든선을 지운다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		for each in [5, 6, 7, 8, 9, 10, 11, 12]:
			my_range.Borders(each).LineStyle = -4142

	def delete_range_link(self, sheet_name, xyxy):
		# 영역의 모든 링크를 지운다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.Hyperlinks.Delete()

	def delete_cell_value(self, sheet_name, xy):
		# range의 입력방법은 [row1, col1, row2, col2]이다
		# 선택한영역에서 값을 clear기능을 한다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1, y1))
		my_range.ClearContents()

	def delete_range_value(self, sheet_name, xyxy):
		# range의 입력방법은 [row1, col1, row2, col2]이다
		# 선택한영역에서 값을 clear기능을 한다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.ClearContents()

	def delete_rangename(self, sheet_name, range_name):
		# 입력한 이름을 삭제한다
		# name은 workbook으로 되지만 동일하게 하기위하여 sheet_name을 넣은 것이다
		sheet = self.check_sheet_name(sheet_name)
		result = self.xlBook.Names(range_name).Delete()
		return result


	def delete_rangename_all(self, sheet_name):
		# 셀의 줄바꿈을 설정할때 사용한다
		# 만약 status를 false로 하면 줄바꿈이 실행되지 않는다.
		sheet = self.check_sheet_name(sheet_name)
		aaa = self.xlApp.Names
		for one in aaa:
			ddd = str(one.Name)
			if ddd.find("!") < 0:
				print(one.Name)

	def delete_shape(self, sheet_name="", name=""):
		sheet = self.check_sheet_name(sheet_name)
		sheet.Shapes(name).Delete()


	def delete_shape_all(self, sheet_name=""):
		# 특정 시트안의 그림을 다 지우는 것이다
		sheet = self.check_sheet_name(sheet_name)
		drawings_no = sheet.Shapes.Count
		if drawings_no > 0:
			for aa in range(drawings_no, 0, -1):
				# Range를 앞에서부터하니 삭제하자마자 번호가 다시 매겨져서, 뒤에서부터 삭제하니 잘된다
				sheet.Shapes(aa).Delete()
		return drawings_no

	def delete_sheet(self, sheet_name):
		# 시트하나 삭제하기
		sheet = self.check_sheet_name(sheet_name)
		self.xlApp.DisplayAlerts = False
		sheet.Delete()
		self.xlApp.DisplayAlerts = True

	def delete_sheet_allvalue(self, sheet_name):
		# 시트의 모든 값을 삭제한다
		# 2005-02-18
		sheet = self.xlBook.Worksheets(sheet_name)
		sheet.Cells.ClearContents()


	def delete_usedrange_value(self, sheet_name=""):
		# 자주사용하는 것 같아서 usedrange의 값을 지우는것을 만들어 보았다
		# 2005-02-18
		sheet = self.check_sheet_name(sheet_name)
		temp_range = self.read_usedrange_address(sheet_name)
		sheet.Range(temp_range[2]).ClearContents()


	def delete_xx(self, sheet_name, xx):
		# 가로 한줄삭제하기
		# 입력형태는 2, [2,3]의 두가지가 가능하다
		sheet = self.check_sheet_name(sheet_name)
		sheet.Columns(str(xx[0]) + ':' + str(xx[1])).Delete()


	def delete_xx_value(self, sheet_name, xx):
		# 한줄값만 삭제하기
		sheet = self.check_sheet_name(sheet_name)
		sheet.Columns(str(xx[0]) + ':' + str(xx[1])).ClearContents()


	def delete_yy(self, sheet_name, yy):
		# 세로줄 삭제하기
		sheet = self.check_sheet_name(sheet_name)
		sheet.Rows(str(yy[0]) + ':' + str(yy[1])).Delete(-4121)


	def delete_yy_value(self, sheet_name, yy):
		# 한줄값만 삭제하기
		sheet = self.check_sheet_name(sheet_name)
		sheet.Columns(str(yy[0]) + ':' + str(yy[1])).ClearContents()

	def draw_range_color(self, sheet_name, xyxy, color_value):
		# 영역에 색깔을 입힌다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		result_rgb = self.check_color(color_value)
		my_range.Interior.color = self.rgb_to_hex(result_rgb)

	def set_range_color(self, sheet_name, xyxy, color_value):
		self.draw_range_color(sheet_name, xyxy, color_value)



	def draw_range_line(self, sheet_name, xyxy, input_list):
		# [선의위치, 라인스타일, 굵기, 색깔]
		# 입력예 : [7,1,2,1], ["left","-","t0","bla"]
		# 선의위치 (5-대각선 오른쪽, 6-왼쪽대각선, 7:왼쪽, 8;위쪽, 9:아래쪽, 10:오른쪽, 11:안쪽세로, 12:안쪽가로)
		# 라인스타일 (1-실선, 2-점선, 3-가는점선, 6-굵은실선,
		# 굵기 (0-이중, 1-얇게, 2-굵게)
		# 색깔 (0-검정, 1-검정, 3-빨강),

		line_vars = {"/":6, "\\":5, "left":7, "top":8, "bottom":9, "right":10, "in|":11, "in-":12,
					 "-": 1, "..": 2, ".-": 7, "--.": 8,
					 "yel": 65535, "빨강": 3, "bla": 255, "red": 255, "aaa": 5466499,
					 "t0": 1, "t1": 2,"thin": 1, "thick": 2,
					 }

		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		for value in input_list:
				my_range.Borders(line_vars[value[0]]).Weight = line_vars[value[2]]
				my_range.Borders(line_vars[value[0]]).LineStyle = line_vars[value[1]]
				my_range.Borders(line_vars[value[0]]).Color = line_vars[value[3]]

	def draw_range_rgbcolor(self, sheet_name, xyxy, input_data):
		# 영역에 색깔을 입힌다
		# 엑셀에서의 색깔의 번호는 아래의 공식처럼 만들어 진다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		rgb_to_int = (int(input_data[2])) * (256 ** 2) + (int(input_data[1])) * 256 + int(input_data[0])
		my_range.Interior.Color = rgb_to_int


	def draw_range_wellusedline(self, sheet_name, xyxy):
		# 자주 사용하는 테두리선을 지정해 놓고 사용을 하는것
		# 이 코드는 선택된 영역의 테두리선을 긋는 것과 맨앞부분에 글자가 있는 부분을 색깔을 칠하는것
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range_1 = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1, y2))

		# 모든것을 다 지우는 것
		self.delete_shapes("")
		self.delete_range_color("", xyxy)

		# [선의위치, 라인스타일, 굵기, 색깔]
		# 선의위치 (5-대각선 오른쪽, 6-왼쪽대각선, 7:왼쪽, 8;위쪽, 9:아래쪽, 10:오른쪽, 11:안쪽세로, 12:안쪽가로)
		# 라인스타일 (1-실선, 2-점선, 3-가는점선, 6-굵은실선,
		# 굵기 (0-이중, 1-얇게, 2-굵게)
		# 색깔 (0-검정, 1-검정, 3-빨강),

		my_outline = [[7, 1, 2, 0],[8, 1, 2, 0],[9, 1, 2, 0],[10, 1, 2, 0], [11, 1, 1, 0],[12, 3, 2, 0]]  #진한 외곽선으로, 안쪽의 세로는 가는실선, 가로는 얇은 점선으로
		my_fist_line = [[9, 1, 2, 0]] #첫번째 라인의 아래는 굵은 실선으로

		for value in my_outline:
				my_range.Borders(value[0]).Weight = value[2]
				my_range.Borders(value[0]).LineStyle = value[1]
				my_range.Borders(value[0]).Color = value[3]

		for value in my_fist_line:
				my_range_1.Borders(value[0]).Weight = value[2]
				my_range_1.Borders(value[0]).LineStyle = value[1]
				my_range_1.Borders(value[0]).Color = value[3]

	def insert_xx(self, sheet_name, x):
		# 가로열을 한줄삽입하기
		sheet = self.check_sheet_name(sheet_name)
		x1 = self.check_xy_address(x)
		x_no = self.change_char_num(str(x1[0]))
		sheet.Range(str(x_no) + ':' + str(x_no)).Insert()

	def insert_yy(self, sheet_name, y):
		# 세로행을 한줄삽입하기
		sheet = self.check_sheet_name(sheet_name)
		num_r1 = self.change_num_char(y)
		sheet.Columns(str(num_r1) + ':' + str(num_r1)).Insert()

	def intersect_range1_range2(self, rng1, rng2):
		# 두개의 영역에서 교차하는 구간을 돌려준다
		# 만약 교차하는게 없으면 ""을 돌려준다
		range_1 = self.check_address_value(rng1)
		range_2 = self.check_address_value(rng2)

		x11, y11, x12, y12 = range_1
		x21, y21, x22, y22 = range_2

		if x11 == 0:
			x11 = 1
			x12 = 1048576
		if x21 == 0:
			x21 = 1
			x22 = 1048576
		if y11 == 0:
			y11 = 1
			y12 = 16384
		if y21 == 0:
			y21 = 1
			y22 = 16384

		new_range_x = [x11, x21, x12, x22]
		new_range_y = [y11, y21, y12, y22]

		new_range_x.sort()
		new_range_y.sort()

		if x11 <= new_range_x[1] and x12 >= new_range_x[2] and y11 <= new_range_y[1] and y12 >= new_range_y[1]:
			result = [new_range_x[1], new_range_y[1], new_range_x[2], new_range_y[2]]
		else:
			result = "교차점없음"
		return result

	def make_list_unique(self, input_data):
		# 1차원의 리스트가 중복값을 제외하고 돌려주는것, 집합형으로 돌려준다
		temp_dic = set()
		for one in input_data:
			temp_dic.add(one)
		return temp_dic

	def make_y_value(self, input_data):
		# 1차원의 리스트가 오면 2차원으로 만들어주는 것
		result = self.change_1d_2d(input_data)
		return result

	def change_1d_2d(self, input_data):
		# 1차원의 리스트가 오면 2차원으로 만들어주는 것
		result = []
		if len(input_data) > 0:
			if type(input_data[0]) != type([]):
				for one in input_data:
					result.append([one, ])
		return result


	def move_degree_distance(self, degree, distance):
		# 현재 위치 x,y에서 30도로 20만큼 떨어진 거리의 위치를 돌려주는 것
		degree = degree * 3.141592 / 180
		x = distance * math.cos(degree)
		y = distance * math.sin(degree)
		return [x, y]


	def move_range_bottom(self, sheet_name, xyxy):
		# 선택한 위치에서 끝부분으로 이동하는것
		# xlDown  : - 4121,  xlToLeft : - 4159, xlToRight  : - 4161, xlUp : - 4162
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.End(- 4121).Select()
		return "ok"

	def move_range_leftend(self, sheet_name, xyxy):
		# 선택한 위치에서 끝부분으로 이동하는것
		# xlDown  : - 4121,  xlToLeft : - 4159, xlToRight  : - 4161, xlUp : - 4162
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		sheet.Cells(x1, y1).End(- 4159).Select()
		return "ok"


	def move_range_rightend(self, sheet_name, xyxy):
		# 선택한 위치에서 끝부분으로 이동하는것
		# xlDown  : - 4121,  xlToLeft : - 4159, xlToRight  : - 4161, xlUp : - 4162
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.End(- 4161).Select()
		return "ok"


	def move_range_top(self, sheet_name, xyxy):
		# 선택한 위치에서 끝부분으로 이동하는것
		# xlDown  : - 4121,  xlToLeft : - 4159, xlToRight  : - 4161, xlUp : - 4162
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.End(- 4162).Select()
		return "ok"


	def move_yy(self, sheet_name1, sheet_name2, yy0, yy1):
		# 세로의 값을 이동시킵니다
		sheet1 = self.check_sheet_name(sheet_name1)
		sheet2 = self.check_sheet_name(sheet_name2)

		yy0_1, yy0_2 = self.check_xy_address(yy0)
		yy1_1, yy1_2 = self.check_xy_address(yy1)

		yy0_1 = self.change_num_char(yy0_1)
		yy0_2 = self.change_num_char(yy0_2)
		yy1_1 = self.change_num_char(yy1_1)
		yy1_2 = self.change_num_char(yy1_2)

		sheet1.Select()
		sheet1.Columns(str(yy0_1) + ':' + str(yy0_2)).Select()
		sheet1.Columns(str(yy0_1) + ':' + str(yy0_2)).Cut()
		sheet2.Select()
		sheet2.Columns(str(yy1_1) + ':' + str(yy1_2)).Select()
		sheet2.Columns(str(yy1_1) + ':' + str(yy1_2)).Insert()

	def preview(self, sheet_name):
		# 미리보기기능입니다
		sheet = self.check_sheet_name(sheet_name)
		sheet.PrintPreview()

	def read_activecell_address(self):
		# 돌려주는 값 [x, y]
		xy = self.check_address_value(self.xlApp.ActiveCell.Address)
		return xy

	def read_activecell_value(self):
		return self.xlApp.ActiveCell.Value

	def read_activesheet_name(self):
		# 현재의 엑셀중에서 활성화된 시트의 이름을 돌려준다
		return self.xlApp.ActiveSheet.Name

	def read_cell_address(self):
		#이런 이름의 함수도 있으면 좋지 않을까 해서 만듦
		result = self.read_activecell_address()
		return result

	def read_cell_color(self, sheet_name, xyxy):
		# 셀 하나에 색을 입힌다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		result = my_range.Interior.Color
		return result

	def read_cell_memo(self, sheet_name, xyxy):
		# 메모를 읽어오는 것
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		result = my_range.Comment.Text()
		return result

	def read_cell_value(self, sheet_name, xyxy):
		# 값을 일정한 영역에서 갖고온다
		# 만약 영역을 두개만 주면 처음과 끝의 영역을 받은것으로 간주해서 알아서 처리하도록 변경하였다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		result = my_range.value
		return result


	def read_continousrange_value(self, sheet, xyxy):
		# 현재선택된 셀을 기준으로 연속된 영역을 가지고 오는 것입니다
		row = xyxy
		col = xyxy

		sheet = self.xlBook.Worksheets(sheet)
		bottom = row  # 아래의 행을 찾는다
		while sheet.Cells(bottom + 1, col).Value not in [None, '']:
			bottom = bottom + 1
		right = col  # 오른쪽 열
		while sheet.Cells(row, right + 1).Value not in [None, '']:
			right = right + 1
		return sheet.Range(sheet.Cells(row, col), sheet.Cells(bottom, right)).Value


	def read_currentregion_address(self):
		# 이것은 현재의 셀에서 공백과 공백열로 둘러싸인 활성셀영역을 돌려준다
		result = self.check_address_value(self.xlApp.ActiveCell.CurrentRegion.Address)
		return result


	def read_general_value(self):
		# 몇가지 엑셀에서 자주사용하는 것들정의
		# 엑셀의 사용자, 현재의 경로, 화일이름, 현재시트의 이름
		result = []
		result.append(self.xlApp.ActiveWorkbook.Name)
		result.append(self.xlApp.Username)
		result.append(self.xlApp.ActiveWorkbook.ActiveSheet.Name)
		return result

	def read_inputbox_value(self, title="Please Input Value"):
		# 그리드 라인을 없앤다
		temp_result = self.xlApp.Application.InputBox(title)
		return temp_result

	def read_range_address(self):
		temp_address = self.xlApp.Selection.Address
		result = self.check_address_value(temp_address)
		return result


	def read_range_value(self, sheet_name, xyxy):
		# 값을 일정한 영역에서 갖고온다
		# 만약 영역을 두개만 주면 처음과 끝의 영역을 받은것으로 간주해서 알아서 처리하도록 변경하였다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		temp_result = my_range.Value
		result = []
		if 1 < len(temp_result):
			for one_data in temp_result:
				result.append(list(one_data))
		else:
			result = temp_result
		return result


	def read_rangename_address(self, sheet_name, xyxy_name):
		sheet = self.check_sheet_name(sheet_name)
		temp = sheet.Range(xyxy_name).Address
		result = self.check_address_value(temp)
		return result

	def read_rangename_all(self):
		# 현재 시트의 이름을 전부 돌려준다
		# [번호, 영역이름, 영역주소]
		names_count = self.xlBook.Names.Count
		result = []
		if names_count > 0:
			for aaa in range(1, names_count + 1):
				name_name = self.xlBook.Names(aaa).Name
				name_range = self.xlBook.Names(aaa)
				result.append([aaa, str(name_name), str(name_range)])
		return result


	def read_selection_address(self):
		# 현재선택된 영역의 주소값을 돌려준다
		result = ""
		temp_address = self.xlApp.Selection.Address
		print(temp_address)
		temp_list = temp_address.split(",")
		if len(temp_list) == 1:
			result = self.check_address_value(self.xlApp.Selection.Address)
		if len(temp_list) > 1:
			result = []
			for one_address in temp_list:
				result.append(self.check_address_value(one_address))
		return result


	def read_selection_value(self, sheet_name):
		# 값을 일정한 영역에서 갖고온다
		# 만약 영역을 두개만 주면 처음과 끝의 영역을 받은것으로 간주해서 알아서 처리하도록 변경하였다
		sheet = self.check_sheet_name(sheet_name)
		y1, x1, y2, x2 = self.check_address_value(self.read_selection_address())[2]
		result = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2)).Value
		return result

	def read_shape_name(self, sheet_name="", no=""):
		sheet = self.check_sheet_name(sheet_name)
		return sheet.Shapes(no).Name

	def read_sheet_count(self):
		# 시트의 갯수를 돌려준다
		return self.xlBook.Worksheets.Count

	def read_sheet_allname(self):
		# 현재 워크북의 모든 시트알아내기
		temp_list = []
		for var_02 in range(1, self.read_sheet_count() + 1):
			temp_list.append(self.xlBook.Worksheets(var_02).Name)
		return temp_list

	def read_usedrange_address(self, sheet_name):
		# 이것은 usedrange를 돌려주는 것이다. 값은 리스트이며 처음은
		# usedrange의 시작셀 ,두번째는 마지막셀값이며 세번째는 전체영역을 돌려주는 것이다
		sheet = self.xlBook.Worksheets(sheet_name)
		result = self.check_address_value(sheet.UsedRange.address)
		return result

	def read_username(self):
		# 사용자 이름을 읽어온다
		return self.xlApp.Username

	def read_workbook_fullname(self):
		# application의 이름과 전체경로를 돌려준다
		return self.xlBook.FullName

	def read_workbook_name(self):
		# application의 이름을 돌려준다
		return self.xlBook.Name

	def read_workbook_path(self):
		# application의 경로를 돌려준다
		return self.xlBook.Path

	def read_xx_value(self, sheet, xx):
		# 한줄 전체의 값을 읽어온다
		sheet = self.xlBook.Worksheets(sheet)
		return sheet.Range(sheet.Cells(xx[0], 1), sheet.Cells(xx[1], 1)).EntireRow.Value

	def read_yy_value(self, sheet, yy):
		# 한 가로행의 전체값을 갖고온다
		sheet = self.xlBook.Worksheets(sheet)
		return sheet.Range(sheet.Cells(1, yy[0]), sheet.Cells(1, yy[1])).EntireColumn.Value

	def save(self, newfilename=""):
		# 별도의 지정이 없으면 기존의 화일이름으로 저장합니다
		if newfilename == "":
			self.xlBook.Save()
		else:
			print(newfilename)
			self.xlBook.SaveAs(newfilename)

	def select_cell(self, sheet_name, xy):
		# 영역을 선택한다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1, y1))
		my_range.Select()


	def select_range(self, sheet_name, xyxy):
		# 영역을 선택한다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.Select()

	def select_sheet(self, sheet_name):
		self.xlBook.Worksheets(sheet_name).Select()

	def set_cell_bold(self, sheet_name, xyxy):
		# 셀안의 값을 진하게 만든다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.Font.Bold = True

	def set_cell_color(self, sheet_name, xyxy, input_data):
		self.draw_cell_color(sheet_name, xyxy, input_data)

	def draw_cell_color(self, sheet_name, xyxy, input_data):
		# 셀 하나에 색을 입힌다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		result_rgb = self.check_color(input_data)
		my_range.Interior.color = self.rgb_to_hex(result_rgb)

	def set_cell_rgb(self, sheet_name, xyxy, input_data):
		# 셀 하나에 색을 입힌다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.Interior.color = self.rgb_to_hex(input_data)


	def set_column_numberproperty(self, sheet_name, num_col, style):
		# 각 열을 기준으로 셀의 속성을 설정하는 것이다
		sheet = self.xlBook.Worksheets(sheet_name)
		if style == 1:  # 날짜의 설정
			sheet.Columns(num_col).NumberFormatLocal = "mm/dd/yy"
		elif style == 2:  # 숫자의 설정
			sheet.Columns(num_col).NumberFormatLocal = "_-* #,##0.00_-;-* #,##0.00_-;_-* '-'_-;_-@_-"
		elif style == 3:  # 문자의 설정
			sheet.Columns(num_col).NumberFormatLocal = "@"

	def set_formula(self, sheet, xyxy, input_data):
		sheet.Cells(5, 2).Formula = "=Now()"
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.xlBook.Worksheets(sheet)
		output = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2)).Value
		return

	def set_fullscreen(self, fullscreen=1):
		# 총괄적으로 언급하면 시작셍이 a10이고
		# 자료의양이 11개 12개이라면
		# 최종영역을 a10:m22로 만들어주는 것이다
		# 이러한 방법은 자료를 하나하나 넣는것보다 수십배빠르게 많은자료를 넣을수있다
		# 전체화면으로 보기
		self.xlApp.DisplayFullScreen = fullscreen

	def set_gridline_off(self):
		# 그리드 라인을 계속 바꾼다
		self.xlApp.ActiveWindow.DisplayGridlines = 0

	def set_gridline_on(self):
		# 그리드 라인을 계속 바꾼다
		self.xlApp.ActiveWindow.DisplayGridlines = 1

	def set_print_page(self, sheet_name="", **var_dic):
		sheet = self.check_sheet_name(sheet_name)
		sheet.PageSetup.Zoom = False
		sheet.PageSetup.FitToPagesTall = 1
		sheet.PageSetup.FitToPagesWide = 1
		# sheet.PageSetup.PrintArea = print_area
		sheet.PageSetup.LeftMargin = 25
		sheet.PageSetup.RightMargin = 25
		sheet.PageSetup.TopMargin = 50
		sheet.PageSetup.BottomMargin = 50
		# sheet.ExportAsFixedFormat(0, path_to_pdf)
		sheet.PageSetup.LeftFooter = "&D"  # 날짜
		sheet.PageSetup.LeftHeader = "&T"  # 시간
		sheet.PageSetup.CenterHeader = "&F"  # 화일명
		sheet.PageSetup.CenterFooter = "&P/&N"  # 현 page/ 총 page
		sheet.PageSetup.RightHeader = "&Z"  # 화일 경로
		sheet.PageSetup.RightFooter = "&P+33"  # 현재 페이지 + 33

	def set_print_preview(self, sheet):
		# 미리보기기능입니다
		sheet = self.xlBook.Worksheets(sheet)
		sheet.PrintPreview()

	def set_range_autofilter(self, sheet_name, column1, column2=None):
		# 엑셀의 자동필터 기능을 추가한 것입니다
		sheet = self.check_sheet_name(sheet_name)
		if column2 == None:
			column2 = column1
		a = str(column1) + ':' + str(column2)
		sheet.Columns(a).Select()
		sheet.Range(a).AutoFilter(1)

	def set_range_autofit(self, sheet_name="", xyxy=""):
		# 선택한 시트의 모든 컬럼에 대해 자동 맞춤을 한 후에 각 컴럼별로 10px만큼 더 키운다
		# 더 키우는 이유는 보통 프린트할때 문제가 생기는 것을 방지하기 위한 목적이다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range = sheet.Columns(str(y1) + ':' + str(y2))

		if xyxy == "":
			sheet.EntireColumn.AutoFit()
		else:
			sheet.my_y_range.AutoFit()
		for y in range(y1, y2):
			width = sheet.Columns(str(y) + ':' + str(y)).ColumnWidth
			sheet.Columns(str(y) + ':' + str(y)).ColumnWidth = width + 10

	def set_range_bold(self, sheet_name, xyxy):
		# 셀안의 값을 진하게 만든다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		myrange.Font.Bold = True

	def set_range_clear(self, sheet_name, xyxy):
		# clear기능을 한다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		myrange.ClearContents()

	def set_range_font(self, sheet_name, xyxy, font):
		# 영역에 글씨체를 설정한다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(y2, x2))

		my_range.font.Name = font

	def check_color(self, input_color):
		# 색깔에 대한 자료를 받으면 rgb값을 돌려준다
		#Font.Color.ColorIndex = 2
		#ws.Cells(1, 1).Interior.color = rgb_to_hex((218, 36, 238))
		color = halmoney_ccolor.ccolor()
		result_rgb = color.check_color_rgb(input_color)
		return result_rgb

	def rgb_to_hex(self, rgb):
		'''
		ws.Cells(1, i).Interior.color uses bgr in hex

		'''
		bgr = (rgb[2], rgb[1], rgb[0])
		strValue = '%02x%02x%02x' % bgr
		# print(strValue)
		iValue = int(strValue, 16)
		return iValue

	def set_range_fontcolor(self, sheet_name, xyxy, font_color):
		# 영역에 글씨체를 설정한다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		my_range.Font.Color = font_color

	def set_cell_fontcolor(self, sheet_name, xyxy, font_color):
		# 영역에 글씨체를 설정한다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1, y1))
		#my_range.Font.Color = font_color
		result_rgb = self.check_color(font_color)
		#my_range.Interior.color = self.rgb_to_hex(result_rgb)
		my_range.Font.color = self.rgb_to_hex(result_rgb)

	def set_range_fontsize(self, sheet_name, xyxy, size):
		# 영역에 글씨크기를 설정한다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		myrange.font.Size = int(size)


	def set_range_formula(self, sheet_name, xyxy, input_data):
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		myrange.Formula = "=Now()"
		myrange.Value = input_data


	def set_range_merge(self, sheet_name, xyxy):
		# 셀들을 합하는 것이다
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		if x1 == x2:
			sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2)).Merge(0)
		else:
			for a in range(x2 - x1 + 1):
				sheet.Range(sheet.Cells(x1 + a, y1), sheet.Cells(x1 + a, y2)).Merge(0)


	def set_range_numberformat(self, sheet_name, xyxy, numberformat):
		# 영역에 숫자형식을 지정하는 것이다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.NumberFormat = numberformat


	def set_range_unmerge(self, sheet_name, xyxy):
		# 병합된 것을 푸는 것이다
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		my_range.UnMerge()


	def set_rangename(self, sheet_name, xyxy, name):
		# 영역에 이름으로 설정하는 기능
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		my_range = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		self.xlBook.Names.Add(name, my_range)


	def set_sheet_lock(self, sheet_name="", password="1234"):
		# 시트 잠그기
		sheet = self.check_sheet_name(sheet_name)
		sheet.protect(password)


	def set_sheet_unlock(self, sheet_name="", password="1234"):
		# 시트 잠그기 해제
		sheet = self.check_sheet_name(sheet_name)
		sheet.Unprotect(password)


	def set_visible(self, value=1):
		# 실행되어있는 엑셀을 화면에 보이지 않도록 설정합니다
		# 기본설정은 보이는 것으로 되너 있읍니다
		self.xlApp.Visible = value


	def set_wrap_on(self, sheet_name, xyxy, input_data):
		# 셀의 줄바꿈을 설정할때 사용한다
		# 만약 status를 false로 하면 줄바꿈이 실행되지 않는다.
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))

		myrange.WrapText = input_data

	def set_x_length(self, sheet_name, x, height=13.5):
		sheet = self.check_sheet_name(sheet_name)
		sheet.Cells(x, 1).EntireRow.RowHeight = height

	def set_x_numberproperty(self, sheet_name, x0, style):
		# 각 열을 기준으로 셀의 속성을 설정하는 것이다
		sheet = self.check_sheet_name(sheet_name)
		x1 = self.check_xy_address(x0)
		x = self.change_char_num(x1)
		if style == 1:  # 날짜의 설정
			sheet.Columns(x).NumberFormatLocal = "mm/dd/" \
												 ""
		elif style == 2:  # 숫자의 설정
			sheet.Columns(x).NumberFormatLocal = "_-* #,##0.00_-;-* #,##0.00_-;_-* '-'_-;_-@_-"
		elif style == 3:  # 문자의 설정
			sheet.Columns(x).NumberFormatLocal = "@"


	def set_y_length(self, sheet_name, y, height=13.5):
		# 가로열의 높이를 설정하는 것이다
		sheet = self.check_sheet_name(sheet_name)
		new_y = self.check_xy_address(y)
		my_range = sheet.Range(sheet.Cells(new_y[0], 1), sheet.Cells(new_y[1], 5))
		my_range.EntireRow.RowHeight = height

	def show_messagebox(self, data, data1="www.sjpark.org"):
		win32gui.MessageBox(0, data, data1, 0)

	def statusbar(self, sheet, row_or_col):
		# 스테이터스바,  아직 미확인
		sheet = self.xlBook.Worksheets(sheet)
		sheet.Range(str(row_or_col) + ':' + str(row_or_col)).Insert(-4121)

	def write_cell_memo(self, sheet_name, xyxy, text):
		# 셀에 메모를 넣는 것
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		myrange = sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x2, y2))
		myrange.AddComment(text)

	def write_cell_value(self, sheet_name, xyxy, value):
		# 값을 셀에 넣는다. (사용법) write_cell(시트이름, 행번호, 열번호, 넣을값)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet = self.check_sheet_name(sheet_name)
		sheet.Cells(int(x1), int(y1)).Value = str(value)

	def write_cell_value_speed(self, sheet_name, xy, value):
		# 값을 셀에 넣는다. (사용법) write_cell(시트이름, 행번호, 열번호, 넣을값)
		# 시트나 셀영역을 확인하지 않는다
		self.xlBook.Worksheets(sheet_name).Cells(xy[0], xy[1]).Value = value

	def write_range_value(self, sheet_name, xyxy, input_datas):
		# 영역에 값을 써 넣는 것이다
		# 이것은 각셀을 하나씩 쓰는 것이다
		# 입력값과 영역이 맞지 않으면 입력값의 갯수를 더 우선함
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)

		for x in range(len(input_datas)):
			for y in range(len(input_datas[x])):
				sheet.Range(sheet.Cells(x1 + x, y1 + y), sheet.Cells(x1 + x, y1 + y)).Value = input_datas[x][y]

	def write_range_value_speed(self, sheet_name, xyxy, input_datas):
		# 영역에 값을 써 넣는 것이다
		# 이것은 각셀을 하나씩 쓰는 것이다
		# 입력값과 영역이 맞지 않으면 입력값의 갯수를 더 우선함
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1 + len(input_datas), y1 + len(input_datas[0]))).Value = input_datas

	def dump_range_value(self, sheet_name, xyxy, input_datas):
		# 한꺼번에 값을 써넣을때 사용
		sheet = self.check_sheet_name(sheet_name)
		x1, y1, x2, y2 = self.check_address_value(xyxy)
		sheet.Range(sheet.Cells(x1, y1), sheet.Cells(x1 + len(input_datas), y1 + len(input_datas[0]))).Value = input_datas