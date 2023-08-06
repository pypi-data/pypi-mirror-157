def get_public_members(instance):
    members = []
    for member_name in dir(instance):
        if not member_name.startswith("__") and not member_name.startswith("_"):
            members.append(member_name)
    return members
