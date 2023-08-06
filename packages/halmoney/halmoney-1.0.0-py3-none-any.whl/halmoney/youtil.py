# -*- coding: utf-8 -*-
from PIL import ImageFont
import shutil
import zipfile
import os
from konlpy.tag import *
import re
import pickle
import time
import string

# 문자나 자료들을 관리하는 모듈
# 문자열인Character에서 따가지고 왔으며, 아들 성철이의 C자의 의미

class youtil:

	def add_data(self, raw_data, added_data, status):
		# 자료에 하나씩 어떤자료를 추가하는 기능
		# raw_data = ['qweqw','qweqweqw','rterert','gdgdfgd',23,534534,'박상진']
		# added_data = "new_data"
		# status=3
		# 각 3번째 마다 자료를 추가한다면

		var_1, var_2 = divmod(len(raw_data), status)
		for num in range(var_1, 0, -1):
			raw_data.insert(num * status - var_2 + 1, added_data)
		return raw_data

	def add_sum_everage(self, raw_data, status):
		# 넘어온 자료의 마직막부분에 합계, 평균을 자동적으로 만들어서 넣어주는 기능
		a = 111
		return a

	def calendar(self):
		# 날짜를 포함한 자료가 들어오면 달력으로 만들어 주는것
		a = 111
		return a

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

	def change_stringonly_cap(self, results):
		#자료중 문자열만 대문자로 변경한다, 그러나 이것은 리스트안에 리스트가있는 2차 리스트까지만 가능하다
		final_datas=[]
		temp_datas=[]
		for datas in results:
			for data in datas:
				if type(data) == type('a') :
					temp_datas.append(str(data).upper)
				else:
					temp_datas.append(data)
			final_datas.append(temp_datas)
			temp_datas=[]
		return final_datas

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

	def check_same_list(self, list_mother, list_son):
		#두개의 리스트를 비교해서 같은것을 찾는 것이다
		result = list_mother
		for one in range(len(list_son)):
			found = 0
			for two in range(len(list_mother)):
				if list_son[one][0] == list_mother[two][0]:
					found = 1
			if found == 0:
				result.append(list_son[one])
				print("새로운것 발견 ===>")
		return result

	def compare_two_value(self, raw_data,req_number,project_name,vendor_name,nal):
		#위아래 비교
		#회사에서 사용하는 inq용 화일은 두줄로 구성이 된다
		#한줄은 client가 요청한 스팩이며
		#나머지 한줄은 vendor가 deviation사항으로 만든 스팩이다
		#이두가지의 스팩을 하나로 만드는 것이다
		#즉, 두줄에서 아래의 글씨가 있고 그것이 0, None가 아니면 위의것과 치환되는 것이다
		#그런후 이위의 자료들만 따로 모아서 돌려주는 것이다
		self.data=list(raw_data)
		self.data_set=[]
		self.data_set_final=[]

		for num_1 in range(0,len(self.data),2):
			for num_2 in range(len(self.data[1])):
				if not(self.data[num_1+1][num_2]==self.data[num_1][num_2]) and self.data[num_1+1][num_2]!= None and self.data[num_1+1][num_2]!= 0:
					self.data_set.append(self.data[num_1+1][num_2])
				else:
					self.data_set.append(self.data[num_1][num_2])
			self.data_set.append(req_number)
			self.data_set.append(project_name)
			self.data_set.append(vendor_name)
			self.data_set.append(nal)
			self.data_set_final.append(self.data_set)
			self.data_set=[]
		return self.data_set_final

	def change_value_sort (self, a,b=0):
		#aa = [[111, 'abc'], [222, 222],['333', 333], ['777', 'sjpark'], ['aaa', 123],['zzz', 'sang'], ['jjj', 987], ['ppp', 'park']]
		#value=sjpark_sort(aa,1)
		#정렬하는 방법입니다
		result_before = [(i[b], i) for i in a]
		result_before.sort()
		result = [i[1] for i in result_before]
		return result

	def copy_file(self, old_path, new_path):
		# 화일복사
		# 화일 이름을 다르게 변경해서 복사가능
		old_path = self.check_file(old_path)
		new_path = self.check_file(new_path)
		shutil.copy(old_path, new_path)

	def copy_file_with_meta(self, old_path, new_path):
		# 화일복사
		old_path = self.check_file(old_path)
		new_path = self.check_file(new_path)
		shutil.copy2(old_path, new_path)

	def copy_folder(self, old_path, new_path):
		# 폴더복사
		shutil.copy(old_path, new_path)

	def change_column_value(self, temp_title):
		for temp_01 in [[" ", "_"], ["(", "_"], [")", "_"], ["/", "_per_"], ["%", ""], ["'", ""], ['"', ""], ["$", ""],
						["__", "_"], ["__", "_"]]:
			temp_title = temp_title.replace(temp_01[0], temp_01[1])
		if temp_title[-1] == "_": temp_title = temp_title[:-2]
		return temp_title

	def change_waste_data(self, original_data):
		# 영문과 숫자와 공백을 제거하고는 다 제거를 하는것
		result = []
		for one_data in original_data:
			temp = ""
			for one in one_data:
				if str(one) in ' 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
					temp = temp + str(one)
			result.append(temp)
		return result

	def change_value(self, raw_data, before, after, status):
		# 자료의 들어가있는 값을 바꾸는 기능입니다
		a = 111
		return a

	def change_sec_time(self, input_data=""):
		# input_data = 123456
		step_1 = divmod(int(input_data), 60)
		step_2 = divmod(step_1[0], 60)
		final_result = [step_2[0], step_2[1], step_1[1]]
		return final_result

	def change_time_sec(self, input_data=""):
		# input_data = "14:06:23"
		re_compile = re.compile("\d+")
		result = re_compile.findall(input_data)
		total_sec = int(result[0]) * 3600 + int(result[1]) * 60 + int(result[2])
		return total_sec

	def change_string_cap(self, datas, argue=1):
		# 대소문자를 변경하는 것입니다
		# 이것은 단일 리스트만 가능하게 만들었다,  리스트안에 리스트가있는것은 불가능하다 (2004년 5월 2일 변경)
		# 기본은 대문자로 바꾸는 것이다
		results = []
		for data in datas:
			print (data)
			if argue == 0: result = str(data).lower  # 모두 소문자로
			if argue == 1: result = str(data).upper  # 모두 대문자로
			if argue == 2: result = str(data).capitalize  # 첫글자만 대문자
			if argue == 3: result = str(data).swapcase  # 대소문자 변경
			results.append(result)
		return results

	def change_lower_value(self, data):
		# 모든 리스트의 자료를 소문자로 만드는것이다
		# 이것은 단일 리스트만 가능하게 만들었다
		# 리스트안에 리스트가있는것은 불가능하다
		# string모듈을 import하여야 한다
		for a in range(len(data)):
			data[a] = str(data[a]).lower
		return data

	def check_file(self, file):
		# 입력자료가 폴더를 갖고있지 않으면 현재 폴더를 포함해서 돌려준다
		if len(file.split(".")) > 1:
			result = file
		else:
			cur_dir = self.read_current_path()
			result = cur_dir + "\\" + file
		return result

	def change_value_lower (self, data):
		#모든 리스트의 자료를 소문자로 만드는것이다
		#이것은 단일 리스트만 가능하게 만들었다
		#리스트안에 리스트가있는것은 불가능하다
		#string모듈을 import하여야 한다
		for a in range(len(data)):
			data[a] =str(data[a]).lower
		return data

	def change_month_eng (self, month):
		#이것은 월을 숫자로 받아서 문자로 돌려주는 것입니다 ---> ['MAR', 'MARCH']
		month_short = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
		month_long = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST', 'SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER']
		return [month_short[month-1],month_long[month-1]]

	def change_data_row_column(self):
		# 자료의 가로와 세로의 자료를바꾸는것
		a = 111
		return a

	def change_day_eng(self, no):
		# 이것은 그날을 서수로 돌려주는 것입니다 ---> ['1ST']
		data = ['1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH', '10TH', '11TH', '12TH', '13TH', '14TH',
				'15TH', '16TH', '17TH', '18TH', '19TH', '20TH', '21ST', '22ND', '23RD', '24TH', '25TH', '26TH', '27TH',
				'28TH', '29TH', '30TH', '31ST']
		return data[no - 1]

	def check_time_inputdata(self, time_char=""):
		self.time_char =time_char
		if self.time_char == "":
			lt = time.localtime()
		else:
			lt = time.localtime(self.time_char)
		return self.time_char

	def change_address_num (self, input_datas):
		#영문으로 되어있는 주소를 아라비아숫자로 변경하는 것이다
		#예전이름 : def address_all (self, input_datas)
		input_datas=str(input_datas).lower
		arange = string.replace(input_datas,"$","").split(":")
		if len(arange)==1: 	arange.append(arange[0])

		if string.lower(arange[0]) in string.lowercase and string.lower(arange[1]) in string.lowercase:
			arange[0]=arange[0]+"0"
			arange[1]=arange[1]+"65536"

		if string.lower(arange[0]) in string.digits and string.lower(arange[1]) in string.digits:
			arange[0]="a"+arange[0]
			arange[1]="iv"+arange[1]

		result=[]
		for a in arange:
			if string.lower(a[0]) in string.lowercase and string.lower(a[1]) in string.lowercase:
				result.append(a[0:2])
				result.append(a[2:])
			else:
				result.append(a[0])
				result.append(a[1:])

		if result[0]:
			if len(result[0])==1:
				result[0]= (string.lowercase.index(result[0])+1)
			else:
				aaa=(string.lowercase.index(result[0][0])+1)*26
				result[0]=aaa+ (string.lowercase.index(result[0][1])+1)

		if result[2]:
			if len(result[2])==1:
				result[2]= (string.lowercase.index(result[2])+1)
			else:
				aaa=(string.lowercase.index(result[2][0])+1)*26
				result[2]=aaa+ (string.lowercase.index(result[2][1])+1)
		final_data = [int(result[1]),int(result[0]),int(result[3]),int(result[2]), input_datas] #2005-02-17 추가
		return final_data

	def delete_holsu_value(self, data):
		# 홀수값을 삭제
		for a in range(len(data)):
			if (a % 2) == 0:
				data[a] = []
		return data

	def delete_zzacsu_value(self, data):
		# 짝수값을 삭제
		for a in range(len(data)):
			if (a % 2 - 1) == 0:
				data[a] = []
		return data

	def delete_file(self, old_path):
		# 화일삭제
		old_path = self.check_file(old_path)
		os.remove(old_path)

	def delete_step_value(self, data, num):
		# 원하는 순서째의 자료를 삭제하기
		data.insert(0, [])
		for a in range(len(data)):
			if (a % num) == 0:
				data[a] = []
		result = data[1:]
		return result

	def delete_same_value(self, input_datas, status=0):
		# 중복된 리스트의 자료를 없애는 것이다. 같은것중에서 하나만 남기고 나머지는 []으로 고친다
		if status == 0:
			result = []
			# 계속해서 pop으로 하나씩 없애므로 하나도 없으면 그만 실행한다
			while len(input_datas) != 0:
				gijun = input_datas.pop()
				sjpark = 0
				result.append(gijun)
				for number in range(len(input_datas)):
					if input_datas[int(number)] == []:  # 빈자료일때는 그냥 통과한다
						pass
					if input_datas[int(number)] == gijun:  # 자료가 같은것이 있으면 []으로 변경한다
						sjpark = sjpark + 1
						input_datas[int(number)] = []
			else:
			# 중복된것중에서 아무것도없는 []마저 없애는 것이다. 위의 only_one을 이용하여 사용한다
			# 같은것중에서 하나만 남기고 나머지는 []으로 고친다
			# 이것은 연속된 자료만 기준으로 삭제를 하는 것입니다
			# 만약 연속이 되지않은 같은자료는 삭제가 되지를 않읍니다
				result = list(self.only_one(input_datas))
		for a in range(len(result) - 1, 0, -1):
				if result[a] == []:
					del result[int(a)]
		return result

	def del_space(self):
		# 자료의 앞뒤에있는 스페이스를제거하는 함수
		a = 111
		return a

	def del_word(self):
		# 문장내의 특정한 글자를 제거하는것
		a = 111
		return a

	def delete_same_of_mine(self, input_list):
		# 리스트로 받은 자료에서 순서는 지키면서 같은것을 삭제하는 것이다
		# 하나씩 돌리면서 나머지 자료에서
		result = input_list
		total_no = len(input_list)
		print(total_no)
		for num_1 in range(total_no):
			base_data = input_list[num_1]
			print(base_data, total_no-num_1)
			if base_data != "":
			#빈것은 그냥 넘어가도록 한다
				for num_2 in range(num_1+1, total_no):
					if base_data == input_list[num_2]:
						result[num_2] = ""
		return result

	def delete_over_2_lines(self, file_name):
		# 빈행이 1줄 이상이 되는것은 지우는 것이다
		f = open(file_name, 'r', encoding='UTF8')
		lines = f.readlines()
		num = 0
		result = []
		for one_line in lines:
			#num = num + 1
			if len(one_line) == 1:
				num = num + 1
				if num > 2:
						print("빈칸이 두줄 이상 ===>>>>")
						pass
				else:
						result.append(one_line)
						num=0
			else:
				result.append(one_line)
				num = 0

		for one in result:
			print(one)

		return result

	def delete_2nd_empty_lines(self, file_name):
		#화일을 읽어 내려가다가 2줄이상의 띄어쓰기가 된것을 하나만 남기는것
		f = open(file_name, 'r', encoding='UTF8')
		lines = f.readlines()
		num = 0
		result = ""
		for one_line in lines:
			if one_line =="\n":
				num=num+1
				if num == 1:
					result = result + str(one_line)
				elif num > 1:
					#print("2줄발견")
					pass
			else:
				num = 0
				result = result + str(one_line)
		print(result)
		return result

	def delete_folder(self, old_dir):
		# 폴더삭제
		# 폴더안에 자료가 있어도 삭제
		shutil.rmtree(old_dir)

	def delete_folder_empty(self, old_dir):
		# 폴더삭제
		# 폴더안에 자료가 없어야 삭제
		os.rmdir(old_dir)

	def delete_continious_value (self, input_datas):
		# 연속된 자료중 같은 값이 있으면 값을 삭제하는 것이다
		# 1차원리스트만 가능하게 하였다
		temp_basic = ""
		for one_num in range(len(input_datas) - 1):
			if one_num == 0:
				temp_basic = input_datas[one_num]
			elif temp_basic == input_datas[one_num + 1]:
				input_datas[one_num + 1] = []
			else:
				temp_basic = input_datas[one_num]
		return input_datas

	def delete_contineous_value (self, input_datas):
		if len(input_datas)==0:
			print ("아무자료도 없읍니다. 확인 바랍니다")
			pass
		else:
			a=0
			while a!=len(input_datas)-1:
				if input_datas[a]==input_datas[a+1]: input_datas[a]=[]
				a=a+1
		return input_datas

	def delete_same_cell (self, input_datas):
		if len(input_datas)==0:
			print ("아무자료도 없읍니다. 확인 바랍니다")
			pass
		else:
			a=0
			while a!=len(input_datas)-1:
				if input_datas[a]==input_datas[a+1]: input_datas[a]=[]
				a=a+1
		return input_datas

	def delete_value_even(self, input_list):
		# 짝수값을 삭제
		for a in range(len(input_list)):
			if (a % 2 - 1) == 0:
				input_list[a] = []
		return input_list

	def delete_value_step(self, input_list, num):
		# 원하는 순서째의 자료를 삭제하기
		input_list.insert(0, [])
		for a in range(len(input_list)):
			if (a % num) == 0:
				input_list[a] = []
		result = input_list[1:]
		return result

	def delete_odd_value (self, data):
		#홀수값을 삭제
		#이것은 아래의 del_step으로 대치가능하다
		for a in range(len(data)):
			if (a%2) == 0:
				data[a]=[]
		return data

	def delete_value_same (self, input_datas, status=0):
		#중복된 리스트의 자료를 없애는 것이다. 같은것중에서 하나만 남기고 나머지는 []으로 고친다
		if status==0:
			result = []
			#계속해서 pop으로 하나씩 없애므로 하나도 없으면 그만 실행한다
			while len(input_datas)!=0:
				gijun = input_datas.pop()
				sjpark = 0
				result.append(gijun)
				for number in range(len(input_datas)):
					if input_datas[int(number)] == [] : #빈자료일때는 그냥 통과한다
						pass
					if input_datas[int(number)] == gijun :#자료가 같은것이 있으면 []으로 변경한다
						sjpark = sjpark+1
						input_datas[int(number)]=[]

		else:
			#중복된것중에서 아무것도없는 []마저 없애는 것이다. 위의 only_one을 이용하여 사용한다
			#같은것중에서 하나만 남기고 나머지는 []으로 고친다
			#이것은 연속된 자료만 기준으로 삭제를 하는 것입니다
			#만약 연속이 되지않은 같은자료는 삭제가 되지를 않읍니다
			result = list(input_datas) #여기는 잘못됨 result = list(only_one(input_datas))
			for a in range(len(result)-1,0,-1):
				if result[a]==[]:
					del result[int(a)]
		return result

	def english_to_korea(self, raw_data, status):
		# 영문으로된 숫자를 한글이나 서수로 만들어 주는것
		a = 111
		return a

	def file_in_folder (self, old_path=""):
		# 폴더안의 화일을 리스트로 돌려주기
		if old_path =="": old_path = self.read_current_path()
		# 경로가 없으면 현재의 폴더를 설정한다
		result = os.listdir(old_path)
		return result


	def get_pixel_size(self, input_text, font_size, font_name):
		# 폰트와 글자를 주면, 필셀의 크기를 돌려준다
		font = ImageFont.truetype(font_name, font_size)
		size = font.getsize(input_text)
		return size

	def get_diagonal_xy(self, xyxy=[5, 9, 12, 21]):
		# 좌표와 대각선의 방향을 입력받으면, 대각선에 해당하는 셀을 돌려주는것
		# 좌표를 낮은것 부터 정렬하기이한것 [3, 4, 1, 2] => [1, 2, 3, 4]
		result = []
		if xyxy[0] > xyxy[2]:
			x1, y1, x2, y2 = xyxy[2], xyxy[3], xyxy[0], xyxy[1]
		else:
			x1, y1, x2, y2 = xyxy

		x_height = abs(x2 - x1) + 1
		y_width = abs(y2 - y1) + 1
		step = x_height / y_width
		temp = 0

		if x1 <= x2 and y1 <= y2:
			# \형태의 대각선
			for y in range(1, y_width + 1):
				x = y * step
				if int(x) >= 1:
					final_x = int(x) + x1 - 1
					final_y = int(y) + y1 - 1
					if temp != final_x:
						result.append([final_x, final_y])
						temp = final_x
		else:
			for y in range(y_width, 0, -1):
				x = x_height - y * step

				final_x = int(x) + x1
				final_y = int(y) + y1 - y_width
				temp_no = int(x)

				if temp != final_x:
					temp = final_x
					result.append([final_x, final_y])
		return result


	def insert_value_step(self, input_datas, num, input_data):
		# 리스트에 일정한 간격으로 같은자료를 반복해서 자료를 넣고 싶을때
		total_number = len(input_datas)
		dd = 0
		for a in range(len(input_datas)):
			if a % num == 0 and a != 0:
				if total_number != a:
					input_datas.insert(dd, input_data)
					dd = dd + 1
			dd = dd + 1
		return input_datas

	def list_folder(self):
		# 특정 폴더안의 화일의 정보를 갖고오는것
		a = 111
		return a

	def make_list_on_re_compile(self, re_txt, file_name):
		#텍스트화일을 읽어서 re에 맞도록 한것을 리스트로 만드는 것이다
		# 함수인 def를 기준으로 저장을 하며, [[공백을없앤자료, 원래자료, 시작줄번호].....]
		re_com = re.compile(re_txt)
		f = open(file_name, 'r', encoding='UTF8')
		lines = f.readlines()
		num = 0
		temp = ""
		temp_original = ""
		result = []
		for one_line in lines:
			aaa = re.findall(re_com, str(one_line))
			original_line = one_line
			changed_line = one_line.replace(" ","")
			changed_line = changed_line.replace("\n","")

			if aaa:
				result.append([temp, temp_original, num])
				temp = changed_line
				temp_original = original_line
				#print("발견", num)
			else:
				temp = temp + changed_line
				temp_original = temp_original + one_line
		return result

	def move_file(self, old_path, new_dir):
		# 화일을 이동시키는것
		old_path = self.check_file(old_path)
		shutil.move(old_path, new_dir)

	def move_folder(self, old_dir, new_dir):
		# 폴더를 이동시키는것
		shutil.move(old_dir, new_dir)

	def make_2_digit(self, input_data):
		input_data = str(input_data)
		if len(input_data) == 1 :
			result = "0"+ input_data
		else:
			result = input_data
		return result

	def make_folder(self, old_dir):
		# 폴더 만들기
		os.mkdir(old_dir)

	def now(self, time_char=""):
		self.time_char =time_char
		if self.time_char == "":
			lt = time.localtime()
		else:
			lt = time.localtime(self.time_char)
		self.year =self.make_2_digit(lt.tm_year)
		self.mon = self.make_2_digit(lt.tm_mon)
		self.day = self.make_2_digit(lt.tm_mday)
		self.hour = self.make_2_digit(lt.tm_hour)
		self.min = self.make_2_digit(lt.tm_min)
		self.sec = self.make_2_digit(lt.tm_sec)
		self.weekday = str(lt.tm_wday)
		self.yearday = str(lt.tm_yday)
		return [self.year, self.mon, self.day,self.hour,self.min,self.sec,self.weekday,self.yearday]

	def num_str_eng(self, number):
		getdigit = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
		num = ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
		num_10 = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'eighteen', 'nineteen']
		num_1000 = ['thousand', 'million', 'billion', 'trillion']
		num_last = ['no', 'one', 'dollars']
		num_last_cent = ['only', 'and one cent', 'and', 'cents']
		aa = ['', '', '', '', '', '', '', '', '', '', '', '', '']
		aaaa = ['', '', '', '', '', '', '', '', '', '', '', '', '']

	def pick_up_max_data(self):
		# 자료중에서 가장 큰값이나 작은값을 찾아내는것

		# 그것을 기준으로 찾아서 자료를 넣어주는 기능
		a = 111
		return a

	def reverse_alt_enter(self):
		# Alt+Enter로 한셀이 여러 값들이 들어있는 것들을 하나의 셀로 분리를 하는 기능
		a = 111
		return a

	def read_pickle(self, file_name="save_file"):
		with open(file_name, "rb") as fr:
			original_file = pickle.load(fr)
		return original_file

	def read_sum_value (self, data):
		#어떤 자료의 합계, 평균, 갯수, 최대, 최소 돌려주기
		total=0
		for a in data:
			total=total+a
		eval = total  / len(data)
		return [total, eval, len(data), max(data), min(data)]

	def rename_file(self, old_path, new_path):
		# 화일이름 변경
		old_path = self.check_file(old_path)
		new_path = self.check_file(new_path)
		os.rename(old_path, new_path)

	def rename_folder(self, old_path, new_path):
		# 폴더이름 변경
		os.rename(old_path, new_path)

	def read_current_path(self, path=""):
		# 현재의 경로를 돌려주는것
		result = os.getcwd()
		return result

	def save_pickle(self, input_data, file_name="save_file"):
		with open(file_name, "wb") as fw:
			pickle.dump(input_data, fw)

	def sort_list_2d(self, input_list, sort_index=1):
		#input_list의 기준에 따라서, 2차원의 자료를 기준으로 정렬하는것이다
		# index는 2차원을 정리하는 기준을 정하는 것이다
		input_list.sort(key=lambda x: x[sort_index])
		return input_list

	def split_eng_num(self, data):
		# 단어중에 나와있는 숫자, 영어를 분리하는기능
		re_compile = re.compile(r"([a-zA-Z]+)([0-9]+)")
		result = re_compile.findall(data)
		new_result = []
		for dim1_data in result:
			for dim2_data in dim1_data:
				new_result.append(dim2_data)
		return new_result

	def split_num_char(self, raw_data, status):
		# 숫자와문자를 나누어주는 것입니다
		a = 111
		return a
	def splitter(self, n, s):
		# 문자열을 몇개씩 숫자만큼 분리하기
		# ['123456'] => ['12','34','56']
		result = []
		for i in range(0, len(s), n):
			result.append("".join(s[i:i + n]))
		return result
	def seperate_num_char(self, raw_data):
		#2005년 12월 9일 추가
		#문자와숫자를 분리해서 리스트로 돌려주는 것이다
		#123wer -> ['123','wer']
		#분류라는 의미 -> seperate를 사용하고, 어떤것들을 분리할지를 언급한다 (숫자, 문자)
		temp=""
		result = []
		int_temp=""
		datas=str(raw_data)
		for num in range(len(datas)):
			if num==0:
				temp=str(datas[num])
			else:
				try:
					fore_var=int(datas[num])
					fore_var_status="integer"
				except:
					fore_var=datas[num]
					fore_var_status="string"
				try:
					back_var=int(datas[num-1])
					back_var_status="integer"
				except:
					back_var=datas[num-1]
					back_var_status="string"

				if fore_var_status==back_var_status:
					temp=temp+datas[num]
				else:
					result.append(temp)
					temp=datas[num]
		if len(temp)>0:
			result.append(temp)
		return result
	def splite_unique(self, raw_data, del_or_blank=0):
		# 이것은 똑같은 자료가 있으면 그자료를 맨처음의 것만을 남기고 없애는 것이다
		# 이것을 클래스로 만들어 본다

		before = list(raw_data)
		blank = []
		for dd in range(len(before[0])):
			blank = blank.append('')

		for a in range(len(before) - 1):
			gijun_data = before[a]

			for b in range(a + 1, len(before)):
				cmp_data = before[b]

				result = self.cmp(gijun_data, cmp_data)
				if result == 0:
					before[b] = blank
		return before

	def sort(self, raw_data, status):
		# 정렬하기
		a = 111
		return a

	def split_kor_words(self, input_text):
		# 문장을 갖고와서 단어별로 품사를 나누는 것이다
		komoran = Komoran(userdic="C:\\Python38-32/sjpark_dic.txt")

		input_text = input_text.replace("\n", ", ")
		input_text = input_text.replace(" ", ", ")
		input_text = input_text.strip()

		split_value = komoran.pos(input_text)
		print(split_value)

		# Save pickle
		with open("data.pickle", "wb") as fw:
			pickle.dump(split_value, fw)


	def time_day_value (self, time_char=time.localtime(time.time())):
		#일 -----> ['05', '095']
		return [time.strftime('%d',time_char),time.strftime('%j',time_char)]

	def time_hour_value (self, time_char=time.localtime(time.time())):
		#시 -----> ['10', '22', 'PM']
		return [time.strftime('%I',time_char),time.strftime('%H',time_char),time.strftime('%P',time_char)]

	def time_minute_value (self, time_char=time.localtime(time.time())):
		#분 -----> ['07']
		return [time.strftime('%M',time_char)]

	def time_month_value (self, time_char=time.localtime(time.time())):
		#월 -----> ['04', 'Apr', 'April']
		return [time.strftime('%m',time_char),time.strftime('%b',time_char),time.strftime('%B', time_char)]

	def time_second_value(self, time_char=time.localtime(time.time())):
		#초 -----> ['48']
		return [time.strftime('%S',time_char)]

	def time_today_value(self, time_char=time.localtime(time.time())):
		#종합 -----> ['04/05/02', '22:07:48', '04/05/02 22:07:48','2002-04-05']
		#040621 : 이름을 변경 (total -> today)
		aaa = string.split(time.strftime('%c',time_char))
		total_dash = time.strftime('%Y', time_char)+"-"+time.strftime('%m',time_char)+"-"+time.strftime('%d',time_char)
		return [aaa[0], aaa[1], time.strftime('%c',time_char), total_dash]

	def time_week_value(self, time_char=time.localtime(time.time())):
		#주 -----> ['5', '13', 'Fri', 'Friday']
		return [time.strftime('%w',time_char),time.strftime('%W',time_char),time.strftime('%a',time_char),time.strftime('%A',time_char)]

	def time_year_value(self, time_char=time.localtime(time.time())):
		#년 -----> ['02', '2002']
		return [time.strftime('%y', time_char), time.strftime('%Y', time_char)]

	def today(self):
		lt = time.localtime()
		self.year =self.make_2_digit(lt.tm_year)
		self.mon = self.make_2_digit(lt.tm_mon)
		self.day = self.make_2_digit(lt.tm_mday)
		total_dash = self.year + "-" + self.mon + "-" + self.day
		return total_dash


	def two_list_caculator(self, list_1, list_2, result_type = "|"):
		#두개의 리스트를 +-/*를 하는것
		if result_type == "|":
			result = list(set(list_1) | set(list_2))
		if result_type == "&":
			result = list(set(list_1) & set(list_2))
		if result_type == "-":
			result = list(set(list_1) - set(list_2))
		if result_type == "^":
			result = list(set(list_1) ^ set(list_2))
		return result

	def write_sheet_line_1 (self, data, number = 1,input_data=[]):
		#리스트에 일정한 간격으로 자료삽입
		total_number = len(data)
		dd=0
		for a in range(len(data)):
			if a%number == 0 and a!=0:
				if total_number!=a:
					data.insert(dd,input_data)
					dd=dd+1
			dd=dd+1
		return data

	def write_line_sheet (self, data_value, number = 1,input_data=[]):
		#리스트에 일정한 간격으로 자료삽입
		total_number = len(data_value)
		dd=0
		for a in range(len(data_value)):
			if a%number == 0 and a!=0:
				if total_number!=a:
					data_value.insert(dd,input_data)
					dd=dd+1
			dd=dd+1
		return data_value

	def week_number(self):
		# 특정한날이 그 년도의 몇번째인지 알아내고, 설정이 없을경우는 오늘을 기준으로 하기
		a = 111
		return a


	def zip_file(self, file_one, new_path):
		# 1개의 화일을 zip으로 압축하는것

		new_zip = zipfile.ZipFile(new_path, 'w')
		# 압축한후의 화일이름
		new_zip.write(file_one, compress_type=zipfile.ZIP_DEFLATED)
		# 압축할 화일
		new_zip.close()

	def zip_files(self, zip_name_path, new_path_all):
		# 화일들을 zip으로 압축하는것
		with zipfile.ZipFile(zip_name_path, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
			for one in new_path_all:
				new_zip.write(one)