from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
from . import util
from django import forms
import random


class SearchItem(forms.Form):
    entry = forms.CharField(label="", widget=forms.TextInput
                            (attrs={'placeholder': 'Search Encyclopedia'}))


class AddItem(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput
                            (attrs={'placeholder': 'Enter Page Title'}))

    Area = forms.CharField(label="Page Content", widget=forms.Textarea)


class EditItem(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput)
    Area = forms.CharField(label="Page Content", widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchItem()
    })

# Takes Title In URL


def entry(request, title):
    entries = util.list_entries()
    # Checking if Title exists in the list of entries
    if title.lower() not in [entry.lower() for entry in entries]:
        return render(request, "encyclopedia/error.html", {
            "form": SearchItem()
        })
    # If Title Exists Then:
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(util.get_entry(title)),
            "form": SearchItem(),
            "title": title
        })


# Handling Query Searchs; Full & Partial Both
def search(request):
    if request.method == "POST":
        entries = util.list_entries()
        searchForm = SearchItem(request.POST)
        if searchForm.is_valid():
            search = searchForm.cleaned_data['entry']
            # Full Entry Search
            if search.lower() in [i.lower() for i in entries]:
                return render(request, "encyclopedia/entry.html", {
                    "entry": markdown2.markdown(util.get_entry(search)),
                    "form": SearchItem()
                })
                # Partial Entry Search Outcome
            else:
                # Creates a list of Entries; containing partial sub string query
                querylist = [i for i in entries if search.lower() in i.lower()]
                return render(request, "encyclopedia/search.html", {
                    "searchs": querylist,
                    "form": SearchItem()
                })

# Page Addition && Redirect


def add(request):
    addentries = util.list_entries()
    if request.method == "POST":
        newEntry = AddItem(request.POST)
        if newEntry.is_valid():
            title = newEntry.cleaned_data["title"]
            # IF a Page exists with same Title; Throw an Error
            if title.lower() in [x.lower() for x in addentries]:
                return render(request, "encyclopedia/adderror.html", {
                    "form": SearchItem()
                })
                # Page doesnt exist with same TITLE ; Create One
            else:
                content = newEntry.cleaned_data["Area"]
                util.save_entry(title, content)
                # Redirect && Entry Function Handles the rest
                return redirect(f"http://127.0.0.1:8000/wiki/{title}")
        # Invalid Form Entry // IF Input doesnt pass Back END Verification Then:
        else:
            return render(request, "encyclopedia/add.html", {
                "form": SearchItem(),
                "form1": AddItem()
            })

    # Default
    return render(request, "encyclopedia/add.html", {
        "form": SearchItem(),
        "form1": AddItem()
    })


def edit(request):

    # Obtain entry title from ENTRY PAGE as POST
    title = request.POST.get("title")
    # Search specific entry, using Post Data
    entry = util.get_entry(title)
    #  Populate the Form Input
    edit_form = EditItem(initial={'Area': entry, 'title': title})

    # Handling Save Edit Event
    if request.method == "POST":
        # Save New Changes in FORM
        content_form = EditItem(request.POST)
        if content_form.is_valid():
            # Pull out changed input
            content_change = content_form.cleaned_data['Area']
            title_change = content_form.cleaned_data['title']
            # Send changed Input to util funtion
            util.save_entry(title_change, content_change)
            # Redirect to intended entry pafe with changes
            return redirect(f'http://127.0.0.1:8000/wiki/{title_change}')

    # Default Page +  Display Populated form
    return render(request, "encyclopedia/edit.html", {
        "form": SearchItem(),
        "form1": edit_form
    })


def rando(request):
    entries = util.list_entries()
    selected_page = random.choice(entries)
    return redirect(f'wiki/{selected_page}')
