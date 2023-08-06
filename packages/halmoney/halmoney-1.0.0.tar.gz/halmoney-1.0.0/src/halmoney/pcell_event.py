import win32com.client as win32
import sys
import pyezxl

#제 모듈을 설치하지 않으신분은 관련된것을 삭제하고 실행 하셔도 실행은 됩니다
excel = pyezxl.pyezxl("")

def sample_code_1(input):
    result = str(input)+"맞아요 맞아요!!"
    return result

def sample_code_2():
    result = excel.read_time_now()
    return result

def sample_code_3():
    color = excel.color()
    address = excel.read_activecell_address()
    excel.set_cell_color("", [int(address[0]) + 1, int(address[1]) + 1], color["pink"])


class ApplicationEvents:
    def OnNewWorkbook(self, *args):
        print("Application Event - OnNewWorkbook 새로운 워크북을 만드셨네요")

    def OnSheetActivate(self, *args):
        print("Application Event - OnSheetActivate 다른 시트로 옮기셨네요")

    def OnActivate(self, *args):
        print("Application Event - OnActivate 엑셀창이 실행됩니다")

    def OnSheetBeforeDoubleClick(self, *args):
        print("Application Event - OnSheetBeforeDoubleClick 더블클릭 전에")

    def OnSheetBeforeRightClick(self, *args):
        print("Application Event - OnSheetBeforeRightClick 오른쪽 클릭전에")

    def OnSheetCalculate(self, *args):
        print("Application Event - OnSheetCalculate 계산하고나서")

    def OnSheetChange(self, *args):
        print("Application Event - OnSheetChange 셀의 뭔가가 바뀌고 나서")
        output_value = sample_code_3()

    def OnSheetDeactivate(self, *args):
        print("Application Event - OnSheetDeactivate 워크시트가 비활성화 될때")

    def OnSheetSelectionChange(self, *args):
        print("Application Event - OnSheetSelectionChange 시트의무엇인가가 변경되엇읍니다")
        output_value = sample_code_1("이건 Application 이벤트")
        excel.write_cell_value("",args[1].Address, output_value)

    def OnWindowActivate(self, *args):
        print("Application Event - OnWindowActivate 엑셀용 창이 실행 되었네요")

    def OnWindowDeactivate(self, *args):
        print("Application Event - OnWindowDeactivate 엑셀화일이 종료하네요")

    def OnWindowResize(self, *args):
        print("Application Event - OnWindowResize 창의 크기를 변경하셨네요")

    def OnWorkbookActivate(self, *args):
        print("Application Event - OnWorkbookActivate 워크북이 활성화됩니다실행됩니다")

    def OnWorkbookBeforeClose(self, *args):
        print("Application Event - OnWorkbookBeforeClose 워크북이 꺼지기 전에 실행되는것")

    def OnWorkbookBeforSave(self, *args):
        print("Application Event - OnWorkbookBeforSave 저장되기 전에")

    def OnWorkbookDeactivate(self, *args):
        print("Application Event - OnWorkbookDeactivate 워크북이 비활성화 될때")

    def OnWorkbookNewSheet(self, *args):
        print("Application Event - OnWorkbookNewSheet 새로운시트를 만들때")

    def OnWorkbookOpen(self, *args):
        print("Application Event - OnWorkbookOpen 새로운 워크북을 열때")

