# /interactive_math_quiz/urls.py


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # User authentication URLs
    path('accounts/', include('apps.users.urls')),

    # Academics URLs (for the student dashboard and profile)
    path('academics/', include('apps.academics.urls')),

    # Quizzes URLs (for taking quizzes)
    path('quizzes/', include('apps.quizzes.urls')),

    # Admin Dashboard URLs - This line connects the new dashboard
    path('management/', include('apps.dashboard.urls')),

    # Core app URLs (for the homepage)
    path('', include('apps.core.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)