---
title: Turtle
date: "2018-05-28"
draft: false
active: true
categories: code
tags: python

# View.
#   1 = List
#   2 = Compact
#   3 = Card
view: 2

# Schedule page publish date (NOT talk date).
publishDate: ""
---
python有一个专门用来绘图的库turtle，最近用它画了个小猪佩奇，代码如下：
<!--more-->
```python
from turtle import *
screensize(800,600,'lemonchiffon')
setup(startx=100,starty=100)
p = Turtle()
p.speed(11)
p.pensize(3)
#画躯干
p.penup()
p.goto(-200,-15)
p.pendown()
p.pencolor('blue')
p.fillcolor('skyblue')
p.begin_fill()
p.right(95)
p.circle(1000,8)
p.circle(100,90)
p.circle(1000,12)
p.circle(100,100)
p.circle(1000,7)
p.end_fill()
#画头
p.pencolor('hotpink')
p.fillcolor('pink')
p.penup()
p.goto(-180,110)
p.pendown()
p.begin_fill()
p.left(70)
p.forward(100)
p.circle(-120,190)
p.circle(-3000,5)
p.circle(-300,30)
p.circle(-150,135)
p.circle(-3000,4)
p.circle(-50,90)
p.circle(-3000,3)
p.end_fill()
#画四肢
#画手臂
p.penup()
p.goto(-200,-60)
p.left(100)
p.pendown()
p.forward(200)
#画手指
p.penup()
p.goto(-360,-100)
p.right(40)
p.pendown()
p.forward(50)

p.penup()
p.goto(-360,-100)
p.left(80)
p.pendown()
p.forward(40)
#画手臂
p.penup()
p.goto(150,-60)
p.left(120)
p.pendown()
p.forward(200)
#画手指
p.penup()
p.goto(320,-75)
p.left(50)
p.pendown()
p.forward(40)

p.penup()
p.goto(320,-75)
p.right(100)
p.pendown()
p.forward(40)
#画腿
p.penup()
p.goto(-80,-230)
p.right(35)
p.pendown()
p.forward(85)

p.penup()
p.goto(80,-200)
p.pendown()
p.forward(115)
#画鞋
p.pencolor('black')
p.fillcolor('black')
p.begin_fill()
p.penup()
p.goto(-100,-315)
p.right(90)
p.pendown()
p.circle(1000,2)
p.circle(30,180)
p.circle(1000,2)
p.circle(30,180)

p.penup()
p.goto(60,-315)
p.pendown()
p.circle(1000,2)
p.circle(30,180)
p.circle(1000,2)
p.circle(30,180)
p.end_fill()
#画眼睛
p.pencolor('hotpink')
p.fillcolor('white')
p.begin_fill()
p.penup()
p.goto(-100,270)
p.pendown()
p.circle(40,360)
p.end_fill()

p.begin_fill()
p.penup()
p.goto(20,240)
p.pendown()
p.circle(40,360)
p.end_fill()
#画眼珠
p.pencolor('black')
p.fillcolor('black')
p.begin_fill()
p.penup()
p.goto(-80,240)
p.pendown()
p.circle(15,360)
p.end_fill()

p.begin_fill()
p.penup()
p.goto(40,210)
p.pendown()
p.circle(15,360)
p.end_fill()
#画嘴巴
p.penup()
p.pencolor("hotpink")
p.goto(-160,60)
p.left(110)
p.pendown()
p.circle(60,130)
#画斑
p.penup()
p.pencolor("hotpink")
p.fillcolor("lightpink")
p.begin_fill()
p.goto(140,90)
p.pendown()
p.circle(50,360)
p.end_fill()
#画耳朵
p.penup()
p.goto(0,295)
p.pendown()
p.begin_fill()
p.circle(1000,4)
p.circle(30,200)
p.circle(1000,4)
p.end_fill()

p.penup()
p.goto(70,280)
p.left(140)
p.pendown()
p.begin_fill()
p.circle(1000,5)
p.circle(30,195)
p.circle(1000,5)
p.end_fill()
#画鼻子
p.penup()
p.goto(-350,100)
p.left(140)
p.pendown()
p.circle(400,5)
p.circle(200,63)

p.fillcolor("palevioletred")
p.penup()
p.goto(-350,240)
p.pendown()
p.begin_fill()
p.circle(17,360)
p.end_fill()

p.penup()
p.goto(-285,235)
p.pendown()
p.begin_fill()
p.circle(17,360)
p.end_fill()

done()
```

结果如下：<br>
![Image Title](./page.jpg)<br>
还不错hhh<br>
