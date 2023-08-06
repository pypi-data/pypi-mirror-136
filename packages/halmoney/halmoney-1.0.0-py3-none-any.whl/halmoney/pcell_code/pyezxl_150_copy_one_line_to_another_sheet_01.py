#  -*- coding: utf-8 -*-

import pyezxl
excel = pyezxl.pyezxl("activeworkbook")
active_sheet = excel.read_activesheet_name()
activecell = excel.read_activecell_range()

# 다른시트에 현재 위치한 한줄을 특정 위치에 복사하기
print(activecell)
excel.copy_range_x(active_sheet, "paste_sheet", activecell[0], 1)

