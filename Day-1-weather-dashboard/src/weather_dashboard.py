#weather-dashboard.py

# import required libraries
import os  # For interacting with environment variables
import json  # For working with JSON data
import boto3  # AWS SDK for Python, used for interacting with S3
import requests  # Used to make HTTP requests to the OpenWeather API
from datetime import datetime  # Used for working with timestamps
from dotenv import load_dotenv  # Used to load environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()  # Loads the variables from the .env file into the environment

class WeatherDashboard:
    def __init__(self):
        # Initialize the class with the necessary variables
        self.api_key = os.getenv('OPENWEATHER_API_KEY')  # Retrieve the OpenWeather API key from environment
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')  # Retrieve the AWS S3 bucket name from environment
        self.s3_client = boto3.client('s3')  # Initialize the S3 client using boto3

    def create_bucket_if_not_exists(self):
        """Check if S3 bucket exists; if not, create it"""
        try:
            # Attempt to check the bucket's existence
            self.s3_client.head_bucket(Bucket=self.bucket_name)  # This checks if the bucket exists
            print(f"Bucket {self.bucket_name} exists")  # Print if the bucket exists
        except:
            # If the bucket does not exist, handle the exception and attempt to create it
            print(f"Creating bucket {self.bucket_name}")
            try:
                # Attempt to create the bucket (simplified creation for the 'us-east-1' region)
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                print(f"Successfully created bucket {self.bucket_name}")  # Print success message
            except Exception as e:
                # Catch any exception and print an error message if bucket creation fails
                print(f"Error creating bucket: {e}")

    def fetch_weather(self, city):
        """Fetch weather data for a given city from the OpenWeather API"""
        base_url = "http://api.openweathermap.org/data/2.5/weather"  # Base URL for OpenWeather API
        params = {
            "q": city,  # City name for the weather request
            "appid": self.api_key,  # API key for OpenWeather authentication
            "units": "imperial"  # Set units to imperial (Fahrenheit for temperature)
        }
        
        try:
            # Make an HTTP GET request to OpenWeather API with the specified parameters
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise an exception for any non-2xx status codes
            return response.json()  # Return the JSON data if the request is successful
        except requests.exceptions.RequestException as e:
            # Handle any exception that occurs during the request and print the error message
            print(f"Error fetching weather data: {e}")
            return None  # Return None if the request fails

    def save_to_s3(self, weather_data, city):
        """Save weather data to S3 bucket"""
        if not weather_data:  # Check if weather_data is None or empty
            return False  # Return False to indicate failure
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        file_name = f"weather-data/{city}-{timestamp}.json"
        
        try:
            weather_data['timestamp'] = timestamp
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(weather_data),
                ContentType='application/json'
            )
            print(f"Successfully saved data for {city} to S3")
            return True
        except Exception as e:
            print(f"Error saving to S3: {e}")
            return False
    
    
def main():
    # Create an instance of the WeatherDashboard class
    dashboard = WeatherDashboard()
    
    # Create the S3 bucket if it doesn't already exist
    dashboard.create_bucket_if_not_exists()
    
    # List of cities to fetch weather data for
    cities = ["Philadelphia", "Seattle", "New York"]
    
    for city in cities:
        print(f"\nFetching weather for {city}...")  # Print the city currently being processed
        # Fetch the weather data for the current city
        weather_data = dashboard.fetch_weather(city)
        if weather_data:  # Check if the weather data was successfully retrieved
            # Extract specific weather details from the fetched data
            temp = weather_data['main']['temp']  # Temperature in Fahrenheit
            feels_like = weather_data['main']['feels_like']  # Feels like temperature in Fahrenheit
            humidity = weather_data['main']['humidity']  # Humidity percentage
            description = weather_data['weather'][0]['description']  # Weather condition description
            
            # Print the fetched weather details
            print(f"Temperature: {temp}°F")
            print(f"Feels like: {feels_like}°F")
            print(f"Humidity: {humidity}%")
            print(f"Conditions: {description}")
            
            # Attempt to save the weather data to S3
            success = dashboard.save_to_s3(weather_data, city)
            if success:
                print(f"Weather data for {city} saved to S3!")  # Success message if the data is saved to S3
        else:
            print(f"Failed to fetch weather data for {city}")  # Message if the data retrieval failed

# This condition ensures that the main function is executed only if the script is run directly
if __name__ == "__main__":
    main()  # Run the main function to start the process
