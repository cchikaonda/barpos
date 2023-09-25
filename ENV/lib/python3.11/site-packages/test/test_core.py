# -*- coding utf-8 -*-#
# ------------------------------------------------------------------
# Name:      test_core
# Author:    liangbaikai
# Date:      2020/1/30
# Desc:      there is a test for jsonfy
# ------------------------------------------------------------------
from cn.jsonfy.core import BaseJsonModel, FloatDesc, IntDesc, ObjectDesc, StrDesc


class Student(BaseJsonModel):
    score = FloatDesc("score")
    age = IntDesc("age")


class Person(BaseJsonModel):
    name = StrDesc("name")
    age = IntDesc("age", hide=False)
    weight = IntDesc("weight")
    student = ObjectDesc("student", Student)


def test1():
    s = Student(score=1.2, age=122)
    print(s.toJson())
    ff = s.fromJson(s.toJson())
    print(ff)
    print(ff.__dict__)


def test2():
    s = Student(score=1.2, age=22)
    person = Person(name='李四', age=22, student=s)
    print(person)
    print(person.toJson())
    print(person.fromJson(person.toJson()))


if __name__ == '__main__':
    test1()
    test2()
