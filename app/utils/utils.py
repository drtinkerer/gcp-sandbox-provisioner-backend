def generate_project_id(user_email, current_timestamp):
    """
        Generates a unique project ID from the given user_email and current_timestamp.

        Args:
            user_email (str): The email address of the user.
            current_timestamp (int): The current timestamp as an integer.

        Returns:
            str: The generated project ID.
        """
    extract_prefix = user_email.split("@")[0].replace(".", "-")
    return f"{extract_prefix}-{current_timestamp}"
