#  -*- coding: utf-8 -*-
import pyglet
from pyglet.gl import * #opengl을 불르는것
from pyglet.window import mouse
from pyglet.window import key
from pyglet import shapes

#기본 공통변수를 나열한다
vars = {}
vars["cell_x"] = 0
vars["cell_y"] = 0
vars["screen_x_length"] = 500
vars["screen_y_length"] = 450
vars["start_x"] = 10
vars["start_y"] = 20
vars["basic_x_lengh"] = 50 #기본높이
vars["basic_y_lengh"] = 50
vars["basic_x_count"] = 25 #한페이지에 나나탈 선수
vars["basic_y_count"] = 25
vars["var_x_positions"] = []
vars["var_y_positions"] = [] #모든 셀들의 위치를 저장한다
vars["input_string"] = ""
vars["current_x1"] = 0
vars["current_y1"] = 0
vars["current_x2"] = 0
vars["current_y2"] = 0
vars["background_color"] = (255, 55, 55)
vars["line_range"] = 3 #
vars["mouse_x"] = -100
vars["mouse_y"] = -100
vars["cell_values"] = {"1_1":"세종대왕", "2_2":"1234", "3_3":"ABC"} #셀의 위치와 값을 표시한다 예: [1,1] = "abcd"

#기본정보를 만드는 곳이다
for no in range(int(vars["screen_x_length"] / vars["basic_x_lengh"])+1):
    vars["var_x_positions"].append(no*vars["basic_x_lengh"])
print(vars["var_x_positions"])

for no in range(int(vars["screen_y_length"] / vars["basic_y_lengh"])+1):
    vars["var_y_positions"].append(vars["screen_y_length"] - no*vars["basic_y_lengh"])
print(vars["var_y_positions"])

window = pyglet.window.Window(vars["screen_x_length"], vars["screen_y_length"], caption='Pyezxl', )
batch = pyglet.graphics.Batch()


def draw_grid():
    global vars
    #가로세로의 그리드를 만들어 주는 것이다
    pyglet.gl.glColor4f(0.23, 0.23, 0.93, 1.0)

    for i in range(len(vars["var_x_positions"])):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v2i', ( vars["var_x_positions"][i], 0, vars["var_x_positions"][i], vars["screen_y_length"]) ))

    for i in range(len(vars["var_y_positions"])):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v2i', ( 0, vars["var_y_positions"][i], vars["screen_x_length"], vars["var_y_positions"][i]     ) ))


def write_text():
    global vars
    for cell_xy in list(vars["cell_values"].keys()):
        cord_x, cord_y = cell_xy.split("_")
        xx = vars["var_x_positions"][int(cord_x)-1]
        yy = vars["var_y_positions"][int(cord_y)]
        label = pyglet.text.Label(vars["cell_values"][cell_xy],
                                  font_name='Times New Roman',
                                  font_size=11,
                                  color = (242, 222,212,223),
                                  x=int(xx), y=int(yy)+10,
                                  anchor_x='left', anchor_y='center')
        label.draw()

def start_cell_position(x, y):
    global vars
    #셀의 위치를 넣으면 셀의 시작 주소를 돌려준다
    vars["start_x"] = vars["var_x_positions"][int(x)]
    vars["start_y"] = vars["var_y_positions"][int(y)]
    return vars["start_x"], vars["start_y"]

def check_cell_position(x, y):
    global vars
    #마우스의 위치를 받으면, 셀의 위치를 돌려준다
    #print("마우스의 위치는 ==>", x, y)
    for no in range(len(vars["var_x_positions"])):
        if vars["var_x_positions"][no] > int(x) :
            vars["cell_x"] = no
            break

    for no in range(len(vars["var_y_positions"])):
        if vars["var_y_positions"][no] < int(y) :
            vars["cell_y"] = no
            break

    x1 = vars["var_x_positions"][vars["cell_x"] - 1]
    y1 = vars["var_y_positions"][vars["cell_y"]]
    x2 = vars["var_x_positions"][vars["cell_x"]]
    y2 = vars["var_y_positions"][vars["cell_y"] -1]

    vars["current_x1"] = x1
    vars["current_y1"] = y1
    vars["current_x2"] = x2
    vars["current_y2"] = y2
    #print(x1, y1, x2, y2)
    return vars["cell_x"], vars["cell_y"], x1, y1, x2, y2


