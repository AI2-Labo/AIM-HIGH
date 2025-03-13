class AI_Profile:
    def __init__(self, name, age, description, education):
        self.name = name
        self.age = age
        self.description = description
        self.education = education
    def information(self):
        return f"You are {self.name}, A {self.age} year old. {self.description}. Your education is {self.education}"
class My_Profile:
    def __init__(self, name, age, education):
        self.name = name
        self.age = age
        self.education = education
    def information(self):
        return f"The users name is {self.name}, they are {self.age} years old, and are at thiis level of education: {self.education}"


