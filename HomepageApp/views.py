import requests
import random
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
import qrcode
from io import BytesIO
from collegeApp.models import Student
from .forms import RegistrationForm, IdUploadForm
from .ocr_api import extract_text_from_api, verify_ocr_data
from .utils import process_extracted_text
import pytesseract
from PIL import Image
import cv2
import re
import os
from fuzzywuzzy import fuzz
from django.core.files.base import ContentFile
from adminApp.models import College
from gate.models import Attendance


User = get_user_model()

otp_storage = {}

# Your 2Factor API Key
API_KEY = "7ce894d3-f694-11ef-8b17-0200cd936042"

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
            active_colleges = College.objects.filter(active=1)  # Get only active colleges
            
            if user_exists:
                return render(request, "qr_display.html", {"phone": phone})  # Redirect to login if user exists
            else:
                return render(request, "student_signup.html", {"phone": phone, "active_colleges": active_colleges})  # Redirect to sign-up if user doesn't exist

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


# import requests

def preprocess_image(image_path):
    """Convert image to grayscale and apply adaptive thresholding."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)


def extract_field(ocr_text, pattern):
    """Extracts a specific field using regex."""
    match = re.search(pattern, ocr_text, re.IGNORECASE)
    if match:
        return " ".join(match.group(1).strip().split())  # Remove extra spaces & normalize
    return None


def normalize_text(text):
    """Normalize text by removing special characters and converting to lowercase."""
    if not text:
        return ""
    return " ".join(re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower().split())

# def verify_ocr(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES.get("college_id_card")
#         form_name = request.POST.get("name")
#         form_event = request.POST.get("event")
#         type_of_visitor = request.POST.get("type_of_visitor")
#         phone = request.POST.get("phone")
#         form_college = request.POST.get("college")
#         form_id = request.POST.get("id")
#         visit_date = request.POST.get("datetime")

#         print(form_name, form_college, form_id, visit_date, phone, type_of_visitor, form_event)

#         if not uploaded_file:
#             return JsonResponse({"success": False, "error": "No image uploaded."})

#         # Save uploaded image temporarily
#         temp_dir = "/tmp"
#         os.makedirs(temp_dir, exist_ok=True)
#         image_path = os.path.join(temp_dir, uploaded_file.name)

#         with open(image_path, "wb") as f:
#             for chunk in uploaded_file.chunks():
#                 f.write(chunk)

#         # Preprocess Image for better OCR
#         img = cv2.imread(image_path)
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#         # # ✅ *Ensure Tesseract Path is Set*
#         # pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

#         # Tesseract ka correct path set karein
#         pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#         # OCR Processing
#         extracted_text = pytesseract.image_to_string(thresh)
#         print("🔍 Raw OCR Output:\n", extracted_text)

#         # Improved Regex-based Field Extraction
#         extracted_name = extract_field(extracted_text, r"(?i)Name\s*[:\-]?\s*([A-Za-z\s]+)")
#         extracted_college = extract_field(extracted_text, r"(?i)(Chitkara\s+University|[\w\s]+University)")
#         extracted_id = extract_field(extracted_text, r"(?i)(\d{10,})")  # Extracts 10+ digit numbers

#         # Normalize extracted and form data
#         extracted_name = normalize_text(extracted_name) if extracted_name else ""
#         extracted_college = normalize_text(extracted_college) if extracted_college else ""
#         extracted_id = normalize_text(extracted_id) if extracted_id else ""

#         form_name = normalize_text(form_name)
#         form_college = normalize_text(form_college)
#         form_id = normalize_text(form_id)

#         # Debugging: Print extracted vs. form data
#         print(f"📌 Extracted Name: {extracted_name} | Form Name: {form_name}")
#         print(f"📌 Extracted College: {extracted_college} | Form College: {form_college}")
#         print(f"📌 Extracted id: {extracted_id} | Form id: {form_id}")

#         # Fuzzy matching with threshold adjustment
#         name_match = fuzz.partial_ratio(form_name, extracted_name) > 65
#         college_match = fuzz.partial_ratio(form_college, extracted_college) > 65
#         id_match = form_id == extracted_id  # id should be exact

#         errors = []
#         if not name_match:
#             errors.append("Name does not match.")
#         if not college_match:
#             errors.append("College name does not match.")
#         if not id_match:
#             errors.append("id does not match.")

#         if errors:
#             return JsonResponse({"success": False, "error": " | ".join(errors)})

#         # ✅ Save Student Data if OCR verification is successful
#         student, created = Student.objects.update_or_create(
#             phone=phone,
#             defaults={
#                 "name": form_name,
#                 "event": form_event,
#                 "type_of_visitor": type_of_visitor,
#                 "college": form_college,
#                 "id": form_id,
#                 "datetime": visit_date,
#                 # "college_id_card": uploaded_file,  # Save the uploaded image
#             }
#         )
#         if created:
#             return generate_qr_code(request,student.id)  # Generate QR code for the new student
        
#         return JsonResponse({"success": True, "message": "Student data stored successfully!", "student_id": student.id})

#     return JsonResponse({"success": False, "error": "Invalid request."})


from datetime import datetime

# def verify_ocr(request):
#     if request.method == "POST":
#         # Fetching form data
#         uploaded_file = request.FILES.get("college_id_card")
#         form_name = request.POST.get("name")
#         form_event = request.POST.get("event")
#         type_of_visitor = request.POST.get("type_of_visitor")
#         phone = request.POST.get("phone")
#         form_college = request.POST.get("college")
#         form_id = request.POST.get("id")
#         visit_date_str = request.POST.get("datetime")

#         print(f"📌 Received Data:\nName: {form_name}, College: {form_college}, ID: {form_id}, Date: {visit_date_str}, Phone: {phone}, Visitor Type: {type_of_visitor}")

#         if not uploaded_file:
#             return JsonResponse({"success": False, "error": "No image uploaded."})

#         # Validate & Convert `visit_date`
#         try:
#             visit_date = datetime.strptime(visit_date_str, "%Y-%m-%dT%H:%M")  # Adjust format as per your frontend
#         except ValueError:
#             return JsonResponse({"success": False, "error": "Invalid date format."})

#         # ✅ Save uploaded file temporarily
#         temp_dir = "/tmp"
#         os.makedirs(temp_dir, exist_ok=True)
#         image_path = os.path.join(temp_dir, uploaded_file.name)

#         with open(image_path, "wb") as f:
#             for chunk in uploaded_file.chunks():
#                 f.write(chunk)

#         # ✅ Preprocess Image for OCR
#         img = cv2.imread(image_path)
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#         # ✅ Ensure Tesseract Path is Set
#         pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#         # OCR Processing
#         extracted_text = pytesseract.image_to_string(thresh)
#         print("🔍 Raw OCR Output:\n", extracted_text)

#         # ✅ Extract key fields using regex
#         extracted_name = extract_field(extracted_text, r"(?i)Name\s*[:\-]?\s*([A-Za-z\s]+)")
#         extracted_college = extract_field(extracted_text, r"(?i)(Chitkara\s+University|[\w\s]+University)")
#         extracted_id = extract_field(extracted_text, r"(?i)(\d{10,})")  # Extracts 10+ digit numbers

#         # ✅ Normalize extracted & form data
#         extracted_name = normalize_text(extracted_name) if extracted_name else ""
#         extracted_college = normalize_text(extracted_college) if extracted_college else ""
#         extracted_id = normalize_text(extracted_id) if extracted_id else ""

#         form_name = normalize_text(form_name)
#         form_college = normalize_text(form_college)
#         form_id = normalize_text(form_id)

#         # ✅ Debugging: Print extracted vs. form data
#         print(f"📌 Extracted Name: {extracted_name} | Form Name: {form_name}")
#         print(f"📌 Extracted College: {extracted_college} | Form College: {form_college}")
#         print(f"📌 Extracted ID: {extracted_id} | Form ID: {form_id}")

#         # ✅ Fuzzy matching with threshold adjustment
#         name_match = fuzz.partial_ratio(form_name, extracted_name) > 65
#         college_match = fuzz.partial_ratio(form_college, extracted_college) > 65
#         id_match = form_id == extracted_id  # ID should be exact

#         errors = []
#         if not name_match:
#             errors.append("Name does not match.")
#         if not college_match:
#             errors.append("College name does not match.")
#         if not id_match:
#             errors.append("ID does not match.")

#         if errors:
#             return JsonResponse({"success": False, "error": " | ".join(errors)})

#         # ✅ Save Student Data if OCR verification is successful
#         student, created = Student.objects.update_or_create(
#             phone=phone,
#             defaults={
#                 "name": form_name,
#                 "event": form_event,
#                 "type_of_visitor": type_of_visitor,
#                 "college": form_college,
#                 "id": form_id,
#                 "datetime": visit_date,
#             }
#         )
#         if created:
#             return generate_qr_code(request, student.id)  # Generate QR code for the new student
        
#         return JsonResponse({"success": True, "message": "Student data stored successfully!", "student_id": student.id})

#     return JsonResponse({"success": False, "error": "Invalid request."})



def verify_ocr(request):
    if request.method == "POST":
        # Fetching form data
        uploaded_file = request.FILES.get("college_id_card")
        form_name = request.POST.get("name")
        form_event = request.POST.get("event")
        type_of_visitor = request.POST.get("type_of_visitor")
        phone = request.POST.get("phone")
        form_college = request.POST.get("college")
        form_id = request.POST.get("id")
        visit_date_str = request.POST.get("datetime")

        if not uploaded_file:
            return JsonResponse({"success": False, "error": "No image uploaded."})

        # Validate & Convert `visit_date`
        try:
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return JsonResponse({"success": False, "error": "Invalid date format."})

        # ✅ Save uploaded file temporarily
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        image_path = os.path.join(temp_dir, uploaded_file.name)

        with open(image_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # ✅ Preprocess Image for OCR
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # ✅ Ensure Tesseract Path is Set
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        # OCR Processing
        extracted_text = pytesseract.image_to_string(thresh)

        # ✅ Extract key fields using regex
        extracted_name = extract_field(extracted_text, r"(?i)Name\s*[:\-]?\s*([A-Za-z\s]+)")
        extracted_college = extract_field(extracted_text, r"(?i)(Chitkara\s+University|[\w\s]+University)")
        extracted_id = extract_field(extracted_text, r"(?i)(\d{10,})")

        # ✅ Normalize extracted & form data
        extracted_name = normalize_text(extracted_name) if extracted_name else ""
        extracted_college = normalize_text(extracted_college) if extracted_college else ""
        extracted_id = normalize_text(extracted_id) if extracted_id else ""

        form_name = normalize_text(form_name)
        form_college = normalize_text(form_college)
        form_id = normalize_text(form_id)

        # ✅ Fuzzy matching with threshold adjustment
        name_match = fuzz.partial_ratio(form_name, extracted_name) > 65
        college_match = fuzz.partial_ratio(form_college, extracted_college) > 65
        id_match = form_id == extracted_id

        # ✅ Debugging: Print extracted vs. form data
        print(f"📌 Extracted Name: {extracted_name} | Form Name: {form_name}")
        print(f"📌 Extracted College: {extracted_college} | Form College: {form_college}")
        print(f"📌 Extracted ID: {extracted_id} | Form ID: {form_id}")

        errors = []
        if not name_match:
            errors.append("Name does not match.")
        if not college_match:
            errors.append("College name does not match.")
        if not id_match:
            errors.append("ID does not match.")

        if errors:
            return JsonResponse({"success": False, "error": " | ".join(errors)})

        # ✅ Fetch College instance
        college_instance = College.objects.filter(college_name__iexact=form_college).first()
        if not college_instance:
            return JsonResponse({"success": False, "error": "College not found in the database."})

        # ✅ Ensure Student is Created First
        student, created = Student.objects.update_or_create(
            phone=phone,
            defaults={
                "name": form_name,
                "event": form_event,
                "type_of_visitor": type_of_visitor,
                "college": college_instance,
                "roll_no": form_id,
                "datetime": visit_date,
            }
        )

        # ✅ Ensure "Pending" attendance exists and is linked properly
        pending_attendance, created = Attendance.objects.get_or_create(
            student=student,  # ✅ Correct Foreign Key Assignment
            defaults={"status": '2'}
        )

        # ✅ Update Student with Attendance Reference
        student.attendance = pending_attendance
        student.save()

        if created:
            return generate_qr_code(request, student.id)  # Generate QR code for the new student
        
        return JsonResponse({"success": True, "message": "Student data stored successfully!", "student_id": student.id})

    return JsonResponse({"success": False, "error": "Invalid request."})



def student_form(request):
    extracted_data = None
    error_message = None  

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("✅ Form Valid Hai!")
            print(form.cleaned_data)  # Debugging form data
            
            # ✅ Extract form data
            form_data = {
                "name": form.cleaned_data['name'],
                "college": form.cleaned_data['college'],
                "id": form.cleaned_data['id'],
            }
            print("📌 Form Data: ", form_data)

            college_id_card = form.cleaned_data['college_id_card']

            if college_id_card:
                try:
                    extracted_text = extract_text_from_api(college_id_card)
                    extracted_data = process_extracted_text(extracted_text)

                    verification_result = verify_ocr_data(extracted_text, form_data)

                    if "✅" not in verification_result:
                        return render(request, 'student_signup.html', {
                            'form': form,
                            'error_message': verification_result,
                            'processed_data': extracted_data,
                            'active_colleges': College.objects.filter(active=True)  # ✅ Fix
                        })

                except Exception as e:
                    print("❌ OCR Error:", str(e))
                    messages.error(request, f"OCR Error: {str(e)}")
                    return render(request, 'student_signup.html', {
                        'form': form,
                        'error_message': "OCR failed",
                        'active_colleges': College.objects.filter(active=True)  # ✅ Fix
                    })

            # ✅ Save Student Data
            student, created = Student.objects.update_or_create(
                id=form.cleaned_data['id'],  # ✅ Unique Identifier Fix
                defaults={
                    "name": form.cleaned_data['name'],
                    "event": form.cleaned_data['event'],
                    "type_of_visitor": form.cleaned_data['type_of_visitor'],
                    "college": form.cleaned_data['college'],
                    "phone": form.cleaned_data['phone'],
                    "college_id_card": college_id_card,
                    "datetime": now()
                }
            )

            messages.success(request, 'Student registered successfully!')
            generate_qr_code(request, student.id)

            return redirect('qr_display', student_id=student.id)

        else:
            print("❌ Form Invalid Hai!")
            print(form.errors)  # Debugging errors

    else:
        form = RegistrationForm()
        active_colleges = College.objects.filter(active=True)  # ✅ Fix

    return render(request, 'student_signup.html', {
        'form': form,
        'processed_data': extracted_data,
        'error_message': error_message,
        'active_colleges': active_colleges  # ✅ Fix
    })


# def student_form(request):
#     extracted_data = None
#     error_message = None  

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             print("✅ Form Valid Hai!")
#             print(form.cleaned_data)  # Check karo kya data aaya hai
#         else:
#             print("❌ Form Invalid Hai!")
#             print(form.errors)  # Yeh batayega kya issue hai

#         if form.is_valid():
#             form_data = {
#                 "name": form.cleaned_data['name'],
#                 "college": form.cleaned_data['college'],
#                 "id": form.cleaned_data['id'],
#             }
#             print(form_data)

#             college_id_card = form.cleaned_data['college_id_card']

#             if college_id_card:
#                 try:
#                     extracted_text = extract_text_from_api(college_id_card)
#                     extracted_data = process_extracted_text(extracted_text)

#                     verification_result = verify_ocr_data(extracted_text, form_data)

#                     if "✅" not in verification_result:
#                         return render(request, 'student_signup.html', {
#                             'form': form,
#                             'error_message': verification_result,
#                             'processed_data': extracted_data,
#                             'active_colleges': College.objects.filter(active=1)  # ✅ Fix
#                         })

#                 except Exception as e:
#                     print("In error")
#                     messages.error(request, f"OCR Error: {str(e)}")
#                     return render(request, 'student_signup.html', {
#                         'form': form,
#                         'error_message': "OCR failed",
#                         'active_colleges': College.objects.filter(active=1)  # ✅ Fix
#                     })

#             # Save Student Data
#             student, created = Student.objects.update_or_create(
#                 id=form.cleaned_data['id'],  # ✅ Fix: Ensure Unique Identifier
#                 defaults={
#                     "name": form.cleaned_data['name'],
#                     "event": form.cleaned_data['event'],
#                     "type_of_visitor": form.cleaned_data['type_of_visitor'],
#                     "college": form.cleaned_data['college'],
#                     "phone": form.cleaned_data['phone'],
#                     "college_id_card": college_id_card,
#                     "datetime": now()
#                 }
#             )

#             messages.success(request, 'Student registered successfully!')
#             generate_qr_code(request, student.id)

#             # Redirect to QR display page after saving
#             return redirect('qr_display', student_id=student.id)

#     else:
#         form = RegistrationForm()
#         active_colleges = College.objects.filter(active=1)  # ✅ Fix

#     return render(request, 'student_signup.html', {
#         'form': form,
#         'processed_data': extracted_data,
#         'error_message': error_message,
#         'active_colleges': active_colleges  # ✅ Fix
#     })


def upload_image(request):
    if request.method == 'POST':
        form = IdUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.cleaned_data['image']
            extracted_text = extract_text_from_api(uploaded_image)
            processed_data = process_extracted_text(extracted_text)

            return render(request, 'upload_success.html', {
                'image': uploaded_image,
                'text': extracted_text,
                'processed_data': processed_data
            })

# def generate_qr_code(request, student_id):
#     student = get_object_or_404(Student, id=student_id)
#     print("✅ Generating QR for:", student.name)  # Debugging

#     qr = qrcode.make(f"Student ID: {student.id}, Name: {student.name}")
#     buffer = BytesIO()
#     qr.save(buffer, format="PNG")

#     student.qr_code.save(f"qr_{student.id}.png", ContentFile(buffer.getvalue()), save=True)
#     print("✅ QR Code saved!")
    
    
#     return qr_display(request,student.id)



# def qr_display(request, student_id):
#     student = get_object_or_404(Student, id=student_id)
#     qr_code=student.qr_code
#     name=student.name
#     context = {
#         'image_url': qr_code.url,
#         'name': name
#     }
#     print(context)
#     return render(request, 'qr_display.html', context)


def generate_qr_code(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    print("✅ Generating QR for:", student.name)  # Debugging

    qr = qrcode.make(f"Student ID: {student.id}, Name: {student.name}, visitor_type: {student.type_of_visitor}, event: {student.event}")
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    student.qr_code.save(f"qr_{student.id}.png", ContentFile(buffer.getvalue()), save=True)
    print("✅ QR Code saved!")
    
    
    return qr_display(request,student.id)



def qr_display(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    qr_code=student.qr_code
    name=student.name
    context = {
        'image_url': qr_code.url,
        'name': name
    }
    print(context)
    
    return render(request, 'qr_display.html', context)