from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.utils import IntegrityError
from django.db import DatabaseError, transaction 
from .models import Users, Blocks, Address, Neighbors
from .forms.signup import UserSignupForm
from .forms.address import AddressForm
from django.db import connection
from .models import Applications, Membership
from django.shortcuts import render
from django.http import HttpResponse
from .models import Message, Thread
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.utils.dateparse import parse_datetime
from django.db import transaction 
from django.shortcuts import render
from django.http import HttpResponse
from .models import Users, Friendship
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.views.decorators.http import require_POST
    
def home(request):
    if request.session.get('is_logged_in', False):
        user_id = request.session.get('user_id')
        # Fetch the logged-in user's details
        user_details = Users.objects.get(user_id=user_id)
        # Fetch the 3 latest users who have joined
        latest_users = Users.objects.order_by('-created_at')[:3]

        with connection.cursor() as cursor:
            # Use the user_id directly from the session for the SQL query
            cursor.execute("""
                SELECT u.*
                FROM users u
                JOIN friendship f ON u.user_id = f.friend_id
                WHERE f.user_id = %s
            """, [user_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            friends = [
                dict(zip(columns, row))
                for row in rows
            ]
        return render(request, 'home.html', {'user': user_details, 'latest_users': latest_users, 'friends': friends})
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
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        if request.method == 'POST' and 'user_name' in request.POST and 'block_name' in request.POST:
            print(request.POST)
            user_name = request.POST['user_name']
            block_name = request.POST['block_name']

            application_status = 'pending'  # Since the status is default set to 'pending'
            membership_status = 'not approved'
            membership_permissions = 'read'

            with connection.cursor() as cursor:
                try:
                    # Transaction block starts here
                    with transaction.atomic():  # Use the transaction.atomic() to manage your transaction
                        # Insert application if not already applied
                        cursor.execute("""
                            INSERT INTO applications (block_id, applicant_id, application_status)
                            SELECT block_id, user_id, %s
                            FROM Blocks, Users
                            WHERE block_name = %s AND user_id = %s
                            AND NOT EXISTS (
                                SELECT 1 FROM applications WHERE block_id = (SELECT block_id FROM Blocks WHERE block_name = %s) AND applicant_id = %s
                            );
                        """, [application_status, block_name, user_id, block_name, user_id])

                        if cursor.rowcount > 0:
                            print('Application inserted successfully.')
                            # Insert membership
                            cursor.execute("""
                                INSERT INTO membership (block_id, user_id, status, permissions)
                                SELECT block_id, user_id, %s, %s
                                FROM Blocks, Users
                                WHERE block_name = %s AND user_id = %s;
                            """, [membership_status, membership_permissions, block_name, user_id])
                            print('Membership entry created.')

                            cursor.execute("""
                                SELECT application_id FROM applications
                                WHERE block_id = (SELECT block_id FROM Blocks WHERE block_name = %s)
                                AND applicant_id = %s;
                            """, [block_name, user_id])
                            application_id = cursor.fetchone()[0]

                            # Insert vote with default count of 0
                            cursor.execute("""
                                INSERT INTO votes (voter_id, application_id, vote_count)
                                VALUES (%s, %s, %s);
                            """, [None, application_id, 0])
                            print('Vote record added with default count of 0.')
                        else:
                            print('You have already applied to this block.')

                except Exception as e:
                    print(f'Error inserting application: {str(e)}')

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


@require_POST  # Ensures that this view can only handle POST requests.
def send_message(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        thread_title = request.POST.get('thread_title')
        recipient = request.POST.get('recipient', 'friend')  # Default to 'friend' if not specified
        friend_id = request.POST.get('friend_id', None)  # Default to None if not specified
        text_body = request.POST.get('text_body', '')

        query1 = '''
        INSERT INTO Thread (thread_title)
        VALUES (%s)
        RETURNING thread_id;'''
        
        query2 = '''
        INSERT INTO Message (user_id, thread_id, recipient, friend_id, text_body)
        VALUES (%s, %s, %s, %s, %s);
        '''

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(query1, [thread_title])
                    thread_id = cursor.fetchone()[0]  # Fetch the newly created thread_id
                    
                    cursor.execute(query2, (user_id, thread_id, recipient, friend_id, text_body))
                    print("Executed SQL:", query2, (user_id, thread_id, recipient, friend_id, text_body))

            return render(request, 'success.html')
        except Exception as e:
            return render(request, 'error.html')
    else:
        return HttpResponse("Unauthorized", status=401)


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

def membership_requests(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
    if request.method == 'GET':
        membership_requests = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.application_id, 
                    a.block_id, 
                    b.block_name,
                    a.applicant_id, 
                    u.user_name,
                    a.application_status,
                    v.vote_count
                FROM Applications a
                JOIN Membership m ON a.block_id = m.block_id
                JOIN Blocks b ON a.block_id = b.block_id
                JOIN Users u ON a.applicant_id = u.user_id
                JOIN votes v ON a.application_id = v.application_id
                WHERE m.user_id = %s and v.vote_count < 3
            """, [user_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            membership_requests = [
                dict(zip(columns, row))
                for row in rows
            ]
        print(membership_requests)
        return render(request, 'membership_requests.html', {'membership_requests': membership_requests})

    
def insert_vote(request,application_id):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        if request.method == 'POST':
            print("application_id", application_id)
            with connection.cursor() as cursor:
                try:
                    cursor.execute(""" SELECT applicant_id FROM applications WHERE application_id = %s;
                                   """, [application_id])
                    row = cursor.fetchone()
                    if row is not None:
                        applicant_id = row[0]
                    else:
                        return ("Application ID not found")
                    # Insert or increment vote record
                    cursor.execute("""
                        INSERT INTO votes (voter_id, application_id, vote_count)
                        VALUES (
                            (SELECT user_id FROM Users WHERE user_id = %s),
                            %s,
                            1
                        )
                        ON CONFLICT (application_id) DO UPDATE
                        SET vote_count = votes.vote_count + 1
                        WHERE votes.application_id = %s
                        RETURNING vote_count;
                    """, [user_id, application_id, application_id])
                    vote_count = cursor.fetchone()[0]
                    print('Voted successfully.')

                    # Check if vote count has reached 3, then update membership status to 'approved'
                    if vote_count == 3:
                        print("VOTE 3 hogya")
                        cursor.execute("""
                            UPDATE membership
                            SET status = 'approved',permissions = 'read'
                            WHERE block_id = (SELECT block_id FROM applications WHERE application_id = %s)
                            AND user_id = %s;
                            UPDATE votes
                            SET voter_id = %s where application_id = %s;
                        """, [application_id, applicant_id, user_id, application_id])
                        print('Membership status updated to approved.')
                
                    
                except IntegrityError as e:
                    print('Error inserting or updating vote:', str(e))
                    print('You may have already voted or there is another constraint violation.')
    return render(request, 'success.html')

def users(request):
    users = Users.objects.all()
    return render(request, 'users.html', {'users': users})

def find_user(username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE user_name = %s", [username])
        result = cursor.fetchall()
        return result
    
def search_users(request):
    users = []  # This will hold the search results
    if 'search_term' in request.GET:
        search_term = request.GET['search_term']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_name ILIKE %s", [f"%{search_term}%"])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            users = [
                dict(zip(columns, row))
                for row in rows
            ]

    # Render the same template whether or not there was a search
    return render(request, 'users.html', {'users': users})

def add_neighbor(request, neighbor_id):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        if request.method == 'POST':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO neighbors (user_id, neighbor_id) VALUES (%s, %s)", [user_id, neighbor_id])
                return render(request, 'success.html')
            except IntegrityError:
                # Handle specific database integrity issues, e.g., duplicate entries
                return HttpResponse("Cannot add duplicate neighbor entry.", status=409)
            except DatabaseError:
                # Handle general database errors
                return HttpResponse("Database error occurred.", status=500)
            except Exception as e:
                # Log exception or send it to your error tracking system
                print(f"An error occurred: {e}")  # Simple print, replace with logging if necessary
    # Redirect to home page on any other issues or if not a POST request
    return redirect(reverse('home'))  # Assumes 'home' is the name of the URL pattern for your home page

def add_friend(request, friend_id):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        if request.method == 'POST':
            try:
                with connection.cursor() as cursor:
                    # Attempt to insert a new friendship
                    cursor.execute("INSERT INTO friendship (user_id, friend_id) VALUES (%s, %s)", [user_id, friend_id])
                return render(request, 'success.html')
            except IntegrityError:
                # Handle specific database integrity issues
                return HttpResponse("Cannot add duplicate friendship entry.", status=409)
            except DatabaseError:
                # Handle other database errors
                return HttpResponse("Database error occurred.", status=500)
            except Exception as e:
                # Handle unexpected exceptions
                # Ideally, log this error to a logging system
                print(f"An error occurred: {e}")  # Simple print, replace with logging if necessary
    # Redirect to home page on any other issues or if not a POST request
    return redirect(reverse('home'))  # Assumes 'home' is the name of the URL pattern for your home page

def view_member_status(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
    try:
        membership = Membership.objects.get(user_id=user_id)
        block = membership.block_id.block_name
        status = membership.status
        response = f"Membership Status: {status}, Block: {block}"
    except Membership.DoesNotExist:
        response = "No membership information found."
    return HttpResponse(response)

def list_friends(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']  # Assumed to be set during user login

        with connection.cursor() as cursor:
            # Use the user_id directly from the session for the SQL query
            cursor.execute("""
                SELECT u.*
                FROM users u
                JOIN friendship f ON u.user_id = f.friend_id
                WHERE f.user_id = %s
            """, [user_id])
            friends_raw = cursor.fetchall()  # Fetch all records

        # Assuming that the indices 3 and 4 in friends_raw correspond to first_name and last_name
        friends_list = [f"{friend[1]} : {friend[2]} {friend[3]}" for friend in friends_raw]

        return render(request, 'friends_list.html', {'friends': friends_list})
    else:
        return HttpResponse("Please login to see the friends list.")
    
def list_neighbors(request):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']  # Assumed to be set during user login

        with connection.cursor() as cursor:
            # Use the user_id directly from the session for the SQL query
            cursor.execute("""
                SELECT u.*
                FROM users u
                JOIN neighbors f ON u.user_id = f.neighbor_id
                WHERE f.user_id = %s
            """, [user_id])
            neighbors_raw = cursor.fetchall()  # Fetch all records

        # Assuming that the indices 3 and 4 in friends_raw correspond to first_name and last_name
        neighbors_list = [f"{neighbor[1]} : {neighbor[2]} {neighbor[3]}" for neighbor in neighbors_raw]

        return render(request, 'neighbors_list.html', {'neighbors': neighbors_list})
    else:
        return HttpResponse("Please login to see the friends list.")
    

def get_threads_by_block(request, block_id):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT t.thread_id, t.thread_title
                    FROM message m
                    JOIN thread t ON m.thread_id = t.thread_id
                    WHERE m.block_id = %s
                """, [block_id])
                rows = cursor.fetchall()
            threads = [{'thread_id': row[0], 'thread_title': row[1]} for row in rows]
            print(threads)
            return render(request, 'block_thread.html', {'threads': threads})
        except Exception as e:
            print("Error fetching threads by block_id:", str(e))


def get_threads_by_hood(request, hood_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.thread_id, t.thread_title
                FROM message m
                JOIN thread t ON m.thread_id = t.thread_id
                WHERE m.hood_id = %s
            """, [hood_id])
            rows = cursor.fetchall()
        threads = [{'thread_id': row[0], 'thread_title': row[1]} for row in rows]
        print(threads)
        return render(request, 'hood_thread.html', {'threads': threads})
    except Exception as e:
        print("Error fetching threads by hood_id:", str(e))

def get_threads_by_friend(request, friend_id):
    if 'is_logged_in' in request.session and request.session['is_logged_in']:
        user_id = request.session['user_id']
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT t.thread_id, t.thread_title, m.text_body
                    FROM message m
                    JOIN thread t ON m.thread_id = t.thread_id
                    WHERE m.friend_id = %s
                """, [friend_id])
                rows = cursor.fetchall()
            threads = [{'thread_id': row[0], 'thread_title': row[1], 'message': row[2]} for row in rows]
            print(threads)
            return render(request, 'friends_thread.html', {'threads': threads})
        except Exception as e:
            print("Error fetching threads by friend_id:", str(e))
