from django.db import models

class My_Profile_Model(models.Model):

    name = models.CharField(max_length=50)
    age = models.IntegerField()
    learning_topic = models.CharField(max_length=50)
        # ^ What the user would like to learn/study

    education_options = [
        ("Elementary", "Elementary School"),
        ("Middle", "Middle School"),
        ("High", "High School"),
        ("Undergraduate", "Undergraduate"),
        ("Graduate", "Graduate"),
        ("PhD", "Doctorate"),
    ]
    education_level = models.CharField(max_length=100,
                                       choices=education_options,
                                       default="Elementary",
                                       )


    def __str__(self):
        return self.name

