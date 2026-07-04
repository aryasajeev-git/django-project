from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db import transaction
from myapp.models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import os

# Create your views here.


def signupfunction(request):
    return render(request,'signup.html')

def signupfunction_post(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone_no = request.POST.get('phone_no', '').strip()
    gender = request.POST.get('gender', '').strip()
    photo = request.FILES.get('photo')
    password = request.POST.get('password', '')

    # Basic validation
    if not (name and email and phone_no and gender and password):
        return HttpResponse('<script>alert("Please fill all required fields."); window.location="/myapp/signup/";</script>')

    if not phone_no.isdigit() or len(phone_no) < 7 or len(phone_no) > 15:
        return HttpResponse('<script>alert("Please enter a valid phone number with 7 to 15 digits."); window.location="/myapp/signup/";</script>')

    # Check if user already exists
    if User.objects.filter(username=email).exists():
        return HttpResponse('<script>alert("Email already registered. Please log in or use a different email."); window.location="/myapp/signup/";</script>')

    try:
        authuser = User.objects.create_user(username=email, password=password)
        authuser.groups.add(Group.objects.get(name='User'))
        authuser.save()
    except Exception:
        return HttpResponse('<script>alert("Error creating account. Please try again."); window.location="/myapp/signup/";</script>')

    si = Usersprofile()
    si.name = name
    si.email = email
    si.phone_no = int(phone_no)
    si.gender = gender
    # save uploaded photo file to MEDIA_ROOT and store filename
    if photo:
        si.photo = photo

    si.AUTHUSER = authuser
    si.save()

    return HttpResponse(
        '<script>alert("Signup successful! Please log in."); window.location="/myapp/login/";</script>'
    )
def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/myapp/login/')


def loginfunction(request):
    return render(request,'login.html')


def login_post(request):
    username = request.POST['email']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/myapp/viewprofile/')
    return HttpResponse('<script>alert("Invalid username or password."); window.location="/myapp/login/";</script>')


def viewprofile(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')

    try:
        profile = Usersprofile.objects.get(AUTHUSER=request.user)

        if profile.photo:
            photo_url = profile.photo.url
        else:
            photo_url = None

    except Usersprofile.DoesNotExist:
        profile = None
        photo_url = None

    return render(request, 'viewprofile.html', {
        'profile': profile,
        'photo_url': photo_url
    })


def editprofile(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')

    try:
        profile = Usersprofile.objects.get(AUTHUSER=request.user)

        if profile.photo:
            photo_url = profile.photo.url
        else:
            photo_url = None

        return render(request, 'editprofile.html', {
            'profile': profile,
            'photo_url': photo_url
        })

    except Usersprofile.DoesNotExist:
        return HttpResponse(
            '<script>alert("Profile not found. Please sign up."); window.location="/myapp/signup/";</script>'
        )


def editprofile_post(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')

    if request.method != 'POST':
        return redirect('/myapp/editprofile/')

    try:
        profile = Usersprofile.objects.get(AUTHUSER=request.user)

    except Usersprofile.DoesNotExist:
        return HttpResponse(
            '<script>alert("Profile not found."); window.location="/myapp/login/";</script>'
        )

    name = request.POST.get('name')
    phone_no = request.POST.get('phone_no')
    gender = request.POST.get('gender')
    photo = request.FILES.get('photo')

    if name is not None:
        profile.name = name

    if phone_no is not None:
        phone_no = phone_no.strip()

        if not phone_no.isdigit() or len(phone_no) < 7 or len(phone_no) > 15:
            return HttpResponse(
                '<script>alert("Please enter a valid phone number with 7 to 15 digits."); window.location="/myapp/editprofile/";</script>'
            )

        profile.phone_no = int(phone_no)

    if gender is not None:
        profile.gender = gender

    if photo:
        profile.photo = photo

    profile.save()

    return redirect('/myapp/viewprofile/')

def uploaddocument(request):
    return render(request, 'uploaddocument.html')
    

def uploaddocument_post(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    if not request.user.is_authenticated:
        return redirect('/myapp/login/')

    document_name = request.POST.get('document_name')
    document_type = request.POST.get('document_type')
    file = request.FILES.get('file')

    if not (document_name and document_type and file):
        return HttpResponse('Please provide document name, document type, and a file.', status=400)

    fs = FileSystemStorage()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{file.name}"
    saved_name = fs.save(filename, file)
    path = fs.url(saved_name)

    profile = Usersprofile.objects.get(AUTHUSER__id=request.user.id)
    doc = Document()
    doc.FileName = document_name
    doc.Type = document_type
    doc.File = path
    doc.User = profile
    doc.save()

    return HttpResponse('<script>alert("Document successfully uploaded!"); window.location="/myapp/viewprofile/";</script>')

def viewdocument(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    
    documents = []
    try:
        profile = Usersprofile.objects.get(AUTHUSER__id=request.user.id)
        # Only get documents for the current user
        for d in Document.objects.filter(User=profile):
            file_url = d.File or ''
            if file_url and not (file_url.startswith('http') or file_url.startswith('/') or file_url.startswith(settings.MEDIA_URL)):
                file_url = settings.MEDIA_URL + file_url
            documents.append({
                'id': d.id,
                'FileName': d.FileName,
                'Type': d.Type,
                'File': file_url,
            })
    except Usersprofile.DoesNotExist:
        documents = []
    
    return render(request, 'viewdocument.html', {'documents': documents})


def editdocument(request, id):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    
    try:
        document = Document.objects.get(id=id)
        # Verify the user owns this document
        if document.User.AUTHUSER != request.user:
            return HttpResponse('Unauthorized', status=403)
    except Document.DoesNotExist:
        return HttpResponse('Document not found', status=404)

    return render(request, 'editdocument.html', {'document': document})

def editdocument_post(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    document_id = request.POST.get('id')
    document_name = request.POST.get('document_name')
    document_type = request.POST.get('document_type')
    file = request.FILES.get('file')

    try:
        document = Document.objects.get(id=document_id)
        # Verify the user owns this document
        if document.User.AUTHUSER != request.user:
            return HttpResponse('Unauthorized', status=403)
    except Document.DoesNotExist:
        return HttpResponse('Document not found', status=404)

    if document_name:
        document.FileName = document_name
    if document_type:
        document.Type = document_type
    if file:
        fs = FileSystemStorage()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{file.name}"
        saved_name = fs.save(filename, file)
        path = fs.url(saved_name)
        document.File = path

    document.save()
    return redirect('/myapp/viewprofile/')

def deletedocument(request, id):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    
    try:
        document = Document.objects.get(id=id)
        # Verify the user owns this document
        if document.User.AUTHUSER != request.user:
            return HttpResponse('Unauthorized', status=403)
        document.delete()
    except Document.DoesNotExist:
        return HttpResponse('Document not found', status=404)

    return redirect('/myapp/viewdocument/')

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    return render(request,'changepassword.html')

def change_password_post(request):
    if not request.user.is_authenticated:
        return redirect('/myapp/login/')
    
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    if new_password != confirm_password:
        return HttpResponse('<script>alert("New password and confirm password do not match."); window.location="/myapp/change_password/";</script>')

    user = authenticate(request, username=request.user.username, password=current_password)
    if user is None:
        return HttpResponse('<script>alert("Current password is incorrect."); window.location="/myapp/change_password/";</script>')

    user.set_password(new_password)
    user.save()
    return HttpResponse('<script>alert("Password changed successfully! Please log in again."); window.location="/myapp/login/";</script>')

def forgot_password(request):
    return render(request, 'forgotpass.html')

def forgot_password_post(request):
    email = request.POST.get('email')

    if not email:
        return HttpResponse('<script>alert("Please enter your email."); window.location="/myapp/forgot_password/";</script>')

    try:
        user = User.objects.get(username=email)
        # Store email in session for the reset password page
        request.session['reset_email'] = email
    except User.DoesNotExist:
        return HttpResponse('<script>alert("Email not found. Please check and try again."); window.location="/myapp/forgot_password/";</script>')

    # Here you would typically send an email with a password reset link.
    # For simplicity, we will just display the password in an alert (not secure).
    return redirect('/myapp/reset_password/')

def reset_password(request):
    # Check if email is in session (user came from forgot password)
    if 'reset_email' not in request.session:
        return redirect('/myapp/forgot_password/')
    
    return render(request, 'reset_password.html')   

def reset_password_post(request):
    # Get email from session instead of POST
    email = request.session.get('reset_email')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')

    if not email:
        return HttpResponse('<script>alert("Invalid session. Please try again."); window.location="/myapp/forgot_password/";</script>')

    if new_password != confirm_password:
        return HttpResponse('<script>alert("New password and confirm password do not match."); window.location="/myapp/reset_password/";</script>')

    try:
        user = User.objects.get(username=email)
        user.set_password(new_password)
        user.save()
        # Clear the session email after successful reset
        if 'reset_email' in request.session:
            del request.session['reset_email']
        return HttpResponse('<script>alert("Password reset successful! Please log in with your new password."); window.location="/myapp/login/";</script>')
    except User.DoesNotExist:
        return HttpResponse('<script>alert("Email not found. Please check and try again."); window.location="/myapp/forgot_password/";</script>')