---
title: 汉诺塔的递归与非递归实现
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
汉诺塔（Tower of Hanoi）是根据一个传说形成的数学问题：

有三根杆子A，B，C。 A杆上有 N 个 (N>1) 穿孔圆盘，盘的尺寸由下到上依次变小。要求按下列规则将所有圆盘移至 C 杆：

每次只能移动一个圆盘；
大盘不能叠在小盘上面。
提示：可将圆盘临时置于 B 杆，也可将从 A 杆移出的圆盘重新移回 A 杆，但都必须遵循上述两条规则。

问：如何移？最少要移动多少次？
<!--more-->
递归版本：
```C++
#include <iostream>
#include <time.h>
int count = 0;
using namespace std;
void hanio(int n, char a, char c, char b)
{
    if(n == 1)
    {
        cout<<a<<" -> "<<b<<endl;
        count++;
    }
    else
    {
        hanio(n - 1, a, b, c);
        cout<<a<<" -> "<<b<<endl;
        count++;
        hanio(n - 1, c, a, b);
    }
}

int main()
{
     int n;
    cin>>n;
    clock_t time_start = clock();
    hanio(n, 'a', 'b', 'c');
    clock_t time_end = clock();
    cout<<"The program takes "<<(time_end - time_start)/1.0/1000<<" milliseconds"<<endl;
    return 0;
}
```
非递归版本：
```C
#include <iostream>
#include <memory.h>
#include <math.h>
#include <time.h>

using namespace std;

int max_k(int i)
{
    if(i==0)
        return 0;
    int k = 0;
    while(i%2==0)
    {
        i/=2;
        k++;
    }
    return k;
}

int main()
{
    int n, k;
    cin>>n;
    clock_t time_start = clock();
    char* a = new char[n];
    memset(a, 'a', n);
    if(n%2==0)
    {
        for(int i=1;i<=pow(2,n)-1;i++)
        {
            k = max_k(i);
            if((k+1)%2)
            {
                char now = a[k];//k+1号盘子现在在哪根柱子上
                char next = (a[k]=='c')?'a':(a[k]+1);//k+1号盘子要移动到哪根柱子上
                cout<<now<<" -> "<<next<<endl;
                a[k] = next;
            }
            else
            {
                char now = a[k];//k+1号盘子现在在哪根柱子上
                char next = (a[k]=='a')?'c':(a[k]-1);//k+1号盘子要移动到哪根柱子上
                cout<<now<<" -> "<<next<<endl;
                a[k] = next;
            }
        }
    }
    else
    {
        for(int i=1;i<=pow(2,n)-1;i++)
        {
            k = max_k(i);
            if((k+1)%2)
            {
                char now = a[k];//k+1号盘子现在在哪根柱子上
                char next = (a[k]=='a')?'c':(a[k]-1);//k+1号盘子要移动到哪根柱子上
                cout<<now<<" -> "<<next<<endl;
                a[k] = next;
            }
            else
            {
                char now = a[k];//k+1号盘子现在在哪根柱子上
                char next = (a[k]=='c')?'a':(a[k]+1);//k+1号盘子要移动到哪根柱子上
                cout<<now<<" -> "<<next<<endl;
                a[k] = next;
            }
        }
    }
    clock_t time_end = clock();
    cout<<"The program takes "<<(time_end - time_start)/1.0/1000<<" seconds"<<endl;
    return 0;
}
```
最后还输出计算时间，n较小时两者差不多，n大了之后明显非递归更快
