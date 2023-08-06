from turtle import *
#left(190)
#setheading(90)


def exec(local):
    fillcolor('#50c7ff')
    move(0, -local)
    begin_fill()
    circle(190, extent=360, steps=None)
    end_fill()
    fillcolor('#fff')
    begin_fill()
    circle(160, extent=360, steps=None)
    end_fill()
    move(0, 320-local)


def move(x, y):
    penup()
    goto(x, y)
    pendown()

def oval1(len=3, up=0.2):
    for i in range(88):
        if 0 <= i < 42 or 60 <= i < 90:
            forward(3)
            right(3)
            len += up
        else:
            forward(len)
            right(3)
            len -= up


def oval(len=3, up=0.2, r=False, all = 120):
    for i in range(all):
        if 0 <= i < 30 or 60 <= i < 90:
            len -= up
        else:
            len += up
        forward(len)
        if r:
            right(3)
        else:
            left(3)


# def cat():
    # color('red', 'yellow')
    # penup()
    # goto(75, -75)
    # pendown()
    # left(30)
    # circle(150, extent=300, steps=None)
    # left(30)
    # forward(15)
    # left(145)
    # circle(-155, extent=50, steps=None)
    # right(10)
    # circle(-135, extent=80, steps=None)
    # right(10)
    # circle(-130, extent=80, steps=None)

#circle(-130, extent=80, steps=None)
# right(9)
# circle(-150, extent=55, steps=None)


# begin_fill()
# while True:
#     forward(200)
#     left(170)
#     if abs(pos()) < 1:
#         break
# #end_fill()


def tongue(len=3, up=0.2, r=True):
    for i in range(53):
        # if 0 <= i < 30 or 60 <= i < 90:
        #     len -= up
        # else:
        if i <= 51:
            len += up
        forward(len)
        if r:
            right(3)
        else:
            left(3)


