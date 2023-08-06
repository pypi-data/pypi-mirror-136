import re

class scolor:
	def __init__(self):

		self.vars ={} #공통 변수를 설정
		
		self.vars["check_color_name"] = {
			"빨": "red", "적": "red", "red":"red","r": "red", "빨강": "red",
			"주": "ora", "yr": "ora","yellowred":"ora","o":"ora","orange":"ora","ora":"ora","주황": "ora",
			"노": "yel", "y": "yel", "yellow": "yel", "yel": "yel", "노랑": "yel",
			"연": "gy", "gy": "gy", "greenyellow": "gy", "연두": "gy","green-yellow": "gy","yg": "gy",
			"초": "gre", "g": "gre", "green": "gre", "gre": "gre", "녹색": "gre","초록": "gre",
			"연초록":"gc", "green-cyan":"gc","cg":"gc",
			"옥": "cya", "옥색": "cya", "c": "cya","cya": "cya","cyan": "cya",
			"청록": "bc","blue-cyan": "bc","청": "bc", "cb": "bc", "bg": "bc", "bluegreen": "bc",
			"파": "blu", "b": "blu", "blue": "blu", "blu": "blu", "파랑": "blu",
			"남": "bm", "blue-magenta": "bm", "blue_magenta": "bm", "mb": "bm", "bm": "bm", "pb": "bm", "purpleblue": "bm", "violet": "bm", "vio": "bm", "남색": "bm",
			"보": "mag", "magenta": "mag", "m": "mag",
			"자홍": "rm", "red-magenta": "rm", "rm": "rm","red_magenta": "rm","mr": "rm",
			"회": "gra", "회색": "gra", "gra": "gra", "gray": "gra",
			"흰": "whi", "하양": "whi", "white": "whi", "whi": "whi","흰색": "whi",
			"검": "bla", "검정": "bla", "black": "bla", "흑": "bla", "bla": "bla",
			}

		self.vars["change_style_dic"] = {
			"1": "1", "l4": "1", "++++": "1", "white": "1", "pastel": "1", "파스텔": "1", "p": "1","d4": "1",
			"2": "2", "l3": "2", "+++": "2", "pale": "2", "연한": "2", "d3": "2",
			"3": "3", "l2": "3", "++": "3", "light": "3", "밝은": "3", "d2": "3",
			"4": "4", "l1": "4", "+": "4", "soft": "4", "흐린": "4", "d1": "4",
			"5": "5", "l0": "5", "": "5", "vivid": "5", "선명한": "5", "basic": "5", "기본": "5", "d0": "5",
			"6": "6", "l-1": "6", "-": "6", "dull": "6", "탁한": "6", "d-1": "6",
			"7": "7", "l-2": "7", "--": "7", "deep": "7", "진한": "7", "d-2": "7",
			"8": "8", "l-3": "8", "---": "8", "dark": "8", "어두운": "8", "d-3": "8",
			"9": "9", "l-4": "9", "----": "9", "bla": "9", "검정": "9", "black": "9", "검은": "9", "d-4": "9",
			}
		self.vars["color_mode"] ={1:"단색조합", "단색조합":1,"강력한 대기효과와 넓은공간감":1,
				              2:"등간격 3색 조화","등간격 3색 조화":2, "활동적인 인상과 이미지":2,
				              3:"보색", "보색":3, "강력한비교":3,
				              4:"인접색",  "인접색":4,"비슷한색 찾기":4,
				              5:"근접보색조합", "근접보색조합":5,"보색의 강한 인상이 부담스러울때 보색의 근처에있는 색":5,
				              6:"고명도배색", "고명도배색":6,
				              7:"고명도배색+약간더 부드러운 이미지", "고명도배색+약간더 부드러운 이미지":7,
				              8:"중명도배색",  "중명도배색":8,
							  9:"중명도배색+약간더 부드러운 이미지", "중명도배색+약간더 부드러운 이미지":9,
							  10:"저중명도배색",  "저중명도배색":10,
							  11:"저명도배색+약간더 어두운 이미지", "저명도배색+약간더 어두운 이미지":11,
							  12:"명도차가 큰 배색",  "명도차가 큰 배색":12,
							  13:"명도차가 큰 배색 + 근접보색", "명도차가 큰 배색 + 근접보색":13,
							  14:"고채도 배색",  "고채도 배색":14,
							  15:"채도차가 큰 배색", "채도차가 큰 배색":15,
							  16:"저채도 배색", "저채도 배색":16,"차분하고 무거운 이미지":16,
				              }
		self.vars["color_style"] = ["단색조합", "등간격 3색 조화","보색","인접색","근접보색조합",
					           "고명도배색", "고명도배색+약간더 부드러운 이미지",
					           "중명도배색", "중명도배색+약간더 부드러운 이미지", "저중명도배색", "저명도배색+약간더 어두운 이미지",
							   "명도차가 큰 배색", "명도차가 큰 배색 + 근접보색",
							   "고채도 배색", "채도차가 큰 배색", "저채도 배색",]

		self.vars["excel_rgb"] = [[0,0,0], [255,255,255], [255,0,0], [0,255,0], [0,0,255], [255,255,0],
										[255,0,255], [0,255,255], [128,0,0], [0,128,0], [0,0,128], [128,128,0],
										[128,0,128], [0,128,128], [192,192,192], [128,128,128], [153,153,255],
										[153,51,102], [255,255,204], [204,255,255], [102,0,102], [255,128,128],
										[0,102,204], [204,204,255], [0,0,128], [255,0,255], [255,255,0],
										[0,255,255], [128,0,128], [128,0,0], [0,128,128], [0,0,255],
										[0,204,255], [204,255,255], [204,255,204], [255,255,153], [153,204,255],
										[255,153,204], [204,153,255], [255,204,153], [51,102,255], [51,204,204],
										[153,204,0], [255,204,0], [255,153,0], [255,102,0], [102,102,153],
										[150,150,150], [0,51,102], [51,153,102], [0,51,0], [51,51,0],
										[153,51,0], [153,51,102], [51,51,153], [51,51,51]]

		self.vars["basic_rgb"] = [[255, 0, 0],[255, 128, 0],[255, 255, 0],[128, 255, 0],
										[0, 255, 0],[0, 255, 128],[0, 255, 255],[0, 128, 255],
										[0, 0, 255],[128, 0, 255],[255, 0, 255],[255, 0, 128],]


		self.vars["basic_hsl"] = [[0, 100, 50], [30, 100, 50], [60, 100, 50], [90, 100, 50], [120, 100, 50],
						                 [150, 100, 50], [180, 100, 50], [210, 100, 50], [240, 100, 50], [270, 100, 50],
						                 [300, 100, 50], [330, 100, 50]]

		self.vars["h_basic"] = {"red": 0, "ora": 30, "yel": 60, "yg": 90, "gre": 120, "gc":150 , "cya": 180,
				       "cb": 210, "blu": 240, "bm": 270, "mag": 300, "mr": 330, "gra": 0, "whi": 0, "bla": 0, }

		self.vars["s_step"] = {"1": [10], "2": [20], "3": [30], "4": [40],"5": [50], "6": [60], "7": [70], "8": [80], "9": [90], }

		self.vars["l_step"] = {"1": [10], "2": [20], "3": [30], "4": [40],"5": [50], "6": [60], "7": [70], "8": [80], "9": [90], }

		self.vars["sb_step"] = {"1": [100, 80], "2": [100, 77], "3": [100, 68], "4": [100, 59],
				  "5": [100, 50], "6": [90, 41], "7": [80, 32], "8": [70, 23], "9": [60, 14], }

		self.vars["sb_step_small"] = {"1": [0, 12], "2": [0, 9], "3": [0, 6], "4": [0, 3],
				      "5": [0, 0], "6": [0, -3], "7": [0, -6], "8": [0, -9], "9": [0, -12], "0": [0, -14],}

		self.vars["color_index"] = {"red":0, "ora":1, "yel":2, "yg":3, "gre":4, "gc":5, "cya":6, "cb":7, "blu":8, "bm":9, "mag":10, "mr":11, "gra":12, "whi":13, "bla":14}
		self.vars["color_kor"] = ["빨강", "주황", "노랑", "연두", "초록", "연초록", "옥색", "청록", "파랑", "남색", "보라", "자홍", "회색", "흰색", "검정"]
		self.vars["color_eng"] = ["red", "ora", "yel", "yg", "gre", "gc", "cya", "cb", "blu", "bm", "mag", "mr", "gra", "whi", "bla"]
		self.vars["color_eng_s"] = ["r", "o", "y", "yg", "g", "gc", "c", "cb", "b", "bm", "m", "mr", "g", "w", "bl"]
		self.vars["color_style_kor"] = ["파스텔", "연한", "밝은", "흐린", "선명한", "기본", "탁한", "진한", "어두운", "회색", "검은", "검정"]

	def read_colors_rgblist (self):
		# 많이 사용하는 다른 색들을 사용하기 위해
		# 테두리, 폰트색이나 단족으로 나타낼때 사용하면 좋다
		result = self.vars["basic_rgb"][0:13]
		return result

	def read_colors_hsllist (self):
		result = self.vars["basic_hsl"][:-4]
		return result

	def read_soft_colors_rgblist (self):
		# 자료가있는 색들의 배경색으로 사용하면 좋은 색들
		color_set = self.vars["basic_hsl"][:-4]
		result = []
		print(color_set)
		for color_hsl in color_set:
			rgb = self.change_hsl_style(color_hsl, "pastel", 4)
			result.append(rgb)
		return result

	def change_hsl_style (self, input_hsl, color_style, small_change = 5):
		# 입력된 기본 값을 스타일에 맞도록 바꾸는것
		# 스타일을 강하게 할것인지 아닌 것인지를 보는것
		# 입력예 : 기본색상, 적용스타일, 변화정도, "red45, 파스텔, 3
		# 변화정도는 5를 기준으로 1~9까지임

		basic_hsl = input_hsl
		temp = self.vars["change_style_dic"][color_style]
		step_1 = self.vars["sb_step"][str(temp)]
		step_2 = self.vars["sb_step_small"][str(small_change)]

		h = int(basic_hsl[0])
		s = int(step_1[0]) + int(step_2[0])
		l = int(step_1[1]) + int(step_2[1])

		if h > 360 : h = 360 - h
		if s > 100 : s = 100
		if l > 100 : l = 100
		if s < 0 : s = 0
		if l < 0 : l = 0

		r, g, b = self.change_hsl_rgb([h,s,l])

		return [int(r), int(g), int(b)]


	def change_color_style (self, input_color, color_style, style_step = 5):
		# 입력된 기본 값을 스타일에 맞도록 바꾸는것
		# 스타일을 강하게 할것인지 아닌것인지를 보는것
		#입력예 : 기본색상, 적용스타일, 변화정도, "red45, 파스텔, 3
		#변화정도는 5를 기준으로 1~9까지임

		basic_rgb = self.check_color_rgb(input_color)

		basic_hsl = self.change_rgb_hsl(basic_rgb)
		step_1 = self.vars["sb_step"][str(style_step)]
		step_2 = self.vars["sb_step_small"][color_style]

		h = int(basic_hsl[0])
		s = int(basic_hsl[1]) + int(step_1[1]) + int(step_2[1])
		l = int(basic_hsl[2]) + int(step_1[2]) + int(step_2[2])

		changed_rgb = self.change_hsl_rgb([h,s,l])
		return changed_rgb


	def change_rgb_3input (self, colorname, big_no="", small_no=""):
		# 3개의 입력값이 오는 형태로 만든느 것이다
		# "red", "4", "5" => [60,100, 50] ==> [255, 255, 0]

		color_name = self.vars["check_color_name"][colorname]
		result_1 = self.vars["h_basic"][color_name]
		result_2 = self.vars["sb_step"][str(big_no)]
		result_3 = self.vars["sb_step_small"][str(small_no)]

		h_value = result_1
		s_value = result_2[0] + result_3[0]
		l_value = result_2[1] + result_3[1]

		if color_name =="whi" or color_name =="bla" or color_name =="gra":
			final_rgb = self.get_rgb_wbg (color_name, big_no, small_no)
		else:
			result = [h_value/360, s_value/100, l_value/100]
			result_rgb = self.change_hsl_rgb(result)
			final_rgb = [result_rgb[0] * 255, result_rgb[1] * 255, result_rgb[2] * 255]
		return final_rgb

	def get_color_rgb(self, input_data="red45"):
		rgb = self.change_color_rgb(input_data="red45")
		return rgb

	def get_color_hsl(self, input_data="red45"):
		rgb = self.change_color_rgb(input_data)
		hsl = self.change_rgb_hsl(rgb)
		return hsl


	def get_rgb_wbg (self, color_name, big_no, small_no):
		# white, black, gray에대한 부분은 다시 정리해서 적용하도록 한다
		#print("white, black, gray ===>", color_name, big_no, small_no)
		basic_rgb = 0
		rgb_diff = (5 - int(big_no)) * 25 + (5 - int(small_no)) * 3
		if color_name =="whi":
			basic_rgb = 255 + rgb_diff
			if basic_rgb >= 255: basic_rgb =255
		elif color_name =="gra":
			basic_rgb = 128 + rgb_diff
		elif color_name =="whi":
			basic_rgb = rgb_diff
			if basic_rgb <= 0: basic_rgb = 0
		return [basic_rgb, basic_rgb, basic_rgb]

	def check_input_data(self, input_data="red45"):
		l_no_gap = 0
		number_only = ""
		color_name =""

		# 새롭게 정의해 보자
		re_com = re.compile("[0-9]+")
		re_no = re_com.findall(input_data)

		if re_no == []:
			l_no_gap = 0
		elif len(input_data) == len(re_no[0]):
				number_only = int(re_no[0])
		else:
			l_no_gap = int(re_no[0]) -50


		re_com = re.compile("[^0-9-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]+")
		re_str = re_com.findall(input_data)
		if re_str != []:
			color_name = self.vars["check_color_name"][re_str[0]]

		re_com = re.compile("[+]+")
		re_plus = re_com.findall(input_data)
		if re_plus != []:
			l_no_gap = 5 * len(re_plus[0])

		re_com = re.compile("[-]+")
		re_minus = re_com.findall(input_data)
		if re_minus != []:
			l_no_gap = -5 * len(re_minus[0])
		result = [number_only, color_name, l_no_gap]
		print(result)
		return result

	def check_color_rgb (self, input_data = "red45"):
		result = self.change_color_rgb(input_data)
		return result

	def change_color_rgb (self, input_data = "red45"):

		[number_only, color_name, l_no_gap] = self.check_input_data(input_data)
		print(number_only, color_name, l_no_gap)
		l_code_dic = {"bla": 0, "gra": 50, "whi": 100}


		if number_only == "":
			color_index = self.vars["color_index"][color_name]
			print(color_index)

		if number_only != "":
			#만약 숫자만 입력을 햇다면
			print("숫자만 입력을 했네요")
			new_rgb = self.vars["excel_rgb"][int(number_only)]
		elif number_only == "" and color_name !="" and l_no_gap == 0:
			#입력내용에 색이름만 언급되었을때 (red)
			print("입력내용에 색이름과번호가 있을때 (red)")
			h_code, s_code, l_code = self.vars["basic_hsl"][color_index]
			print(h_code, s_code, l_code)
			temp_rgb = self.change_hsl_rgb([h_code, s_code, l_code])
			print(temp_rgb)

			r_no, g_no, b_no = [temp_rgb[0], temp_rgb[1], temp_rgb[2]]
			new_rgb = [int(r_no), int(g_no), int(b_no)]

		else:
			#입력내용에 색이름과번호가 있을때 (red45)
			print("입력내용에 색이름과번호가 있을때 (red45)")
			if color_name =="whi" or color_name =="bla" or color_name =="gra":
				h_code = 0
				s_code = 0
				l_code = l_code_dic[color_name] + l_no_gap
			else:
				h_code = self.vars["h_basic"][color_name]
				s_code = 100
				l_code = 50 + int(l_no_gap)
				print(h_code,s_code,l_code )

			if int(l_code) > 100 : l_code = 100
			if int(l_code) < 0 : l_code = 0
			temp_rgb = self.change_hsl_rgb([h_code, s_code, l_code])
			#r_no, g_no, b_no = [int(temp_rgb[0] * 255), int(temp_rgb[1] * 255), int(temp_rgb[2] * 255)]
			r_no, g_no, b_no = [temp_rgb[0], temp_rgb[1], temp_rgb[2]]

			if r_no > 255:	r_no = 255
			if g_no > 255: g_no = 255
			if b_no > 255: b_no = 255
			new_rgb = [int(r_no), int(g_no), int(b_no)]

		print("========", input_data, new_rgb)
		return new_rgb

	def read_near_colors (self, input_color = "red", step = 10):
		#하나의 색을 지정하면 10가지의 단계로 색을 돌려주는 것이다
		result =[]
		for no in range(0,100,int(100/step)):
			temp = self.check_color_rgb(input_color+str(no))
			result.append(temp)
		return result


	def get_near_colors (self, input_color = "red", step = 10):
		#하나의 색을 지정하면 10가지의 단계로 색을 돌려주는 것이다
		result =[]
		for no in range(0,100,int(100/step)):
			temp = self.check_color_rgb(input_color+str(no))
			result.append(temp)
		return result


	def read_colors_name(self):
		#기본 13가지 색의 리스트
		result = list(self.vars["color_eng"].keys())
		return result

	def get_color_mix(self, color1, color2):
		#두가지색을 믹스한 색을 돌려준다
		# 다음에 만들어야 징ㅇㅇㅇㅇ
		pass


	def change_rgb_hsl (self, rgb):
		# 입력은 0~255사이의 값
		r,g,b = rgb
		r = float(r / 255)
		g = float(g / 255)
		b = float(b / 255)
		max1 = max(r, g, b)
		min1 = min(r, g, b)
		l = (max1 + min1) / 2

		if max1 == min1:
			s = 0
		elif l < 0.5:
			s = (max1 - min1) / (max1 + min1)
		else:
			s = (max1 - min1) / (2 - max1 - min1)

		if s ==0:
			h = 0
		elif r >= max(g, b):
			h = (g - b) / (max1 - min1)
		elif g >= max(r, b):
				h = 2+ (b - r) / (max1 - min1)
		else:
				h = 4+ (r - g) / (max1 - min1)
		h = h *60
		if h > 360 : h = h -360
		if h < 0 : h = 360 -h

		return [int(h), int(s*100), int(l*100)]

	def change_hsl_rgb(self, hsl):
		h, s, l = hsl
		h = float(h / 360)
		s = float(s / 100)
		l = float(l / 100)

		if s == 0:
			R = l * 255
			G = l * 255
			B = l * 255

		if l < 0.5:
			temp1 = l * (1 + s)
		else:
			temp1 = l + s - l * s

		temp2 = 2 * l - temp1

		#h = h / 360

		tempR = h + 0.333
		tempG = h
		tempB = h - 0.333

		if tempR < 0: tempR = tempR + 1
		if tempR > 1: tempR = tempR - 1
		if tempG < 0: tempG = tempG + 1
		if tempG > 1: tempG = tempG - 1
		if tempB < 0: tempB = tempB + 1
		if tempB > 1: tempB = tempB - 1

		if 6 * tempR < 1:
			R = temp2 + (temp1 - temp2) * 6 * tempR
		else:
			if 2 * tempR < 1:
				R = temp1
			else:
				if 3 * tempR < 2:
					R = temp2 + (temp1 - temp2) * (0.666 - tempR) * 6
				else:
					R = temp2

		if 6 * tempG < 1:
			G = temp2 + (temp1 - temp2) * 6 * tempG
		else:
			if 2 * tempG < 1:
				G = temp1
			else:
				if 3 * tempG < 2:
					G = temp2 + (temp1 - temp2) * (0.666 - tempG) * 6
				else:
					G = temp2
		if 6 * tempB < 1:
			B = temp2 + (temp1 - temp2) * 6 * tempB
		else:
			if 2 * tempB < 1:
				B = temp1
			else:
				if 3 * tempB < 2:
					B = temp2 + (temp1 - temp2) * (0.666 - tempB) * 6
				else:
					B = temp2
		R = abs(round(R * 255,0))
		G = abs(round(G * 255,0))
		B = abs(round(B * 255,0))

		return [R, G, B]

	def manual(self):
		result = """
		색을 변경하고 관리하는 모듈이며
		색의 변화를 잘 사용이 가능하도록 하기위한 것이다
		
		# 기본 입력 예 : "빨강", "빨강55", "red55", "0155"
		# 기본색 ==> 12색 + (하양, 검정, 회색),
		# 큰변화 ==> 1~9단계, 작은변화 ==> 1~9단계
		# 기본함수 : get_color_rgb("red55"),  get_rgb_3input(색, 큰변화, 작은변화)
		# 모든색의 표현이나 결과는 rgb로 돌려준다
		"""
		return result

	def change_rgb_int(self, input_data):
		# rgb인 값을 color에서 인식이 가능한 값으로 변경하는 것이다
		result = (int(input_data[2])) * (256 ** 2) + (int(input_data[1])) * 256 + int(input_data[0])
		return result