class WorkbookEvents:
    def OnActivate(self, *args):
        print("Workbook    Event - OnActivate 워크북이 활성화됩니다실행됩니다")

    def OnBeforeClose(self, *args):
        print("Workbook    Event - OnBeforeClose 워크북이 꺼지기 전에 실행되는것")

    def OnBeforSave(self, *args):
        print("Workbook    Event - OnBeforSave 저장되기 전에")

    def OnDeactivate(self, *args):
        print("Workbook    Event - OnDeactivate 워크북이 비활성화 될때")

    def OnNewSheet(self, *args):
        print("Workbook    Event - OnNewSheet 새로운시트를 만들때")

    def OnOpen(self, *args):
        print("Workbook    Event - OnOpen 새로운 워크북을 열때")

    def OnSheetActivate(self, *args):
        print("Workbook    Event - OnSheetActivate 워크시트가 활성화되면 실행됩니다")

    def OnSheetBeforeDoubleClick(self, *args):
        print("Workbook    Event - OnSheetBeforeDoubleClick 더블클릭 전에")

    def OnSheetBeforeRightClick(self, *args):
        print("Workbook    Event - OnSheetBeforeRightClick 오른쪽 클릭전에")

    def OnSheetCalculate(self, *args):
        print("Workbook    Event - OnSheetCalculate 계산하고나서")

    def OnSheetChange(self, *args):
        print("Workbook    Event - OnSheetChange 셀의 뭔가가 바뀌고 나서")

    def OnSheetDeactivate(self, *args):
        print("Workbook    Event - OnSheetDeactivate 워크시트가 비활성화 될때")

    def OnSheetSelectionChange(self, *args):
        print("Workbook    Event - OnSheetSelectionChange 시트의 무엇인가가 변경되었읍니다")
        output_value = sample_code_1("이건 워크북 이벤트")
        excel.write_cell_value("",args[1].Address, output_value)

    def OnWindowActivate(self, *args):
        print("Workbook    Event - OnWindowActivate 엑셀용 창이 실행 되었네요")

    def OnWindowDeactivate(self, *args):
        print("Workbook    Event - OnWindowDeactivate 엑셀화일이 종료하네요")

    def OnWindowResize(self, *args):
        print("Workbook    Event - OnWindowResize 창의 크기를 변경하셨네요")

class SheetEvents:
    def OnActivate(self, *args):
        print("Sheet       Event - OnActivate 워크시트가 활성화됩니다실행됩니다")

    def OnSheetBeforeDoubleClick(self, *args):
        print("Sheet       Event - OnSheetBeforeDoubleClick 더블클릭 전에 실행")

    def OnBeforeRightClick(self, *args):
        print("Sheet       Event - OnBeforeRightClick 오른쪽 클릭전에")
        output_value = sample_code_2()
        address = excel.read_activecell_address()
        # 마우스 오른쪽 클릭을 했을떼 왼쪽으로 위로 한칸 올라가서 시간을 찍는것이다
        # 그러니 1열과 행에서 찍으면 에러가 난다
        excel.write_cell_value("",[int(address[0]), int(address[1])], "이건 시트 이벤트")
        excel.write_cell_value("",[int(address[0])-1, int(address[1])-1], output_value)

    def OnCalculate(self, *args):
        print("Sheet       Event - OnCalculate 계산하고나서")

    def OnChange(self, *args):
        print("Sheet       Event - OnChange 셀의 뭔가가 바뀌고 나서")

    def OnDeactivate(self, *args):
        print("Sheet       Event - OnDeactivate 워크시트가 비활성화 될때")

    def OnSelectionChange(self, *args):
        print("Sheet       Event - OnSelectionChange 시트의무엇인가가 변경되엇읍니다")
        #print(args)
        #print("args[1].Address ===>", args[1].Address)
        #args[0].Range("A1").Value = "You selected cell " + str(args[1].Address)
        #output_value = sample_code_1("여긴어디")
        #excel.write_cell_value("",args[1].Address, output_value)


xl = win32.dynamic.Dispatch("Excel.Application")
xl.Visible = 1

xl_events = win32.WithEvents(xl, ApplicationEvents)
xb = xl.ActiveWorkbook
xl_workbook_events = win32.WithEvents(xb, WorkbookEvents)

xs = xl.ActiveSheet
xl_sheet_events = win32.WithEvents(xs, SheetEvents)


keepOpen = True

while keepOpen:
    try:
        # 워크북이 하나라도 있으면 엑셀을 살리고
        if xl.Workbooks.Count != 0:
            keepOpen = True
        # 없으면 끝낸다
        else:
            keepOpen = False
            xl = None
            sys.exit()
    except:
        pass


import win32com.client as win32
import sys
import pyezxl

#제 모듈을 설치하지 않으신분은 관련된것을 삭제하고 실행 하셔도 실행은 됩니다
excel = pyezxl.pyezxl("")

def sample_code(input):
	result = str(input)+"???"
	return result

class ApplicationEvents:
	def OnSheetActivate(self, *args):
		print('You Activated a new sheet.')

	def OnSheetChange(self, *args):
		print("Sheet에서 뭔가를 변경")

class WorkbookEvents:
	def OnSheetSelectionChange(self, *args):
		print(args)
		print(args[1].Address)
		args[0].Range('A1').Value = 'You selected cell ' + str(args[1].Address)
		output_value = sample_code("여긴어디")
		excel.write_cell_value("",args[1].Address, output_value)