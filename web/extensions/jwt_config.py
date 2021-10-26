#required to use get_current_user()
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data['sub']
    from web.api.user.user import SuperUser
    return SuperUser.get_by_id(user_id)