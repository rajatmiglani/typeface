from django.http import JsonResponse
from django.http import HttpResponseNotFound, HttpResponse
from .models import UploadedFile
from django.shortcuts import render
from datetime import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


import os

def upload_page(request):
    return render(request, 'upload.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        
        file_name = uploaded_file.name
        created_at = datetime.now()
        size = uploaded_file.size
        file_type = os.path.splitext(file_name)[-1].lower()
        
        with open('uploads/' + file_name, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        uploaded_file_obj = UploadedFile.objects.create(
            file_name=file_name,
            created_at=created_at,
            size=size,
            file_type=file_type
        )
        
        file_identifier = uploaded_file_obj.id
        return JsonResponse({"file_identifier": file_identifier}, status=201)
    
    return JsonResponse({"error": "File upload failed."}, status=400)

def read_file(request, fileId):
    try:
        uploaded_file = UploadedFile.objects.get(id=fileId)
    except UploadedFile.DoesNotExist:
        return HttpResponseNotFound("File not found")

    file_name = uploaded_file.file_name

    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)

    if not os.path.exists(file_path):
        return HttpResponseNotFound("File not found")

    with open(file_path, 'rb') as file:
        file_data = file.read()

    response = HttpResponse(file_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@csrf_exempt
def delete_file(request, fileId):
    if request.method == 'DELETE':
        try:
            uploaded_file = UploadedFile.objects.get(id=fileId)
        except UploadedFile.DoesNotExist:
            return JsonResponse({'message': 'File not found'}, status=404)

        file_name = uploaded_file.file_name

        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            uploaded_file.delete()
            return JsonResponse({'message': 'File deleted successfully'}, status=200)
        else:
            return JsonResponse({'message': 'File not found'}, status=404)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    

def list_files(request):
    files = UploadedFile.objects.all()

    files_metadata = []
    for file in files:
        file_metadata = {
            'id': file.id,
            'file_name': file.file_name,
            'created_at': file.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'size': file.size,
            'file_type': file.file_type
        }
        files_metadata.append(file_metadata)

    return JsonResponse(files_metadata, safe=False)