
from secrets import choice
#StablishPoints
def StablishPoints(variable):
    #Find RangeA and its interval type
    if variable.find("[") != -1:
        DivR1 = variable.find("[")
        LimR1 = "Closed"
        Comma = variable.find(",")
        Range1 = variable[DivR1 + 1: Comma]
    elif variable.find("(") != -1:
        DivR1 = variable.find("(")
        LimR1 = "Open"
        Comma = variable.find(",")
        Range1 = variable[DivR1 + 1: Comma]
    else:
        print("Error, cannot find the first type of interval")
    #Find RangeB and its interval type
    if variable.find("]") != -1:
        DivR2 = variable.find("]")
        LimR2 = "Closed"
        Comma = variable.find(",")
        Range2 = variable[Comma + 1: DivR2]
    elif variable.find(")") != -1:
        DivR2 = variable.find(")")
        LimR2 = "Open"
        Comma = variable.find(",")
        Range2 = variable[Comma + 1: DivR2]
    else:
        print("Error, cannot find the second type of interval")
    return Range1, Range2, LimR1, LimR2

#Equals
class Equals:
    def __init__(self, A_DataRange, B_DataRange):
        A_Range1, A_Range2, A_LimR1, A_LimR2 = StablishPoints(A_DataRange)
        B_Range1, B_Range2, B_LimR1, B_LimR2 = StablishPoints(B_DataRange)
        if A_Range1 == B_Range1 and A_Range2 == B_Range2 and A_LimR1 == B_LimR1 and A_LimR2 == B_LimR2:
            print(A_DataRange + " equals " + B_DataRange)
        else:
            print(A_DataRange + " neq " + B_DataRange)

#getAllPoints
class getAllPoints:
    def __init__(self, A_DataRange):
        A_Range1, A_Range2, A_LimR1, A_LimR2 = StablishPoints(A_DataRange)
        result = []
        if A_LimR1 == "Closed":
            if A_LimR2 == "Closed":
                for x in range(int(A_Range1), int(A_Range2) + 1): 
                    result += [x]
            elif A_LimR2 == "Open":
                for x in range(int(A_Range1), int(A_Range2)):
                    result += [x]
            else:
                print("Error, cannot find the second type of interval")
        elif A_LimR1 =="Open":
            if A_LimR2 == "Closed":
                for x in range(int(A_Range1) + 1, int(A_Range2) + 1):
                    result += [x]
            elif A_LimR2 == "Open":
                for x in range(int(A_Range1) + 1, int(A_Range2)):
                    result += [x]    
            else:
                print("Error, cannot find the second type of interval")        
        else:
            print("Error, cannot find the first type of interval")
        print(result)

#endPoints
class endPoints:
        def __init__(self, A_DataRange):
            A_Range1, A_Range2, A_LimR1, A_LimR2 = StablishPoints(A_DataRange)
            if A_LimR1 == "Closed":
                if A_LimR2 == "Closed":
                    print(int(A_Range1), int(A_Range2))
                elif A_LimR2 == "Open":
                    print(int(A_Range1), int(A_Range2) - 1)
            elif A_LimR1 =="Open":
                if A_LimR2 == "Closed":
                    print(int(A_Range1) + 1, int(A_Range2))
                elif A_LimR2 == "Open":
                    print(int(A_Range1) + 1, int(A_Range2) - 1)


