from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed


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
