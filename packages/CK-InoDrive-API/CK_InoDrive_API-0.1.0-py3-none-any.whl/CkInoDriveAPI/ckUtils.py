import uuid


def get_transaction_id(length=8):
    """Returns a random string of length string_length."""

    # Convert UUID format to a Python string.
    random = str(uuid.uuid4())

    # Make all characters uppercase.
    random = random.upper()

    # Remove the UUID '-'.
    random = random.replace("-", "")

    # Return the random string.
    return random[0:length]
