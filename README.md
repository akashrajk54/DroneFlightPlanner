# drone-flight-planner
A Django REST Framework (DRF) based web application for generating optimized flight paths for drones using polygon coordinates. Users can create polygons via an API, customize image overlap percentages, and receive an XML file with waypoints. Features robust error handling and efficient flight path algorithms.


# Setup

   1. Clone the repository:
       git clone https://github.com/akashrajk54/DroneFlightPlanner/tree/development

   2. Navigate to the project directory:
       cd DroneFlightPlanner

   3. Create a virtual environment (optional but recommended):
       python -m venv venv

   4. Activate the virtual environment:
      a). Windows:
          venv\Scripts\activate
      b). Linux/macOS:
          source venv/bin/activate

   5. Install dependencies:
      pip install -r requirements.txt

   6. Set up environment variables:
       # DATABASE Use: PostgresSQL
       DATABASE_NAME=''
       DATABASE_USER=''
       DATABASE_PASSWORD=''
       DATABASE_HOST='localhost'
       DATABASE_PORT='5432'

       MAX_TIME_LIMIT_TO_VERIFY_OTP='3' (otp valid max 3min)

       TWILIO_ACCOUNT_SID=''
       TWILIO_AUTH_TOKEN=''
       TWILIO_PHONE_NUMBER=''

       # During production 
            Debug = False
            ALLOWED_HOSTS = insted of ['*'], please add specific frontend url, so that request from anyother will be rejected.
       # Please Update DEFAULT_THROTTLE_RATES into the settings currently set to 100/Hours

   7. Run migrations to create the database schema:
      python manage.py makemigrations
      python manage.py migrate

   8. Create a superuser (admin) account:
      python manage.py createsuperuser

   9. Run the development server:
      python manage.py runserver
      (by default it will use 8000 port)



# Functionality:
The backend provides comprehensive functionality for managing Flight path, including user authentication, waypoint generation. Each API endpoint is designed to fulfill specific requirements, ensuring that users can perform desired actions efficiently and effectively.

# Code Quality:
The backend codebase adheres to best practices for clean, maintainable, and well-documented code. It follows the Django framework conventions, utilizes descriptive variable and function names, and includes comments and docstrings to explain the purpose and usage of different components.
# User Experience:
The backend aims to deliver a smooth and intuitive user experience by offering a straightforward API interface with clear and consistent endpoint naming and request/response formats. Error messages are informative and user-friendly, guiding users on how to rectify issues or provide necessary input.

# Problem Solving:
The backend effectively handles potential issues such as API errors and load performance through robust error handling mechanisms and optimization techniques. Error responses are properly formatted with appropriate HTTP status codes and error messages, enabling clients to identify and address issues promptly.

