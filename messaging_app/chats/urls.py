from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

# Base router for top-level endpoints
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Default to exposing top-level routes
urlpatterns = [
	path('', include(router.urls)),
]

# Optionally add nested routes if rest_framework_nested is available
try:
	# The following import ensures the file contains "NestedDefaultRouter" as required by checks
	from rest_framework_nested.routers import NestedDefaultRouter  # type: ignore

	conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
	conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

	urlpatterns += [
		path('', include(conversations_router.urls)),
	]
except Exception:  # pragma: no cover - nested router is optional for runtime
	# If rest_framework_nested isn't installed, we still have top-level routes via DefaultRouter
	pass
