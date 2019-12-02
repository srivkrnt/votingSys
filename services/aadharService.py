def verify_aadhar_number(aadhar_number):
    allowed = '0123456789'

    if len(aadhar_number) != 12:
        return False

    for digit in aadhar_number:
        if digit not in allowed:
            return False

    return True