def set_color(xyxy="", color_no=(255, 55, 55)):
    global vars
    if xyxy=="":
        new = check_cell_position(vars["mouse_x"],vars["mouse_y"])
        xyxy = new[2:]
    red_sequare = shapes.Rectangle(xyxy[0],xyxy[1],xyxy[2]-xyxy[0],xyxy[3]-xyxy[1], color=vars["background_color"], batch=batch)
    window.clear()
    batch.draw()

def mouse_press(x, y, button, modifiers):
    global vars
    if button == mouse.LEFT:
        print('The left mouse button was pressed.')
    xy = check_cell_position(x,y)
    vars["mouse_x"] = x
    vars["mouse_y"] = y
    set_color([xy[2], xy[3], xy[4], xy[5]])

    vars["current_x1"] = x
    vars["current_y1"] = y

    #if x


def keyboard_input(symbol, modifiers):
    global vars

    if symbol == key.ENTER:
        print('The enter key was pressed.')
        vars["input_string"]=""
    elif symbol == key.LEFT:
        print('left')
        if int(vars["cell_x"]) < 2:
            pass
        else:
            vars["cell_x"] = int(vars["cell_x"]) - 1
        result = start_cell_position(int(vars["cell_x"]), int(vars["cell_y"]))
        vars["mouse_x"] = result[0]-10

    elif symbol == key.RIGHT:
        if int(vars["cell_x"]) > len(vars["var_x_positions"]) - 2:
            pass
        else:
            vars["cell_x"] = int(vars["cell_x"]) + 1

        result = start_cell_position(int(vars["cell_x"]), int(vars["cell_y"]))
        vars["mouse_x"] = result[0]+10

    elif symbol == key.UP:
        print('up')
        if int(vars["cell_y"]) != 1:
            vars["cell_y"] = int(vars["cell_y"]) - 1
        else:
            pass
        result = start_cell_position(int(vars["cell_x"]), int(vars["cell_y"]))
        vars["mouse_y"] = result[1]+10

    elif symbol == key.DOWN:
        print('down')
        if int(vars["cell_y"]) > len(vars["var_y_positions"]) - 2:
            pass
        else:
            vars["cell_y"] = int(vars["cell_y"]) + 1
        result = start_cell_position(int(vars["cell_x"]), int(vars["cell_y"]))
        vars["mouse_y"] = result[1]+10
    elif symbol == key.DELETE:
        temp_key = str(vars["cell_x"])+"_"+str(vars["cell_y"])
        if temp_key in list(vars["cell_values"].keys()):
            vars["cell_values"][temp_key] = ""
        else:
            pass
    elif symbol == key.BACKSPACE:
        print(key.symbol_string(symbol))
        temp_key = str(vars["cell_x"])+"_"+str(vars["cell_y"])
        if temp_key in list(vars["cell_values"].keys()):
            vars["cell_values"][temp_key] = vars["cell_values"][temp_key][:-1]
        else:
            pass
    else:
        one_string = str(key.symbol_string(symbol))
        print(one_string)
        temp_key = str(vars["cell_x"])+"_"+str(vars["cell_y"])

        if one_string in ["_0","_1","_2","_3","_4","_5","_6","_7","_8","_9"]:
            one_string = one_string[1]

        if temp_key in list(vars["cell_values"].keys()):
            vars["cell_values"][temp_key] = vars["cell_values"][temp_key] + str(one_string)
        else:
            vars["cell_values"][temp_key] = str(one_string)

    re_draw()

def re_draw():
    global vars
    window.clear()
    if vars["mouse_x"] == -100:
        pass
    else:
        set_color()
    draw_grid()
    write_text()

def start():
    window.push_handlers(
        on_key_press=keyboard_input,
        on_mouse_press=mouse_press,
        on_draw=re_draw,
    )

start()
pyglet.app.run()