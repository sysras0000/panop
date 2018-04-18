from django.shortcuts import render

# Create your views here.


def help(request):

    context = {
        'base_url': 'http://' + request.get_host()
    }

    return render(request, 'help.html', context)
