from venv import logger
from django.contrib import auth
from django.contrib.sites import requests
from django.contrib.auth import login, authenticate
from django.utils.translation import get_language
from .forms import RegistrationForm, LoginForm ,ExpenseForm
import markdown
from .models import Chat, Expense
from django.utils import timezone
from langchain_groq import ChatGroq
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.db.models import Sum
from django.conf import settings
import cv2
import google.generativeai as genai
import requests
OPENWEATHER_API_KEY = '2d0856879ba007d2ab90df7e77b2360d'
GROQ_API_KEY = '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'

from django.contrib.auth.decorators import login_required
from .forms import UserForm, FarmerProfileForm

@login_required
def profile_view(request):
    user = request.user
    profile = user.farmer_profile
    return render(request, 'profile_view.html', {'user': user, 'profile': profile})

@login_required
def profile_edit(request):
    user = request.user
    profile = user.farmer_profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = FarmerProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_view')
    else:
        user_form = UserForm(instance=user)
        profile_form = FarmerProfileForm(instance=profile)

    return render(request, 'profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

def home(request):
    user_name = request.user.username if request.user.is_authenticated else "Guest"

    return render(request, 'home.html', {'user_name': user_name})
def logout(request):
    auth.logout(request)
    return redirect('home')
# User Registration view
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# User Login view
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def ask_groq(message):
    try:
        selected_language = get_language()
        language_map = {
            "en": "English",
            "gu": "Gujarati",
            "hi": "Hindi",
            "mr": "Marathi",
        }
        language_name = language_map.get(selected_language, "English")
        llm = ChatGroq(
            temperature=0,
            max_tokens=None,
            model_name="llama-3.3-70b-versatile",
            groq_api_key=GROQ_API_KEY,
            max_retries=2,
        )
        messages = [
            f"You are an AI-powered sustainable farming advisor. Respond in {language_name}. "
            "Your goal is to assist small farmers with sustainable farming practices, including crop selection, pest management, "
            "and resource optimization. Provide actionable, practical advice to enhance productivity while ensuring environmental sustainability.",
        ("human", message),
        ]
        ai_msg = llm.invoke(messages)
        response = ai_msg.content
        html_response = markdown.markdown(response)
        return mark_safe(html_response)
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return mark_safe("Sorry, I couldn't process your request. Please try again later.")

def chatbot(request):
    if not request.user.is_authenticated:
        return redirect('login')

    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')

        if message:
            response = ask_groq(message)

            chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
            chat.save()

            return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot.html', {'chats': chats})

def get_crop_suggestions(temperature, rainfall,location):
    try:
        selected_language = get_language()
        language_map = {
            "en": "English",
            "gu": "Gujarati",
            "hi": "Hindi",
            "mr": "Marathi",
        }
        language_name = language_map.get(selected_language, "English")
        llm = ChatGroq(
            max_tokens=None,
            model_name="llama-3.3-70b-versatile",
            groq_api_key= GROQ_API_KEY,
            max_retries=2,
        )
        messages = [
            ("system",
             f"You are a helpful agriculture advisor. Respond in {language_name}. Based on the user's location '{location}', temperature {temperature}°C, "
             f"and rainfall {rainfall}mm, suggest 5 suitable crops for this environment. Provide only the names of the crops, with no additional explanation or preamble."),
            ("human", f"Location: {location}, Temperature: {temperature}°C, Rainfall: {rainfall}mm"),
        ]

        ai_msg = llm.invoke(messages)
        response = ai_msg.content.strip().split(", ")
        return response
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "Sorry, I couldn't process your request. Please try again later."
def suggest_crops(request):
    if request.method == "POST":
        location = request.POST.get("location")
        if not location:
            return render(request, "suggest_crops.html", {"error": "Please enter a location."})

        # Fetch weather data from OpenWeatherMap API
        weather_api_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        try:
            response = requests.get(weather_api_url)
            data = response.json()

            if response.status_code == 200:
                # Extract relevant weather data
                temperature = data["main"]["temp"]
                rainfall = data.get("rain", {}).get("1h", 0)  # Rainfall in mm (last 1 hour)

                # Get crop suggestions
                crops = get_crop_suggestions(temperature, rainfall,location)
                return render(
                    request,
                    "suggest_crops.html",
                    {
                        "location": location,
                        "temperature": temperature,
                        "rainfall": rainfall, "crops": crops},
                )
            else:
                return render(request, "suggest_crops.html", {"error": "Could not fetch weather data. Please try again."})

        except Exception as e:
            return render(request, "suggest_crops.html", {"error": f"Error fetching weather data: {e}"})

    return render(request, "suggest_crops.html")

from django.utils import translation

def set_language(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def expense_tracker(request):
    if not request.user.is_authenticated:
        return redirect('login')

    recent_expenses = Expense.objects.filter(user=request.user).order_by('-date')[:5]
    # Calculate the total expense from the recent ones
    total_expense = recent_expenses.aggregate(total=Sum('amount'))['total'] or 0
    # Handle form submission
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('view_expenses')
    else:
        form = ExpenseForm()

    # Aggregate total amounts per category
    category_totals = Expense.objects.filter(user=request.user).values('category').annotate(total=Sum('amount'))
    categories = [expense['category'] for expense in category_totals]
    totals = [float(expense['total']) for expense in category_totals]

    return render(request, "expense_tracker.html", {
        'recent_expenses': recent_expenses,
        'total_expense': total_expense,
        'form': form,
        'categories': categories,
        'totals': totals,
    })

def view_expenses(request):
    # Get all expenses
    expenses = Expense.objects.all().filter(user=request.user).order_by('-date')
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, "view_expenses.html", {"expenses": expenses, "total_expenses": total_expenses})

def get_weather(request):
    city = request.GET.get('city', 'London')

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # Extract necessary data from the API response
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        city_name = data['name']
        icon = data['weather'][0]['icon']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        feels_like = data['main']['feels_like']
    else:
        temperature = description = city_name = icon = humidity = wind_speed = pressure = feels_like = None

    return render(request, 'weather.html', {
        'temperature': temperature,
        'description': description,
        'city_name': city_name,
        'icon': icon,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'feels_like': feels_like
    })

def analytics(request):
    return render(request, 'analytics.html')



# ✅ Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_soil_image(image_path):
    """
    Sends the soil image to Gemini AI for analysis and returns soil type & recommended crops.
    """
    try:
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")

        model = genai.GenerativeModel("gemini-pro-vision")

        response = model.generate_content(
            ["Analyze this soil image and provide the soil type and recommended crops.", {"image": img_data}]
        )

        if response and response.text:
            lines = response.text.split("\n")
            soil_type = lines[0] if len(lines) > 0 else "Unknown Soil Type"
            suggested_crops = lines[1] if len(lines) > 1 else "No crop recommendations"
            return soil_type, suggested_crops
        else:
            return "Analysis Failed", "No crop recommendations"

    except Exception as e:
        return "Error", str(e)

# ✅ Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)




# Set your Gemini API key
GENAI_API_KEY = "AIzaSyCbKjFORqEr05gOSqyfjVWac40KCjbW65o"
genai.configure(api_key=GENAI_API_KEY)

def analyze_soil_with_gemini(image_path):
    """Analyzes soil image using Gemini AI 1.5 Flash and returns soil type and recommended crops."""
    try:
        # Read image and encode in Base64
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")

        # ✅ Update the prompt to force AI to return crop suggestions
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_data
                            }
                        },
                        {
                            "text": (
                                "Analyze this soil image and determine its type. "
                                "Then, based on the soil type, provide a list of 5 suitable crops that can be grown in this soil. "
                                "Return only the soil type and the crop names."
                            )
                        }
                    ]
                }
            ]
        }

        # ✅ Using Gemini 1.5 Flash model
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GENAI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=request_data, headers=headers)

        # Handle API response
        if response.status_code == 200:
            result = response.json()

            # ✅ Extract text output correctly
            if "candidates" in result and len(result["candidates"]) > 0:
                text_output = result["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "No output")
                lines = text_output.strip().split("\n")

                # ✅ Ensure soil type and suggested crops are extracted
                soil_type = lines[0] if len(lines) > 0 else "Unknown Soil Type"
                suggested_crops = lines[1:] if len(lines) > 1 else ["No crop recommendations"]

                return soil_type, ", ".join(suggested_crops)

            else:
                return "Analysis Failed", "No crop recommendations"

        else:
            return "Analysis Failed", f"Error: {response.json()}"

    except Exception as e:
        return "Error", str(e)


def is_fake_image(image_path):
    """Detect if an image is AI-generated using digital noise analysis."""
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
        return laplacian_var < 50  # Low variance indicates a possible fake image
    except Exception:
        return True  # Assume fake if error occurs


from django.shortcuts import render, redirect
from django.contrib import messages

def upload_soil_map(request):
    """Handles soil map upload, AI-based analysis, and fake image detection."""
    if request.method == "POST":
        soil_map_name = request.POST.get("soil_map_name")
        soil_image = request.FILES.get("soil_image")

        if not soil_map_name or not soil_image:
            messages.error(request, "❌ Please provide a valid soil map name and image.")
            return redirect("upload_soil_map")

        # Save the uploaded file
        soil_map = SoilAnalysis.objects.create(name=soil_map_name, image=soil_image)

        # Run AI Analysis
        soil_type, suggested_crops = analyze_soil_with_gemini(soil_map.image.path)

        # Detect Fake Image
        is_fake = is_fake_image(soil_map.image.path)

        # Save results in the database
        soil_map.soil_type = soil_type
        soil_map.suggested_crops = suggested_crops
        soil_map.is_fake = is_fake
        soil_map.save()

        messages.success(request, "✅ AI Analysis Complete!")
        return redirect("soil_analysis_results")

    return render(request, "upload_soil_map.html")

from django.shortcuts import render
from .models import SoilAnalysis

def soil_analysis_results(request):
    """
    Fetch and display the latest soil analysis result.
    """
    latest_analysis = SoilAnalysis.objects.last()  # Get the latest entry

    if not latest_analysis:
        return render(request, "soil_analysis_results.html", {"error": "No analysis results available."})
    suggested_crops_list = latest_analysis.suggested_crops.split(",") if latest_analysis.suggested_crops else []

    context = {
        "name": latest_analysis.name,
        "soil_type": latest_analysis.soil_type if latest_analysis.soil_type else "AI analysis failed",
        "suggested_crops": suggested_crops_list,
        "image_path": latest_analysis.image.url if latest_analysis.image else None,
    }

    return render(request, "soil_analysis_results.html", context)

import google.generativeai as genai
import base64

# ✅ Set up Gemini AI API Key
GENAI_API_KEY = "AIzaSyCbKjFORqEr05gOSqyfjVWac40KCjbW65o"
genai.configure(api_key=GENAI_API_KEY)

def generate_soil_analysis(image_path):
    """ Sends the soil image to Gemini AI for analysis and returns the soil type and recommended crops. """
    try:
        # Convert image to Base64
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode("utf-8")

        # Initialize Gemini AI Model
        model = genai.GenerativeModel("gemini-pro-vision")

        # Send AI Request
        response = model.generate_content(
            [
                "Analyze this soil image and provide the soil type and recommended crops for farming.",
                {"image": img_data},
            ]
        )

        # Extract AI Response
        if response and response.text:
            lines = response.text.split("\n")
            soil_type = lines[0] if len(lines) > 0 else "Unknown"
            suggested_crops = lines[1] if len(lines) > 1 else "No recommendations"
        else:
            soil_type = "Analysis Failed"
            suggested_crops = "No recommendations"

        return {"soil_type": soil_type, "suggested_crops": suggested_crops}

    except Exception as e:
        return {"soil_type": "Error", "suggested_crops": str(e)}



