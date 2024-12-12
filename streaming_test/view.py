from django.shortcuts import render


def stream_page(request):
    # Render the HTML template
    return render(request, 'stream_page.html')
