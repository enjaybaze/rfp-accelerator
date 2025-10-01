class User:
    def __init__(self, userid=None, ldap=None, role='PA', status=True, updated_by=None, updated_date=None):
        self.userid = userid
        self.ldap = ldap
        self.role = role
        self.status = status
        self.updated_by = updated_by
        self.updated_date = updated_date
