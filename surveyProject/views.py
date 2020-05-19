from django.shortcuts import render


def homepage(request):
    error = ""
    if request.method == 'GET' and 'error' in request.GET:
        error = request.GET['error']
    return render(request, 'home.html', {'error': error})
