from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Meep
from .forms import MeepForm, ProfilePicform, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm
from django.contrib.auth.models import User
def home(request):
    if request.user.is_authenticated:
        form  = MeepForm(request.POST or None)
        
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, ("Your tweet has been posted"))
                return redirect('home')
            
        
        meeps = Meep.objects.all().order_by('-created_at')
        
        return render(request, 'home.html', {"meeps":meeps, "form":form})
    else:
        meeps = Meep.objects.all()
        return render(request, 'home.html', {"meeps":meeps})
def post_comment(request, meep_id):
    meep = get_object_or_404(Meep, id=meep_id)
    if request.user.is_authenticated and request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.meep = meep
            comment.user = request.user
            comment.save()
            messages.success(request, "Your comment has been posted")
        else:
            messages.error(request, "There was an error with your comment. Please try again.")
        
        
    else:
        messages.error(request, "You must be logged in to post a comment")
        
    return redirect('home')
        
            
            
                
def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {'profiles':profiles})
    else:
        messages.success(request, ("You must be logged in first..."))
        return redirect('home')
    
def follow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id= pk)
        request.user.profile.follows.add(profile)
        request.user.profile.save()
        return redirect(request.META.get("HTTP_REFERER"))        
    else:
        messages.success(request,("You must be logged in to see this page.."))
        return redirect('home')
    
def unfollow(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id= pk)
        request.user.profile.follows.remove(profile)
        request.user.profile.save()
        
        return redirect(request.META.get("HTTP_REFERER"))        
    else:
        messages.success(request,("You must be logged in to see this page.."))
        return redirect('home')
    
def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id =pk)
        
        if request.method == "POST":
            current_user_profile = request.user.profile

            action = request.POST['follow']
            
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
                
            current_user_profile.save()
        
        
        
        return render(request, 'profile.html', {'profile':profile, 'meeps':meeps})
    else:
        messages.success(request, ("You must be logged in first..."))
        return redirect('home')
def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk :
            profiles = Profile.objects.get(user=request.user)
            return render(request, 'followers.html', {'profiles':profiles})
        else:
            messages.success(request, ("That was not your profile..."))
            return redirect('home')
            
    else:
        messages.success(request, ("You must be logged in first..."))
        return redirect('home')
    
    
def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk :
            profiles = Profile.objects.get(user=request.user)
            return render(request, 'follows.html', {'profiles':profiles})
        else:
            messages.success(request, ("That was not your profile..."))
            return redirect('home')
            
    else:
        messages.success(request, ("You must be logged in first..."))
        return redirect('home')
    
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You have been logged in! "))
            return redirect('home')
        else:
            messages.success(request, ("There was an error "))
            return redirect('login')
    else:
        return render(request, 'login.html', {})
            
            
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged out "))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']
            
            user = authenticate(username=username, password=password)
            login(request,user)
            messages.success(request, ("You have successfully registered "))
            return redirect('home')
    return render(request, 'register.html', {'form':form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = get_object_or_404(User, id=request.user.id)
        profile_user = get_object_or_404(Profile, user=current_user)
        
        # Get Forms
        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicform(request.POST or None, request.FILES or None, instance=profile_user)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            login(request, current_user)
            messages.success(request, "Your Profile Has Been Updated!")
            return redirect('home')
        
        return render(request, "update_user.html", {'user_form': user_form, 'profile_form': profile_form})
    else:
        messages.error(request, "You must be logged in to view that page...")
        return redirect('home')
    
    
def meep_like(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
            
        return redirect(request.META.get("HTTP_REFERER")) 
            
    else:
        messages.success(request, ("You must be logged in to see this page"))
        return redirect('home')

    
def meep_show(request, pk):
    tweet = get_object_or_404(Meep, id=pk)
    if tweet:
        comment_form = CommentForm()
        return render(request, 'show_meep.html', {'tweet':tweet, "comment_form":comment_form})

    else:
        messages.success(request, ("That tweet does not exist"))
        return redirect('home')
    
    
def delete_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if request.user.username == meep.user.username:
            meep.delete()
            return redirect(request.META.get("HTTP_REFERER")) 
        else:
            messages.success(request, ("You must be logged in to continue..."))
            return redirect('home') 
    else:
        messages.success(request, ("You must be logged in to continue..."))
        return redirect(request.META.get("HTTP_REFERER")) 
    
def edit_meep(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if request.user.username == meep.user.username:
            if request.method == 'POST':
                form = MeepForm(request.POST, instance=meep)
                if form.is_valid():
                    form.save()
                    messages.success(request, ("Tweet updated successfully!"))
                    return redirect('home')  # Redirect to home or any other appropriate view
            else:
                form = MeepForm(instance=meep)
            return render(request, "edit_meep.html", {'form': form, 'tweet': meep})
        else:
            messages.error(request, ("You don't own this tweet..."))
            return redirect('home') 
    else:
        messages.error(request, ("You must be logged in to continue..."))
        return redirect('home')
    
    
def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        
        searched = Meep.objects.filter(body__contains=search)
        
        return render(request, 'search.html', {'search':search, 'searched':searched})
    else:
        return render(request, 'search.html', {})
    
def search_user(request):
    if request.method == 'POST':
        search = request.POST['search']
        
        searched = User.objects.filter(username__contains=search)
        
        return render(request, 'search_user.html', {'search':search, 'searched':searched})
    else:
        return render(request, 'search_user.html', {})