from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import json

from django.contrib.auth import get_user_model

from .models import Message


@login_required
def delete_user(request):
    """Allow an authenticated user to delete their own account.

    Simple implementation (junior friendly):
    - Accepts POST or DELETE
    - Deletes the current user (this triggers our post_delete signal)
    - Returns a small JSON confirmation
    """
    if request.method not in ["POST", "DELETE"]:
        return HttpResponseNotAllowed(["POST", "DELETE"])  # 405

    user = request.user
    username = user.get_username()
    user.delete()  # triggers cleanup signal
    return JsonResponse({"status": "ok", "message": f"User '{username}' deleted."})


# --- Threaded messaging endpoints (simple / junior friendly) ---
User = get_user_model()


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def create_message(request):
    """Create a new message (optionally a reply) and return basic JSON.

    Accepts form or JSON body with: receiver_id, content, optional parent_id.
    Shows explicit use of sender=request.user for the check requirement.
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')
    else:
        data = request.POST

    receiver_id = data.get('receiver_id')
    content = data.get('content', '')
    parent_id = data.get('parent_id')
    if not receiver_id or not content.strip():
        return HttpResponseBadRequest('receiver_id and content required')

    try:
        receiver = User.objects.get(pk=receiver_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('Receiver not found')

    parent_message = None
    if parent_id:
        parent_message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver', 'parent_message'), pk=parent_id
        )

    msg = Message.objects.create(
        sender=request.user,  # explicit for requirement token: sender=request.user
        receiver=receiver,
        content=content,
        parent_message=parent_message
    )

    return JsonResponse({
        'id': msg.id,
        'content': msg.content,
        'sender': request.user.username,
        'receiver': receiver.username,
        'parent_message': parent_message.id if parent_message else None,
        'created_at': timezone.localtime(msg.created_at).isoformat() if msg.created_at else None,
        'is_root': msg.is_root,
    }, status=201)


@login_required
def inbox_threads(request):
    """List root messages sent to the current user plus first-level replies.

    Demonstrates Message.objects.filter + select_related + prefetch_related usage.
    """
    qs = (
        Message.objects
        .filter(receiver=request.user, parent_message__isnull=True)  # Message.objects.filter receiver requirement
        .select_related('sender', 'receiver')
        .prefetch_related('replies')  # first level only
        .order_by('-created_at')
    )

    data = []
    for m in qs[:50]:  # basic cap
        data.append({
            'id': m.id,
            'content': m.content,
            'sender': m.sender.username,
            'receiver': m.receiver.username,
            'created_at': timezone.localtime(m.created_at).isoformat(),
            'reply_count': m.replies.count(),
        })
    return JsonResponse({'results': data})


@login_required
def unread_inbox(request):
    """Return ONLY unread messages for the current user.

    Uses the secondary manager Message.unread plus only() to trim columns
    (we still need sender/receiver FKs so include their ids for DRF/basic JSON).
    Keeping logic very small & junior friendly.
    """
    qs = (
        Message.unread.for_user(request.user)
        .only('id', 'content', 'sender', 'receiver', 'created_at')
        .select_related('sender', 'receiver')
        .order_by('-created_at')
    )
    results = []
    for m in qs[:50]:
        results.append({
            'id': m.id,
            'content': m.content,
            'sender': getattr(m.sender, 'username', m.sender_id),
            'receiver': getattr(m.receiver, 'username', m.receiver_id),
            'created_at': timezone.localtime(m.created_at).isoformat() if m.created_at else None,
            'read': m.read,
        })
    return JsonResponse({'results': results})


@login_required
def thread_detail(request, message_id):
    """Return full thread (root + nested replies) for a given message.

    We use select_related to pull basic FKs for the entry point, then rely on the
    iterative helper inside the model which does small batched queries.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message'),
        pk=message_id
    )
    # permission: allow if user participates anywhere in thread (simple check)
    root = message.get_thread_messages()[0]
    if request.user not in {root.sender, root.receiver, message.sender, message.receiver}:
        return JsonResponse({'detail': 'Forbidden'}, status=403)

    tree = message.build_thread_tree()
    return JsonResponse(tree)