def exec():
    title("Christmas 2021")
    setup(1920, 1080, 0, 0)
    bgcolor("#FFCC0E")
    loca = 60
    pensize(3)
    exec(loca)
    #setheading(144)
    setheading(90)
    fillcolor("#fff")
    begin_fill()
    #眼睛
    oval(3, 0.06, True)
    oval(3, 0.06, False)
    end_fill()
    move(8, 320-loca - 5)
    # 眼线
    pensize(5)
    circle(-10, extent=180, steps=None)
    # 鼻子
    move(-8, 320-loca - 5)
    setheading(90)
    circle(10, extent=180, steps=None)
    pensize(3)
    # 鼻子反光
    move(0, 320-loca - 67)
    setheading(0)
    fillcolor("#b04141")
    begin_fill()
    circle(22, extent=360, steps=None)
    end_fill()
    move(-3, 320-loca - 45)
    color("#fff")
    begin_fill()
    circle(7, extent=360, steps=None)
    end_fill()
    color("#000")
    # 鼻子
    move(0, 320-loca - 67)
    goto(0,  320-loca - 120)
    # 上胡子
    move(-40, 320-loca - 61)
    goto(-130,  320-loca - 50)
    move(40, 320-loca - 61)
    goto(130,  320-loca - 50)
    # 上胡子
    move(-43, 320-loca - 81)
    goto(-133,  320-loca - 80)
    move(43, 320-loca - 81)
    goto(133,  320-loca - 80)
    # 下胡子
    move(-40, 320-loca - 101)
    goto(-130,  320-loca - 110)
    move(40, 320-loca - 101)
    goto(130,  320-loca - 110)

    # 长胡子

    move(0,  320-loca - 120)
    goto(128,  320-loca - 130)
    circle(30, extent=205, steps=None)
    move(0,  320-loca - 120)
    goto(-125,  320-loca - 130)
    right(30)
    circle(-30, extent=205, steps=None)

    # 嘴
    fillcolor("#932e17")
    move(-125,  320-loca - 130)
    setheading(270)
    begin_fill()
    circle(126.5, extent=180, steps=None)
    goto(0,  320-loca - 120)
    goto(-125,  320-loca - 130)
    end_fill()

    # 舌头
    setheading(270)
    circle(126.5, extent=50, steps=None)
    x = xcor()
    y = ycor()
    h = heading()
    fillcolor("#ff5f3a")
    begin_fill()
    setheading(120)
    tongue(1, 0.048)
    x1 = xcor()
    y1 = ycor()
    h1 = heading()
    move(x, y)
    setheading(h)
    circle(126.5, extent=80, steps=None)
    setheading(60)
    tongue(1, 0.05, False)
    goto(x1, y1)
    end_fill()


    # 左胳膊
    fillcolor("#50c7ff")
    move(-115, -40 - 19)
    begin_fill()
    setheading(215)
    circle(85, extent=34, steps=None)

    yt = ycor()
    xt = xcor()
    move(-115, -40 - 19)
    # 右胳膊
    move(115, -40 - 19)

    setheading(325)
    circle(-85, extent=34, steps=None)
    move(0, yt - 50)
    move(xt, yt)
    end_fill()


    # 左手
    setheading(10)
    fillcolor("#fff")
    begin_fill()
    circle(-35, extent=360, steps=None)
    end_fill()
    # 左手

    move(-xcor(), ycor())
    begin_fill()
    setheading(170)
    circle(35, extent=360, steps=None)
    end_fill()
    #
    #
    # fillcolor("#fff")
    
    
    
    
    # begin_fill()
    # setheading(0)
    # end_fill()
    # circle(-35, extent=360, steps=None)

    # 左身体
    move(-115, -40-50)
    fillcolor("#50c7ff")
    begin_fill()
    setheading(268)
    circle(1000, extent=8.8, steps=None)
    xt = xcor()
    yt = ycor()
    move(-115, -40-50)
    # 右身体
    move(115, -40-50)
    setheading(272)
    circle(-1000, extent=8.8, steps=None)
    move(xt, yt)
    end_fill()
    # 肚子
    setheading(0)
    # move(0, 320-loca - 285)
    #
    # circle(-95, extent=360, steps=None)
    move(0, 320-loca - 293)
    fillcolor("#fff")
    begin_fill()
    oval(6, 0.097, True, 30)
    forward(5)
    circle(-95, extent=180, steps=None)
    move(0, 320-loca - 293)
    setheading(180)
    oval(6, 0.097, False, 30)
    forward(5)
    end_fill()
    y = ycor()



    # 红线
    move(0, 320-loca - 280)

    fillcolor("red")
    begin_fill()
    goto(-118, 320-loca - 280)
    setheading(230)
    circle(30, extent=80, steps=None)
    goto(118, ycor())
    setheading(50)
    circle(30, extent=80, steps=None)
    goto(0, 320-loca - 280)
    end_fill()
    move(0,  320-loca - 300)
    y1 = ycor()
    print(y1)
    # 铃铛
    fillcolor("#ede84c")
    begin_fill()
    setheading(180)
    circle(30, extent=360, steps=None)
    end_fill()
    circle(30, extent=70, steps=None)
    begin_fill()
    setheading(20)
    circle(-90, extent=40, steps=None)
    right(18)
    circle(-7, extent=170, steps=None)
    left(11.09)
    circle(90, extent=35, steps=None)
    right(30)
    circle(-7, extent=170, steps=None)
    end_fill()
    move(0,  320-loca - 360)
    goto(0,  320-loca - 350)
    fillcolor("#b6b5a8")
    begin_fill()
    circle(7, extent=360, steps=None)
    end_fill()

    move(0,  y)
    goto(85,  y)
    setheading(270)
    circle(-85, extent=180, steps=None)
    goto(0,  y)

    # 裤裆
    move(0, y - 85 - 25)
    goto(10, ycor())
    goto(-10, ycor())
    goto(0, ycor())
    goto(0, ycor() - 20)




    #fillcolor("#FFCC0E")
    #begin_fill()

    yt = ycor()

    setheading(355)
    circle(500, 12.1)
    hy1 = heading()
    #move(xcor(), ycor() - 100)
    move(0, yt)
    setheading(185)
    circle(-500, 12.1)
    hy2 = heading()



    #move(xcor(), ycor() - 100)
    #move(-xcor(), ycor() - 100)
    #end_fill()
    move(0, yt)

    # 脚
    fillcolor("#fff")
    begin_fill()
    goto(0, yt - 40)
    setheading(320)
    circle(60, 40)
    circle(1000, 3)

    left(3)
    forward(3)
    #left(3)
    forward(3)
    circle(30, 146.5)

    setheading(180+hy1)
    circle(-500, 12.1)
    #move(0, y - 85 - 25-23)
    move(0, yt - 40)
    end_fill()
    begin_fill()
    setheading(220)
    circle(-60, 40)
    circle(-1000, 3)

    right(3)
    forward(3)
    #right(3)
    forward(3)
    circle(-30, 146.5)
    setheading(180+hy2)
    circle(500, 12.1)
    end_fill()
    # shapesize(0.2, 0.2, 12)
    #hideturtle()
    move(270, 320-loca - 280)
    write("@敏敏呀", font=('Vladimir Script', 8, 'normal'))
    move(130, 320-loca - 330)
    write("Happy Christmas", font=('Vladimir Script', 48, 'normal'))

    done()