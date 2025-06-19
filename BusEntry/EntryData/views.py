from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import CustomUser
from django.utils import timezone
from .models import Bus_Data
from pytz import timezone as pytz_timezone
from .sheets_utils import append_to_sheet

# Bus numbers list
BUS_NUMBERS = [
    "6736", "6836", "6861", "6873", "6874", "6884", "6886", "6889", "6891", "6893",
    "6894", "6897", "6899", "6900", "6902", "6903", "6904", "6906", "6908", "6910",
    "6913", "6915", "6917", "6920", "6922", "6924", "6925", "6928", "6930", "6931",
    "6933", "6935", "6936", "6937", "6939", "6940", "6941", "6942", "6945", "6948",
    "6949", "6953", "6960", "6962", "6964", "6965", "6966", "6968", "6970", "6971",
    "6973", "6974", "6976", "6977", "6978", "6979", "6983", "6986", "6988", "6991",
    "6997", "7002", "7003", "7004", "7006", "7007", "7013", "7016", "7017", "7018",
    "7019", "7020", "7023", "7029", "7031", "7035", "7038", "7039", "7040", "7042",
    "7043", "7048", "7049", "7051", "7052", "7065", "7069", "7071", "7072", "7077",
    "7079", "7094", "7095", "7118", "7180", "7181", "7182", "7183", "7185", "7188",
    "7190", "7193", "7198", "7200", "7205", "7206", "7207", "7208", "7209", "7212",
    "7216", "7217", "7219", "7222", "7228", "7231", "7232", "7233", "7234", "7238",
    "7240", "7241", "7242", "7248", "7249", "7256", "7265", "7268", "7271", "7274"
]


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
                request.session['user_name'] = user.name   # Store the name in session
                messages.success(request, "Login successful!")
                return redirect('entry')
            else:
                messages.error(request, "Incorrect password.")
        except CustomUser.DoesNotExist:
            messages.error(request, "User ID not found.")
        return redirect('index')
    
from .sheets_utils import append_to_sheet, update_in_sheet

def Entry(request):
    user_name = request.session.get('user_name')
    if request.method == 'POST':
        date = request.POST.get('date')
        shift = request.POST.get('shift')
        bus_no = request.POST.get('busno')
        
        # Check for existing entry
        existing_entry = Bus_Data.objects.filter(
            date=date,
            bus_no=bus_no,
            shift=shift
        ).exists()

        if existing_entry:
            messages.error(request, f"❌ Entry already exists for this bus {bus_no}, {shift}, and {date}!")
            return redirect('entry')

        # Proceed if no duplicate exists
        out_kms = float(request.POST.get('outkms'))
        in_kms = float(request.POST.get('inkms')) if request.POST.get('inkms') != "" else 0.0
        soc = request.POST.get('soc') or "Not Provided"
        soc_in = request.POST.get('soc_in') or "Not Provided"
        diff = abs(in_kms - out_kms)
        india_tz = pytz_timezone('Asia/Kolkata')
        time_of_submission = timezone.now().astimezone(india_tz).strftime('%H:%M')

        # Create database entry
        entry = Bus_Data.objects.create(
            date=date,
            shift=shift,
            bus_no=bus_no,
            out_kms=out_kms,
            in_kms=in_kms,
            diff=diff,
            soc=soc,
            soc_in=soc_in,
            time_of_submission=time_of_submission,
            user_name=user_name
        )
        
        # Prepare data for Google Sheet (include ID as last column)
        sheet_data = [
            date,
            shift,
            bus_no,
            str(out_kms),
            str(in_kms),
            str(diff),
            soc,
            soc_in,
            time_of_submission,
            user_name
        ]
        SheetStatus = ""
        # Append to Google Sheet
        try:
            append_to_sheet(sheet_data)
            SheetStatus = "✅ Google Sheet Updated"
        except Exception as e:
            SheetStatus = f"Google Sheets error: {e}"
            print(f"Google Sheets error: {e}")
            messages.info(request, "✅ Data saved locally. Google Sheets update failed.")
        
        messages.success(request, f"✅ Bus data for {bus_no}, {shift}, and {date} submitted successfully! {SheetStatus}")
        return redirect('entry')

    return render(request, 'EntryForm.html', {
        'bus_numbers': BUS_NUMBERS,
    })


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
        
        # Store original values for Google Sheets update
        original_values = {
            'in_kms': entry.in_kms,
            'soc': entry.soc,
            'soc_in': entry.soc_in,
            'diff': entry.diff
        }
        
        # Update fields if provided
        if in_kms:
            entry.in_kms = float(in_kms)
            entry.diff = abs(entry.in_kms - entry.out_kms)
        if soc:
            entry.soc = soc
        if soc_in:
            entry.soc_in = soc_in
        
        entry.save()
        india_tz = pytz_timezone('Asia/Kolkata')
        # Prepare data for Google Sheet update
        sheet_data = {
            'date': entry.date.strftime('%Y-%m-%d'),  # or isoformat() if that's your sheet's format
            'shift': entry.shift,
            'bus_no': entry.bus_no,
            'out_kms': str(entry.out_kms),
            'in_kms': str(entry.in_kms),
            'diff': str(entry.diff),
            'soc': entry.soc,
            'soc_in': entry.soc_in,
            'time':timezone.now().astimezone(india_tz).strftime('%H:%M'),
            'user': entry.user_name,
        }
        print(sheet_data)
        # Update Google Sheet
        try:
            update_in_sheet(sheet_data)
            print("===================Success==========================")
        except Exception as e:
            print(f"Google Sheets update error: {e}")
            messages.info(request, "✅ Data updated locally. Google Sheets update failed.")
        
        messages.success(request, "✅ Entry updated successfully!")
        return redirect('update_list')
    
    return render(request, 'edit_entry.html', {'entry': entry})
