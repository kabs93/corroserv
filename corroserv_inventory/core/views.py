from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def home(request: HttpRequest) -> HttpResponse:

    context = {}

    return render(request, "core/home.html", context=context)


@login_required
def movement(request: HttpRequest, movement_type: str) -> HttpResponse:

    item_type = request.GET.get("item_type", None)

    context = {
        "movement_type": movement_type,
        "item_type": item_type,
    }

    return render(request, "core/movement.html", context=context)
