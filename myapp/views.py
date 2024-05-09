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
        # Assuming you have a method to get user details by user_id
        user_details = Users.objects.get(user_id=user_id)
        return render(request, 'home.html', {'user': user_details})
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
            print(user.addr_id.addr_id)
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
    # return render(request, 'blocks.html', {'blocks': blocks})
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        try:
            user = Users.objects.get(user_id=user_id)
            print(user.addr_id.addr_id)
            context = {
                'user': user,
                'blocks': blocks 
            }
            return render(request, 'blocks.html', context)
        except Users.DoesNotExist:
            return HttpResponse('User does not exist.', status=404)
    else:
        return redirect('login')

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

def insert_application(request):
    if request.method == 'POST' and 'user_name' in request.POST and 'block_name' in request.POST:
        print(request.POST)
        user_name = request.POST['user_name']
        block_name = request.POST['block_name']

        application_status = 'pending'  # Since the status is default set to 'pending'

        with connection.cursor() as cursor:
            try:
                # Insert only if not already applied
                cursor.execute("""
                    INSERT INTO applications (block_id, applicant_id, application_status)
                    SELECT (SELECT block_id FROM Blocks WHERE block_name = %s),
                           (SELECT user_id FROM Users WHERE user_name = %s),
                           %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM applications WHERE block_id = (SELECT block_id FROM Blocks WHERE block_name = %s) AND applicant_id = (SELECT user_id FROM Users WHERE user_name = %s)
                    );
                """, [block_name, user_name, application_status, block_name, user_name])
                if cursor.rowcount > 0:
                    print('Application inserted successfully.')
                else:
                    print('You have already applied to this block.')
            except Exception as e:
                print('Error inserting application: {str(e)}')

    return render(request, 'success.html')

def view_applications(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
    applications = []
    print(user_id)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.application_status, b.block_name
            FROM applications a
            JOIN blocks b ON a.block_id = b.block_id
            WHERE a.applicant_id = %s
        """, [user_id])
        applications = cursor.fetchall()
    context = {
        'applications': applications
    }
    print(applications)
    return render(request, 'view_applications.html', {'applications': applications})



