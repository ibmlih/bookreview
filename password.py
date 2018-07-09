def isStrongPassword(password):
    """A password is considered strong if
        1. It has at least 6 characters and at most 20 characters.
        2. It must contain at least one lowercase letter,
        at least one uppercase letter, and at least one digit."""
    if not (6 <= len(password) <= 20):
        return False

    lowercase = False
    uppercase = False
    digit = False

    for char in password:
        if char.islower():
            lowercase = True

        elif char.isupper():
            uppercase = True

        elif char.isdigit():
            digit = True

    if lowercase and uppercase and digit:
        return True
    else:
        return False
