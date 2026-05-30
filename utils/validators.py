def validate_topic(topic):

    if not topic:
        return False

    if len(topic.strip()) < 2:
        return False

    return True