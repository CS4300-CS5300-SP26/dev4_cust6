import hashlib

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm
from .models import UserProfile

LOGIN_FAILURE_LIMIT = 5
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60


def _safe_cache_part(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _client_ip(request):
    """Return the best available client IP for lightweight throttling."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _login_cache_key(request, username):
    normalized_username = (username or "").strip().lower() or "unknown"
    ip_part = _safe_cache_part(_client_ip(request))
    username_part = _safe_cache_part(normalized_username)
    return f"login-failures:{ip_part}:{username_part}"


def _too_many_login_attempts(request, username):
    attempts = cache.get(_login_cache_key(request, username), 0)
    return attempts >= LOGIN_FAILURE_LIMIT


def _record_failed_login(request, username):
    key = _login_cache_key(request, username)
    if cache.add(key, 1, LOGIN_FAILURE_WINDOW_SECONDS):
        return
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, LOGIN_FAILURE_WINDOW_SECONDS)


def _clear_failed_logins(request, username):
    cache.delete(_login_cache_key(request, username))


def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to Crinkle, {user.username}!")
            return redirect("profile")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        username = request.POST.get("username", "")
        if _too_many_login_attempts(request, username):
            messages.error(
                request,
                "Too many failed login attempts. Please try again later.",
            )
            form = LoginForm(request, data=request.POST)
            return render(
                request,
                "accounts/login.html",
                {"form": form},
                status=429,
            )

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            _clear_failed_logins(request, username)

            next_url = request.GET.get("next", "")
            if url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("profile")

        _record_failed_login(request, username)
        messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


def guest_view(request):
    if request.method == "POST":
        request.session["is_guest"] = True
    return redirect("index")
