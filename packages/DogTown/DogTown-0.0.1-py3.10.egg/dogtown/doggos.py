class Town:
    def __init__(self, name, houses, joinProperties, fullName):
        self.name = name
        self.houses = houses
        self.joinProperties = joinProperties
        self.fullName = fullName
        self.dogs = []
    
    def addDog(self, dog):
        if len(self.dogs) < self.houses:
            if self.fullName:
                if dog.name == self.joinProperties:
                    self.dogs.append(dog.name)
                    print(dog.name + " has been added to " + self.name)
                    return True

            elif self.fullName == False:
                if dog.name[0] == self.joinProperties:
                    self.dogs.append(dog.name)
                    print(dog.name + " has been added to " + self.name)
                    return True

            print(dog.name + " cannot be added to " + self.name)
            return False
    
    def removeDog(self, dog):
        if type(dog) == str:
            print(dog + " has been removed from " + self.name)
            self.dogs.remove(dog)
        
        if type(dog) == int:
            print(self.dogs[dog] + " has been removed from " + self.name)
            self.dogs.pop(dog)
    
    def show(self):
        print(self.dogs)


class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age