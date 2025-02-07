from flask import Flask, render_template, request, redirect,url_for, session, flash
#from pymongo import MongoClient
import functions
import database


app = Flask(__name__)
app.secret_key = 'your_secret_key' 


@app.route('/', methods=['POST', 'GET'])
def homePage():
    # Retrieve messages from the session
    success = session.pop('success', None)
    error = session.pop('error', None)

    if request.method == 'POST':
        result = functions.add_enquiry(request)

        if result == "success":  # Assuming add_enquiry returns 'success' on success
            session['success'] = "Enquiry submitted successfully!"
        else:
            session['error'] = "Failed to submit enquiry. Please try again."

        return redirect(url_for('homePage'))  # Redirect to the same page

    return render_template('home.html', success=success, error=error)
                    
                    
@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        value = functions.login_user()

        if value == 'not':
            session['error'] = "Username does not exist"
            return redirect(url_for('login'))

        if value == "admin":
            return redirect(url_for('adminhome'))

        if value == "tuser":
            session['success'] = "Login successful!"  # Set the success message
            return redirect(url_for('index'))  # Redirect to the index page

        session['error'] = "Incorrect username or password"
        return redirect(url_for('login'))

    # For GET requests
    success = session.pop('success', None)
    error = session.pop('error', None)
    return render_template('login.html', success=success, error=error)




@app.route("/index", methods=['GET', 'POST'])
def index():
    success = session.pop('success', None)  # Retrieve the success message
    return render_template('index.html', success=success)



@app.route("/adminhome",methods=['POST','GET'])
def adminhome():
    success = session.pop('success', None)  # Retrieve the success message
    return render_template('adminhome.html',msg=" ",success=success)


@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == 'POST':
        value = functions.register_func()

        if value == 'not match':
            session['error'] = "Passwords do not match"
            return redirect(url_for('register'))

        if not value:
            session['error'] = "User already exists"
            return redirect(url_for('register'))

        session['success'] = "Registration successful! Please log in."
        return redirect(url_for('login'))

    error = session.pop('error', None)
    return render_template('register.html', error=error)

@app.route("/about",methods=['POST','GET'])
def about():
    return render_template('about.html')

@app.route("/destination", methods=['POST', 'GET'])
def destination():
    destinations = database.get_all_destinations()  # Fetch data from the database
    return render_template('destination.html', destinations=destinations)

@app.route('/book_destination/<int:destination_id>', methods=['POST', 'GET'])
def book_destination(destination_id):
    if 'email' not in session:
        return redirect('/login')  # Redirect to login if not logged in
    
    user_email = session['email']  # Get the logged-in user's email
    user = database.get_user_by_email(user_email)  # Fetch the user details
    destination = database.get_destination_by_id(destination_id)  # Fetch the destination details
    
    if user and destination:
        # Add the booking to the Booking table
        booking_success = database.add_booking(
            user['id'],
            user['name'],
            user['phone'],
            destination['DestinationID'],  # DestinationID (correct key)
            destination['TourName'],  # TourName
            destination['Prize']  # Prize
        )
        return redirect('/destination')  # Redirect after successful booking


# @app.route('/image/<int:destination_id>')
# def serve_image(destination_id):
#     image_data = database.get_image_data(destination_id)
#     if image_data:
#         return send_file(io.BytesIO(image_data), mimetype='image/jpeg')
#     return "Image not found", 404

@app.route("/profile",methods=['POST','GET'])
def profile():
    email = functions.session_check()

    if email == "NO":
        return redirect(url_for('login'))  # Redirect to login if the session is not active
    
    # Get the user details by email
    user = database.getuser_by_email(email)  # Assuming you query the user details based on the email
    
    if not user:
        return "User not found", 404

    # Render the profile.html template and pass user details
    return render_template('profile.html', user=user)

@app.route("/contact",methods=['POST','GET'])
def contact():
    return render_template('contact.html')

@app.route("/forgotpassword",methods=['POST','GET'])
def forgotpassword():
    if request.method == 'POST':
        result = functions.forgot_password()
        if result == 'User not found':
            return render_template('forgotpassword.html', msg="User not found")
        return render_template('login.html', msg="Password updated. Please log in with your new password.")
    
    return render_template('forgotpassword.html')

@app.route('/add_destination', methods=['GET', 'POST'])
def add_destination():
    if request.method == 'POST':
        result = functions.add_destination(request)
        return render_template('adminhome.html', msg="")

    return render_template('adminhome.html')

@app.route('/adminmanageuser', methods=['GET'])
def admin_manage_user():
    users = database.get_all_users()  # Fetch all users
    return render_template('adminmanageuser.html', users=users)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    database.delete_user(user_id)
    return redirect('/adminmanageuser')


@app.route('/adminguestenquiry', methods=['GET'])
def admin_guest_enquiry():
    enquiries = database.get_all_enquiries()
    return render_template('adminguestenquiry.html', enquiries=enquiries)

@app.route('/delete_enquiry/<int:enquiry_id>', methods=['POST'])
def delete_enquiry(enquiry_id):
    database.delete_enquiry(enquiry_id)
    return redirect('/adminguestenquiry')

@app.route("/adminmanagebooking",methods=['POST','GET'])
def admin_manage_booking():
    booking_data = database.get_booking_data()  # Fetch data from the Booking table
    return render_template('adminmanagebooking.html', bookings=booking_data)

# @app.route('/deletebooking/<int:booking_id>', methods=['POST'])
# def delete_booking(booking_id):
#     database.delete_booking_from_db(booking_id)  # Call function to delete booking from database
#     return redirect('/adminmanagebooking')

@app.route('/logout')
def logout():
    functions.logout_user()
    return redirect('/')
    

if __name__ == '__main__':
    app.run(debug=True)