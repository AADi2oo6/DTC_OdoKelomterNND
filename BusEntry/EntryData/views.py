from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser
from django.utils import timezone
from .models import Bus_Data
from pytz import timezone as pytz_timezone

# Bus numbers list
BUS_NUMBERS = ['6939', '7051', '7039', '7038', '6978', '6965', '6942', '6904', '7185', '7233']

def Entry(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        shift = request.POST.get('shift')
        bus_no = request.POST.get('busno')
        out_kms = float(request.POST.get('outkms'))
        in_kms = float(request.POST.get('inkms')) if request.POST.get('inkms') is not "" else 0.0
        soc = request.POST.get('soc') or "Not Provided"
        soc_in = request.POST.get('soc_in') or "Not Provided"
        diff = abs(in_kms-out_kms)
        india_tz = pytz_timezone('Asia/Kolkata')
        time_of_submission = timezone.now().astimezone(india_tz).strftime('%H:%M')

        # Save to database
        Bus_Data.objects.create(
            date=date,
            shift=shift,
            bus_no=bus_no,
            out_kms=out_kms,
            in_kms=in_kms,
            diff=diff,
            soc=soc,
            soc_in = soc_in,
            time_of_submission=time_of_submission
        )
        messages.success(request, "✅ Bus data submitted successfully!")
        return redirect('entry')  # change to your url name

    return render(request, 'EntryForm.html', {
        'bus_numbers': BUS_NUMBERS,
    })

def index(request):
    return render(request, 'index.html')

def register_user(request):
    if request.method == "POST":
        name = request.POST['regName']
        user_id = request.POST['regId']
        password = request.POST['regPassword']
        confirm_password = request.POST['regConfirmPassword']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('index')

        if CustomUser.objects.filter(user_id=user_id).exists():
            messages.error(request, "User ID already exists.")
            return redirect('index')

        user = CustomUser(name=name, user_id=user_id, password=make_password(password))
        user.save()
        messages.success(request, "Registered successfully.")
        return redirect('index')




def login_user(request):
    if request.method == "POST":
        user_id = request.POST['loginId']
        password = request.POST['loginPassword']

        try:
            user = CustomUser.objects.get(user_id=user_id)
            if check_password(password, user.password):
                request.session['user_id'] = user.user_id
                messages.success(request, "Login successful!")
                return redirect('entry')
            else:
                messages.error(request, "Incorrect password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User ID not found.")
        return redirect('index')
    

def update_list(request):
    # Get distinct bus numbers from database
    bus_numbers = Bus_Data.objects.order_by('bus_no').values_list('bus_no', flat=True).distinct()
    
    # Handle filters
    selected_bus = request.GET.get('bus_no')
    selected_date = request.GET.get('date', timezone.now().date().isoformat())
    
    # Query entries
    entries = Bus_Data.objects.all()
    if selected_bus:
        entries = entries.filter(bus_no=selected_bus)
    if selected_date:
        entries = entries.filter(date=selected_date)
    
    return render(request, 'update_list.html', {
        'bus_numbers': bus_numbers,
        'entries': entries,
        'selected_bus': selected_bus,
        'selected_date': selected_date,
    })

def edit_entry(request, entry_id):
    entry = Bus_Data.objects.get(id=entry_id)
    if request.method == 'POST':
        # Update only in_kms and SOC
        in_kms = request.POST.get('inkms')
        soc = request.POST.get('soc')
        soc_in = request.POST.get("soc_in")
        
        if in_kms:
            entry.in_kms = float(in_kms)
            entry.diff = abs(entry.in_kms - entry.out_kms)
        if soc:
            entry.soc = soc
        if soc_in:
            entry.soc_in=soc_in
        
        entry.save()
        messages.success(request, "✅ Entry updated successfully!")
        return redirect('update_list')
    
    return render(request, 'edit_entry.html', {'entry': entry})
