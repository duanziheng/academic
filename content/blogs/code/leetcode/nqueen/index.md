---
title: 八皇后问题
date: "2018-05-27"
draft: false
active: true
layout: post
categories: code
tags: leetcode

# View.
#   1 = List
#   2 = Compact
#   3 = Card
view: 2
---
八皇后问题，是一个古老而著名的问题，是回溯算法的典型案例。
该问题是国际西洋棋棋手马克斯·贝瑟尔于1848年提出：在8×8格的国际象棋上摆放八个皇后，使其不能互相攻击，即任意两个皇后都不能处于同一行、同一列或同一斜线上，问有多少种摆法。
高斯认为有76种方案。
1854年在柏林的象棋杂志上不同的作者发表了40种不同的解。
后来有人用图论的方法解出92种结果。
现在给出n皇后问题的代码
<!--more-->
```C++
#include<iostream>

using namespace std;

int total = 0;
int n;
int* n_queens;

void print()
{
    for(int i=0;i<n;i++)
    {
        for(int j=0;j<n_queens[i];j++)
        {
            cout<<"0";
        }
        cout<<"1";
        for(int j=n_queens[i]+1;j<n;j++)
        {
            cout<<"0";
        }
        cout<<endl;
    }
    cout<<"****************************"<<endl;
}

bool check(int queen_i, int pos_i)//第queen_i个皇后，在第pos_i列
{
    int i, pos;
    for(i=0;i<queen_i;i++)//只需要查看前面的皇后
    {
        pos = n_queens[i];//在同一列
        if(pos_i==pos)
            return false;
        if((queen_i+pos_i)==(i+pos))//在右下角
            return false;
        if((queen_i-pos_i)==(i-pos))//在左下角
            return false;
    }
    return true;
}

void my_queens(int i)//第i个皇后
{
    for(int pos=0;pos<n;pos++)//在第pos列
    {
        if(check(i,pos))
        {
            n_queens[i] = pos;
            if(i == n-1)
            {
                total++; 
                print();
                n_queens[i] = 0;
                return;
            }
            my_queens(i+1);//找下一个皇后的位置
            n_queens[i] = 0;//回溯，这个皇后继续寻找新位置
        }
    }
}

int main()
{
    cout<<"Please enter the number of queens."<<endl;
    cin>>n;
    n_queens = new int[n];
    my_queens(0);
    if(total==0)
        cout<<"There is no way."<<endl;
    else if(total==1)
        cout<<"There is only one way."<<endl;
    else
        cout<<"There are "<<total<<" ways."<<endl;
    return 0;
}
```
运行后可以发现当n为1或大于3的时候才有解。