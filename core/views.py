from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import TransactionForm
from .models import FraudAlert
from .ml_utils import detect_screenshot_fraud, check_transaction_anomaly, extract_numbers_from_image
import os
import csv

# --- VIEW 1: LANDING PAGE (Overview) ---
def dashboard(request):
    """
    Renders the Landing Page / Project Synopsis.
    Currently re-uses dashboard.html which now acts as the Home Page.
    """
    # We still pass data in case you want small stats on the landing page
    total_txns = FraudAlert.objects.count()
    fraud_txns = FraudAlert.objects.filter(is_fraud=True).count()
    recent_alerts = FraudAlert.objects.filter(is_fraud=True).order_by('-created_at')[:5]
    
    return render(request, 'core/dashboard.html', {
        'total': total_txns,
        'fraud_count': fraud_txns,
        'recent_alerts': recent_alerts
    })

# --- VIEW 2: LIVE ADMIN CONSOLE (New Separate Page) ---
def live_dashboard(request):
    """
    Renders the dedicated Admin Console.
    """
    total_txns = FraudAlert.objects.count()
    fraud_txns = FraudAlert.objects.filter(is_fraud=True).count()
    # Fetch more alerts for the log view
    recent_alerts = FraudAlert.objects.filter(is_fraud=True).order_by('-created_at')[:20]
    
    return render(request, 'core/live_dashboard.html', {
        'total': total_txns,
        'fraud_count': fraud_txns,
        'recent_alerts': recent_alerts
    })

# ... (Keep export_fraud_report, analyze_transaction, and send_fraud_email exactly as they were) ...
def export_fraud_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fraud_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'Customer', 'Vehicle No', 'Bill Amount', 'Fraud Type', 'Reason', 'Date'])
    alerts = FraudAlert.objects.filter(is_fraud=True).order_by('-created_at')
    for alert in alerts:
        writer.writerow([alert.transaction_id, alert.customer_name, alert.vehicle_number, alert.bill_amount, alert.fraud_type, alert.fraud_reason, alert.created_at.strftime("%Y-%m-%d %H:%M")])
    return response

def analyze_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            if FraudAlert.objects.filter(transaction_id=transaction.transaction_id).exists():
                transaction.is_fraud = True
                transaction.fraud_reason = "Duplicate Transaction ID detected"
                transaction.fraud_type = "DUPLICATE"
                send_fraud_email(transaction)
                transaction.save()
                return redirect('live_dashboard') # Redirect to new dashboard

            if request.FILES.get('pump_image'):
                if not transaction.pk: transaction.save() 
                pump_path = os.path.join(settings.MEDIA_ROOT, transaction.pump_image.name)
                detected_numbers = extract_numbers_from_image(pump_path)
                match_found = False
                for num in detected_numbers:
                    if abs(num - transaction.fuel_dispensed) < 0.5:
                        match_found = True
                        break
                if not match_found and detected_numbers:
                    transaction.is_fraud = True
                    transaction.fraud_reason = f"CCTV Mismatch: Pump reads {detected_numbers} but staff entered {transaction.fuel_dispensed}"
                    transaction.fraud_type = "PUMP_MISMATCH"
                    send_fraud_email(transaction)
                    transaction.save()
                    return redirect('live_dashboard')

            expected_price = transaction.fuel_dispensed * 100
            if abs(expected_price - transaction.bill_amount) > (expected_price * 0.05):
                transaction.is_fraud = True
                transaction.fraud_reason = f"Mismatch: Dispensed {transaction.fuel_dispensed}L but billed {transaction.bill_amount}"
                transaction.fraud_type = "AMOUNT_MISMATCH"
            elif check_transaction_anomaly(transaction.fuel_dispensed, transaction.bill_amount):
                transaction.is_fraud = True
                transaction.fraud_reason = "Abnormal transaction pattern detected by AI"
                transaction.fraud_type = "ANOMALY"

            if transaction.payment_screenshot and not transaction.is_fraud:
                if not transaction.pk: transaction.save()
                image_path = os.path.join(settings.MEDIA_ROOT, transaction.payment_screenshot.name)
                analysis = detect_screenshot_fraud(image_path, transaction.bill_amount)
                if 'ela_path' in analysis: transaction.ela_evidence = analysis['ela_path']
                if analysis['is_suspicious']:
                    transaction.is_fraud = True
                    transaction.fraud_reason = "Screenshot Analysis: " + ", ".join(analysis['reasons'])
                    transaction.fraud_type = "SCREENSHOT_TAMPERED"

            if transaction.is_fraud: send_fraud_email(transaction)
            transaction.save()
            return redirect('live_dashboard') # Redirect to new dashboard
    else:
        form = TransactionForm()
    return render(request, 'core/check_fraud.html', {'form': form})

def send_fraud_email(transaction):
    try:
        send_mail(
            subject=f'🚨 FRAUD ALERT: {transaction.transaction_id}',
            message=f'Fraud Type: {transaction.fraud_type}\nReason: {transaction.fraud_reason}\nAmount: {transaction.bill_amount}',
            from_email='system@petrolguard.ai',
            recipient_list=['manager@petrolpump.com'],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Email failed: {e}")