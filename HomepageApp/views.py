
from django.shortcuts import render, redirect
from django.contrib import messages

import requests
import random
from django.contrib.auth import get_user_model

User = get_user_model()

otp_storage = {}

# Your 2Factor API Key
API_KEY = "a5850e61-f35a-11ef-8b17-0200cd936042"

def send_otp(request):
    """ Send OTP to user's phone """
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        if not phone:
            messages.error(request, "Phone number is required!")
            return redirect("send_otp")

        otp = random.randint(100000, 999999)  # Generate 6-digit OTP
        otp_storage[phone] = otp  # Store OTP temporarily
        request.session["phone"] = phone  # Store phone in session

        # Send OTP via 2Factor API
        url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{phone}/{otp}"
        response = requests.get(url)

        if response.status_code == 200:
            messages.success(request, f"OTP sent to {phone}!")
            return redirect("verify_otp")
        else:
            messages.error(request, "Failed to send OTP. Try again.")

    return render(request, "send_otp.html")



# def verify_otp(request):
#     if request.method == "POST":
#         entered_otp = request.POST.get("otp", "").strip()  # Get entered OTP
#         phone = request.session.get("phone")  # Retrieve phone from session
#         stored_otp = otp_storage.get(phone)  # Get OTP from storage

#         messages.get_messages(request).used = True  # 🚀 Clear old messages

#         if not stored_otp:  # OTP expired case
#             messages.error(request, "OTP expired! Request a new OTP.")
#             return render(request, "verify_otp.html", {"otp_expired": True})

#         if entered_otp == str(stored_otp):  # Convert both to string before comparing
#             messages.success(request, "OTP verified successfully!")
#             otp_storage.pop(phone, None)  # Remove OTP after verification
#             request.session.pop("otp", None)  # Clear session storage
#             return redirect("dashboard")  # Redirect to dashboard
        
#         else:  # Wrong OTP case
#             messages.error(request, "Invalid OTP! Please try again.")
#             return render(request, "verify_otp.html", {"otp_expired": False})

#     return render(request, "verify_otp.html", {"otp_expired": False})

def verify_otp(request):
    """ Verify OTP and check if user exists, then redirect to login or sign-up """
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()  # Get user-entered OTP
        phone = request.session.get("phone")  # Retrieve phone number from session
        stored_otp = otp_storage.get(phone)  # Get OTP from temporary storage

        messages.get_messages(request).used = True  # 🚀 Clear old messages

        if not stored_otp:  # OTP expired case
            messages.error(request, "OTP expired! Request a new OTP.")
            return render(request, "verify_otp.html", {"otp_expired": True})

        if entered_otp == str(stored_otp):  # Convert both to string before comparing
            messages.success(request, "OTP verified successfully!")
            otp_storage.pop(phone, None)  # Remove OTP after verification
            request.session.pop("otp", None)  # Clear session storage

            # 🔥 Check if user exists in the database
            user_exists = User.objects.filter(phone=phone).exists()

            if user_exists:
                return redirect("login")  # Redirect to login if user exists
            else:
                return redirect("signup")  # Redirect to sign-up if user doesn't exist

        else:  # Wrong OTP case
            messages.error(request, "Invalid OTP! Please try again.")
            return render(request, "verify_otp.html", {"otp_expired": False})

    return render(request, "verify_otp.html", {"otp_expired": False})


def resend_otp(request):
    """ Resend OTP when requested """
    phone = request.session.get("phone")  # Retrieve phone from session
    if not phone:
        messages.error(request, "Session expired. Enter your phone number again.")
        return redirect("send_otp")

    otp = random.randint(100000, 999999)  # Generate new OTP
    otp_storage[phone] = otp  # Store new OTP temporarily

    # Send new OTP via 2Factor API
    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{phone}/{otp}"
    response = requests.get(url)

    if response.status_code == 200:
        messages.success(request, f"New OTP sent to {phone}!")
    else:
        messages.error(request, "Error sending OTP. Try again.")

    return redirect("verify_otp")