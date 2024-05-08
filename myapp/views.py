from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Users, Blocks, Address

from .forms.signup import UserSignupForm
from .forms.address import AddressForm

from django.db import connection
    
def home(request):
    if request.session.get('is_logged_in', False):
        user_id = request.session.get('user_id')
        # Fetch the logged-in user's details
        user_details = Users.objects.get(user_id=user_id)
        # Fetch the 3 latest users who have joined
        latest_users = Users.objects.order_by('-created_at')[:3]
        return render(request, 'home.html', {'user': user_details, 'latest_users': latest_users})
    else:
        return redirect('login') 

@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Attempt to retrieve the user from the Users model
        try:
            user = Users.objects.get(user_name=username)
            
            # Checking if the provided password matches the stored hashed password
            if check_password(password, user.password):  # Assuming passwords are now hashed
                # Setting up the session
                request.session['user_id'] = user.user_id
                request.session['is_logged_in'] = True
                return redirect('home')  # Redirect to a home page or similar
            else:
                return HttpResponse('Login failed. Incorrect password.')
        except Users.DoesNotExist:
            return HttpResponse('Login failed. User does not exist.')
    else:
        # Show the login form
        return render(request, 'login.html')

def user_logout(request):
    try:
        # Clearing the session
        del request.session['user_id']
        del request.session['is_logged_in']
    except KeyError:
        pass
    return redirect('login')  # Redirect back to the login page or home page

def signup(request):
    if request.method == 'POST':
        user_form = UserSignupForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            # First, save the Address to ensure we have an address_id to store in the User model
            address = address_form.save()

            # Now save the User, with the address relationship established
            user = user_form.save(commit=False)
            user.addr_id = address  # Set the foreign key reference
            user.save()

            # Optionally, redirect to a new page upon successful registration
            return redirect('login')  # Redirect to login page or wherever you see fit
        else:
            # If the forms are not valid, re-render the page with the form errors
            return render(request, 'signup.html', {
                'user_form': user_form,
                'address_form': address_form
            })

    else:
        # If it's a GET request, just render the forms
        user_form = UserSignupForm()
        address_form = AddressForm()
        return render(request, 'signup.html', {
            'user_form': user_form,
            'address_form': address_form
        })

    

def profile(request):
    # Check if the user is logged in
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        try:
            user = Users.objects.get(user_id=user_id)
            if request.method == 'POST':
                # Retrieve updated profile information from the form
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                email = request.POST.get('email')
                phone_number = request.POST.get('phone_number')
                number_of_family_members = request.POST.get('number_of_family_members')
                intro = request.POST.get('intro')
                # Retrieve other updated profile attributes similarly
                
                # Update the user's profile in the database using SQL queries
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET first_name = %s, last_name = %s, email = %s, phone_number = %s, number_of_family_members = %s, intro = %s WHERE user_id = %s",
                        [first_name, last_name, email, phone_number, number_of_family_members, intro, user_id]
                    )
                    # Execute similar UPDATE queries for other profile attributes
                
                # Redirect to the profile page after updating
                return redirect('profile')

            context = {
                'user': user,
                'address': user.addr_id  # Directly access the address from the user
            }
            return render(request, 'profile.html', context)
        except Users.DoesNotExist:
            return HttpResponse('User does not exist.', status=404)
    else:
        return redirect('login')
    
def blocks(request):
    blocks = Blocks.objects.all()
    return render(request, 'blocks.html', {'blocks': blocks})

def find_block(block_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM blocks WHERE block_name = %s", [block_name])
        result = cursor.fetchall()
        return result
    
def search_blocks(request):
    blocks = []  # This will hold the search results
    if 'search_term' in request.GET:
        search_term = request.GET['search_term']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM blocks WHERE block_name ILIKE %s", [f"%{search_term}%"])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            blocks = [
                dict(zip(columns, row))
                for row in rows
            ]

    # Render the same template whether or not there was a search
    return render(request, 'blocks.html', {'blocks': blocks})

from django.shortcuts import render
from django.http import HttpResponse
from .models import Message, Thread

def send_message(request):
    if request.method == 'POST':
        user_id = request.user.id  # Assuming you have a user authentication system
        title = request.POST.get('title')
        recipient = request.POST.get('recipient')
        text_body = request.POST.get('text_body')
        
        # Assuming you have a method to determine thread_id based on recipient
        thread_id = 2  

        # Create a new thread if it doesn't exist
        if not Thread.objects.filter(id=thread_id).exists():
            thread_name = f"Thread for {recipient}"
            Thread.objects.create(id=thread_id, thread_name=thread_name, first_sender_id=user_id)

        # Create the message
        message = Message(user_id=user_id, thread_id=thread_id, title=title, recipient=recipient, text_body=text_body)
        message.save()

        return HttpResponse("Message sent successfully")

    return render(request, 'send_message.html')

def get_messages(request, user_id):
    message_feeds = {}

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.thread_id, t.thread_name, COUNT(m.message_id) as unread_messages
            FROM Message m
            INNER JOIN Thread t ON m.thread_id = t.thread_id
            WHERE m.user_id = %s
            GROUP BY m.thread_id, t.thread_name
        """, [user_id])
        rows = cursor.fetchall()
        for row in rows:
            thread_id = row[0]
            thread_name = row[1]
            unread_messages = row[2]
            message_feeds[thread_id] = {'thread_name': thread_name, 'unread_messages': unread_messages}

    return render(request, 'message_feeds.html', {'message_feeds': message_feeds})

def view_thread(request, thread_id):
    messages = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.*, u.username
            FROM Message m
            INNER JOIN Users u ON m.user_id = u.user_id
            WHERE m.thread_id = %s
            ORDER BY m.timestamp
        """, [thread_id])
        rows = cursor.fetchall()
        for row in rows:
            message = {
                'message_id': row[0],
                'user_id': row[1],
                'thread_id': row[2],
                'reply_to_message_id': row[3],
                'title': row[4],
                'timestamp': row[5],
                'recipient': row[6],
                'friend_id': row[7],
                'block_id': row[8],
                'hood_id': row[9],
                'text_body': row[10],
                'addr_id': row[11],
                'username': row[12]
            }
            messages.append(message)

    return render(request, 'view_thread.html', {'messages': messages})


def search_messages(request):
    messages = []  # This will hold the search results
    if 'search_term' in request.GET:
        search_term = request.GET['search_term']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Message WHERE text_body ILIKE %s", [f"%{search_term}%"])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            messages = [
                dict(zip(columns, row))
                for row in rows
            ]

    # Render the same template whether or not there was a search
    return render(request, 'messages.html', {'messages': messages})

from .models import Applications, Membership

def membership_requests(request):
    if request.method == 'GET':
        # Fetch all pending membership applications
        membership_requests = Applications.objects.filter(application_status='pending')
        return render(request, 'membership_requests.html', {'membership_requests': membership_requests})

def approve_membership(request, application_id):
    if request.method == 'POST':
        # Approve the membership application
        application = Applications.objects.get(application_id=application_id)
        application.application_status = 'approved'
        application.save()

        # Create a membership record for the approved user and block
        Membership.objects.create(user_id=application.applicant_id, block_id=application.block_id, status='approved', permissions='read')

        return HttpResponse("Membership approved successfully")

def reject_membership(request, application_id):
    if request.method == 'POST':
        # Reject the membership application
        application = Applications.objects.get(application_id=application_id)
        application.application_status = 'rejected'
        application.save()

        return HttpResponse("Membership rejected successfully")
    


