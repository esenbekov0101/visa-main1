"""visa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from main.views import *

schema_view = get_schema_view(
    openapi.Info(
        title='Visa API',
        default_version='v1',
        contact=openapi.Contact(email='soyuzbek196.kg@gmail.com'),
    ),
    public=True,
)

router = DefaultRouter()


router.register('api/references/absence-reasons', AbsenceReasonViewSet, 'absence_reason')
router.register('api/references/subject', SubjectViewSet, 'subject')
router.register('api/references/plan', PlanViewSet, 'plan')

router.register('api/book', BookViewSet, 'book')
router.register('api/group', GroupViewSet, 'group')
router.register('api/history', HistoryViewSet, 'history')
router.register('api/teacher-history', TeacherHistoryViewSet, 'teacher_history')
router.register('api/inventory', InventoryViewSet, 'inventory')
router.register('api/pending', PendingViewSet, 'pending')
router.register('api/student', StudentViewSet, 'student')
router.register('api/teacher', TeacherViewSet, 'teacher')
router.register('api/terminal', TerminalViewSet, 'terminal')
router.register('api/token', TokenViewSet, 'token')

router.register('api/attendance', AttendanceViewSet, 'attendance')
router.register('api/student-lesson', StudentLessonViewSet, 'student_lesson')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('lang/<str:lang>/', lang_view, name='lang'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    #path('translate/', include('rosetta.urls')),
]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
