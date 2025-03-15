def user_display_name(request):
    if request.user.is_authenticated:
        if request.user.get_full_name():
            display_name = request.user.get_full_name()
        else:
            display_name = request.user.email
    else:
        display_name = None
    
    return {'user_display_name': display_name}

def username_processor(request):
    """
    Provide a 'username' variable for all templates.
    """
    if request.user.is_authenticated:
        # Kullanıcı adı olarak email'i kullan
        username = request.user.email
    else:
        username = None
    
    return {'username': username} 