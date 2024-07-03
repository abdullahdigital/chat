from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Room, Message
from django.contrib.messages import constants as message_constants
from django.db import IntegrityError
from .models import CustomUser  # Assuming CustomUser is in the same app
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from datetime import datetime
import json
from .models import Profile

def home(request):
    return render(request, 'home.html')

def room(request, room, username):
    room_details = get_object_or_404(Room, name=room)
    messages = Message.objects.filter(room=room_details)
    return render(request, 'room.html', {
        'username': username,
        'room': room,
        'room_details': room_details,
        'messages': messages
    })
@login_required
def checkview(request):
    if request.method == 'POST':
        room_name = request.POST['room_name'].strip()
        username = request.POST['username'].strip()
        if room_name:
            room, created = Room.objects.get_or_create(name=room_name)
            return redirect(f'/room/{room_name}/{username}')
        else:
            return render(request, 'home.html', {'error': 'Room name cannot be empty.'})
        
def create_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name', '').strip()
        if room_name:
            room, created = Room.objects.get_or_create(name=room_name)
            if created:
                return JsonResponse({'success': True, 'room_id': room.id})
            else:
                return JsonResponse({'success': False, 'error': 'Room already exists.'})
        else:
            return JsonResponse({'success': False, 'error': 'Room name cannot be empty.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def send(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data['message']
        username = data['username']
        room_id = data['room_id']

        new_message = Message.objects.create(value=message, user=username, room=room_id)
        new_message.save()
        return JsonResponse({'success': True, 'message': new_message.value})
    else:
        return HttpResponse("Method not allowed", status=405)

def getMessages(request, room):
    room_details = Room.objects.get(name=room)
    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages": list(messages.values())})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in')
            return redirect('/')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('/login/')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('/')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Validate inputs
        if len(username) < 5:
            messages.error(request, "Username must be at least 5 characters long.")
            return redirect('register')
        if not username.isalnum():
            messages.error(request, "Username should only contain alphanumeric characters.")
            return redirect('register')
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
        except IntegrityError:
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect('register')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('register')
    else:
        return render(request, 'register.html')



@login_required
def profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        marital_status = request.POST.get('marital_status')
        country = request.POST.get('country')
        city = request.POST.get('city')
        dob_str = request.POST.get('dob')  # Get dob as a string from POST data

        # Validate and parse dob
        dob = None
        if dob_str:
            try:
                parsed_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
                dob = parsed_date
            except ValueError:
                raise ValidationError('Invalid date format. Must be in YYYY-MM-DD format.')

        number = request.POST.get('number')
        profile_pic = request.FILES.get('profile_pic')

        profile.bio = bio
        profile.marital_status = marital_status
        profile.country = country
        profile.city = city
        profile.dob = dob  # Assign parsed date to dob field
        profile.number = number
        if profile_pic:
            profile.profile_pic = profile_pic
        profile.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile')

    context = {
        'user': user,
        'profile': profile,
        'profile_message': next((message for message in messages.get_messages(request) if 'profile_message' in message.tags), None)
    }
    return render(request, 'profile.html', context)