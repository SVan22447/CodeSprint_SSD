from django.shortcuts import render, redirect, get_object_or_404
from .models import QRCode
from django.http import HttpResponse
from django.contrib import messages

def index(request):
    return render(request, 'scanner/index.html')

def add_qr_code(request):
    if request.method == 'POST':
        print(request.POST)  # Выводим данные запроса в консоль
        qr_data = request.POST.get('qr_data')
        if qr_data:
            QRCode.objects.create(data=qr_data)
            messages.success(request, 'QR код успешно добавлен.')
        else:
            messages.error(request, 'Пожалуйста, введите данные QR кода.')
        return redirect('show_all_data')
    return render(request, 'scanner/addqrcode.html')

def show_all_data(request):
    qr_codes = QRCode.objects.all()
    return render(request, 'scanner/showalldata.html', {'qr_codes': qr_codes})

def delete_qr_code(request, pk):
    qr_code = get_object_or_404(QRCode, pk=pk)
    qr_code.delete()
    messages.success(request, 'QR код успешно удален.')
    return redirect('show_all_data')
