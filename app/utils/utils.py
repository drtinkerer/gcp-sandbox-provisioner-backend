def generate_sandbox_id(user_email, request_time):
    """
        Generates a unique sandbox ID from the given user_email and current_timestamp.

        Args:
            user_email (str): The email address of the user.
            request_time (int): The current timestamp as datetime.now(UTC).

        Returns:
            str: The generated project ID.
        """
    extract_prefix = user_email.split("@")[0].replace(".", "-")
    epoch_timestamp_suffix = int(request_time.timestamp())
    return f"{extract_prefix}-{epoch_timestamp_suffix}"
