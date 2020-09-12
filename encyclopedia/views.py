import markdown2
import secrets

from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from django import forms
from markdown2 import Markdown
from django.urls import reverse


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Enter Title",widget=forms.TextInput(attrs={'class' : 'form-control col-md-8 col-lg-8'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control col-md-8 col-lg-10', 'rows' : 10}))
    edit = forms.BooleanField(widget=forms.HiddenInput(),required=False,initial=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request,entry):
    markdowner=Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonExistingEntry.html",{
            "entryTitle":entry,
            "error_link":"/",
            "message1":"You can go back to the home page here ",
            "message2":"The Page you are looking for is not found"
        })
    else:
        return render(request,"encyclopedia/entry.html",
        {
            "entryTitle":entry,
            "entry":markdowner.convert(entryPage)
        })
    
def search(request):
    value=request.GET.get('q','')
    if util.get_entry(value) is not None:
        return HttpResponseRedirect(reverse("entry",kwargs={'entry':value}))
    else:
        subString=[]
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subString.append(entry)

        return render(request,"encyclopedia/index.html",{
            "entries":subString,
            "search":True,
            "value":value,
        })

def newEntry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': title}))
            else:
                return render(request, "encyclopedia/nonExistingEntry.html", {
                "form": form,
                "existing": True,
                "entry": title,
                "error_link": "/newEntry",
                "message1": "This entry already exists. If you want to view all entries,",
                "message2": "You must change the ENTRY NAME"
                })
        else:
            return render(request, "encyclopedia/newEntry.html", {
            "form": form,
            "existing": False
            })
    else:
        return render(request,"encyclopedia/newEntry.html", {
            "form": NewEntryForm(),
            "existing": False
        }) 

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry",kwargs={
        'entry':randomEntry
    }))

def edit(request,entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request,"encyclopedia/nonExistingEntry.html",{
            "entryTitle":entry
        })
    else:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["content"].initial = entryPage
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["edit"].initial = True
        return render(request,"encyclopedia/newEntry.html",{
            "form":form,
            "edit":form.fields["edit"].initial,
            "entryTitle": form.fields["title"].initial
        })