Day 1: Building a weather data collection system using AWS S3 and OpenWeather API

## Steps
1. mkdir weather-dashboard
2. mkdir src tests data
3. touch src/__init__.py src/weather_dashboard.py
4. touch requirements.txt README.md .env
5. git init
6. git branch -M main
7. `echo ".env" >> .gitignore` :.env stores environment vars so they aren't tracked
8. echo "__pycache__/" >> .gitignore
9. echo "*.zip" >> .gitignore
10. echo "python-dotenv==1.0.0" >> requirements.txt
11. echo "bboto3==1.26.137" >> requirements.txt
12. echo "requests==2.28.2" >> requirements.txt
13. run `aws configure`
14. create file that stores api key: `echo "OPENWEATHER_API_KEY=your_api_key" >> .env`
15. create bucket stores api data: `echo "AWA_BUCKET_NAME=weather-dashboard-${RANDOM}" >> .env
16. add code to GetYouAJob/weather-dashboard/src/weather_dashboard.py
17. create virtual env: `python3 -m venv .venv`
18a. activate virtual env: `source .venv/bin/activate`
18b. Recreate env:
    `rm -rf .venv`
`````python3 -m venv .venv`
    `source .venv/bin/activate`
19. install boto3 to virtual env: `pip install boto3`
19. `pip install -r requirements.txt`
20. Run python code: `python3 "src/weather_dashboard.py"`


