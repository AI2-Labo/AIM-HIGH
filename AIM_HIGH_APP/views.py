from django.shortcuts import render, redirect

from .models import My_Profile_Model
from .forms import My_Profile_Form

def index(request):
    form = My_Profile_Form()
    My_Profile_Attributes = My_Profile_Model.objects.all()

    if request.method == "POST":
        form = My_Profile_Form(request.POST)

        if form.is_valid():
            form.save()

        return redirect("/") # Change to whatever is next

    context = {"My_Profile_Attributes": My_Profile_Attributes, "My_Profile_Form": form}
    return render(request, "my_profile.html", context)