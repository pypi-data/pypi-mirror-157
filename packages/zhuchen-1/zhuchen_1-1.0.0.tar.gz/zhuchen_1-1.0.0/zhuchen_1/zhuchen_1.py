# -*- coding: utf-8 -*-
# @File : zhuchen_1.py
# @Author : 朱臣
# @iphone : 15850225717 
# @time : 2022/6/30 12:47

import itertools

case_list = ["用户名", "密码"]
value_list = ["正确","不正确","特殊符号","超过最大长度"]

def gen_case(item = case_list,value = value_list):
    """ 输出笛卡尔用例集合"""
    for i in itertools.product(item,value):
        print("输入".join(i))

if __name__ == "__main__":
    gen_case()