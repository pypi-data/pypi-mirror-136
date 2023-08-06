This module is for easily read/write with EXCEL using Python.

The target is for easily control for EXCEL.

Therefore pyezxl is focused to control easily as follows.

1) the function name is consist of 3 parts (action_target_role)
   
   read_range_value
   
   write_cell_value
   
   delete_cell_value

2) function name is linked with underbar(_) and text is all lowcase
   
   action words : read, write, Insert, delete, change, set, copy, move
   
   target words : range, sheet, x, y, line
   
   role words : name, color, value, end

3) word definition
   
  * read: when you want to read cell value

    check : read some data except cell value as like color, font etc

  * write : when you want to write cell value

    set : write some data except cell value as like color, line etc

  * cell : 1 cell

    range : minimum 2 cells and over

4) web-site : please visit for more information 

    www.halmoney.com

simple example

    *  When you want to input [A1]="sujin"

        import pyezxl

        excel = pyezxl.pyezxl("")

        excel.write_cell_value("",[1,1],"sujin")

    * When you want to input value in some range

        import pyezxl

        excel = pyezxl.pyezxl("")

        activesheet_name = excel.read_activesheet_name()

        my_range = [2,1,10,5]

        [x1, y1, x2, y2 ] = excel.check_address_value(my_range)
    
        for x in range(x1, x2+1):

            for y in range(y1, y2+1):

                excel.write_cell_value(activesheet_name,[x, y],"sujin" )
