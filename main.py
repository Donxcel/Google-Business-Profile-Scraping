class School:
    def __init__(self,name,courses,classes):
        self.name = name
        self.courses = courses
        self.classes = classes

    def competition(self,other):
        print('Class',self.classes,"against class",other.classes)

class Second:
    def __init__(self) :
        super(School)
    
get_name = input("Enter the school name")
get_courses = input("Enter the school course ")
get_classes = input("Enter the number of classes")
other_school = ''
my_school = School(get_name,get_courses,get_classes)
if input("is there any other school") == 'yes':
    get_name = input("Enter the school name")
    get_courses = input("Enter the school course ")
    get_classes = input("Enter the number of classes")
    other_school = Second(get_name,get_courses,get_classes)
if len(other_school.name) != 0:
    my_school.competition(other=other_school)