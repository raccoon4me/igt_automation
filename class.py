import math


class Point3D(object):
    #init
    def __init__(self, x, y, z):
        self.a, self.b, self.c = x, y,z
    def __repr__(self):
        return "(%s,%s,%s)" % (self.a, self.b, self.c)



my_point = Point3D(3,4,5)
print my_point


'''
class Car(object):
    condition = "new"
    def __init__(self, model, color, mpg):
        self.model = model
        self.color = color
        self.mpg = mpg

    def display_car(self):
        print "This is a %s %s with %s MPG." % (self.model,self.color,str(self.mpg))

    def drive_car(self):
        self.condition = "used"


class ElectricCar(Car):
    def __init__(self, model, color, mpg, battery_type):
        self.model = model
        self.color = color
        self.mpg = mpg
        self.battery_type = battery_type

    def drive_car(self):
        self.condition = "like new"



my_car = ElectricCar("DeLorean", "silver", 88,"molten salt")
print my_car.condition
my_car.drive_car()
print my_car.condition






class Triangle(object):
    #let's set a member variable that will be accessible from all methods
    number_of_slide = 3
    #we always initialize our class
    def __init__(self, angle1, angle2, angle3):
        self.angle1 = angle1
        self.angle2 = angle2
        self.angle3 = angle3


    def check_angles(self):
        data = {}
        data = self.angle1, self.angle2, self.angle3
        print data
        if math.fsum(data) == 180:
            return True
        else:
            return False

class Equilateral(Triangle):
    angle = 60
    def __init__(self):
        self.angle1 = Equilateral.angle
        self.angle2 = Equilateral.angle
        self.angle3 = Equilateral.angle
        print Triangle.number_of_slide

one_triangle = Triangle(80,80,20)
print one_triangle.check_angles()

one_equilateral = Equilateral()
print one_equilateral.check_angles()


exo p14
class Employee(object):
    """Models real-life employees!"""
    def __init__(self, employee_name):
        self.employee_name = employee_name
    def calculate_wage(self, hours):
        self.hours = hours
        return hours * 20.00

class PartTimeEmployee(Employee):
    def calculate_wage(self, hours):
        self.hours = hours
        return hours * 12
    
    def full_time_wage(self, hours):
        print "his name is %s" % self.employee_name
        #this return the result of the overwriting of the method calculate_wage of the base class employee
        r = super(PartTimeEmployee,self).calculate_wage(hours)
        return r

milton = PartTimeEmployee("jason")
print milton.full_time_wage(1)
'''
