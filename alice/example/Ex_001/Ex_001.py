# -*- coding: utf-8 -*-
import aiml
import os
import codecs

mybot_path = "./mybot"
# 切换到语料库所在工作目录
os.chdir(mybot_path)
print(mybot_path)
mybot = aiml.Kernel()
mybot.learn("std-startup.xml")
mybot.respond("load aiml c")
while True:
  input1 = input("Enter your message >> ")
  res = mybot.respond(input1)
  print(res)
