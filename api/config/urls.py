from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import include, url
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.conf.urls.static import static
from dashboard.views import ProcessLoginView, DashBoardView, UserLogoutView, UserSignUpView

from auth.views import AuthApiListView
from utils.router import DefaultRouterWithAPIViews

admin.site.site_header = settings.ADMIN_SITE_HEADER

router = DefaultRouterWithAPIViews()
router.register('api/auth', AuthApiListView)

schema_view = get_schema_view(title=settings.API_BROWSER_HEADER, public=True)
doc_urls = include_docs_urls(title=settings.API_BROWSER_HEADER)
api_browser_urls = include('rest_framework.urls')
auth_urls = include('auth.urls')
users_urls = include('users.urls')

urlpatterns = [
    path('api/', auth_urls),
    path('api/users/', users_urls),
    path('api/docs/', doc_urls),
    path('api/schema/', schema_view),
    path('api/browser/', api_browser_urls),
    path('api/admin/', admin.site.urls),
    path('', DashBoardView.as_view()),
    url(r'^login/?$', ProcessLoginView.as_view()),
    url(r'^dashboard/?$', DashBoardView.as_view()),
    url(r'^logout/?$', UserLogoutView.as_view()),
    url(r'^signup/?$', UserSignUpView.as_view()),
]

urlpatterns += router.urls

# Serve media assets for development, only works while DEBUG=True
# https://docs.djangoproject.com/en/2.0/howto/static-files/#serving-files-uploaded-by-a-user-during-development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
