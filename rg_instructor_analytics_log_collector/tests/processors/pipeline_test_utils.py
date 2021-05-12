"""Utility functionality to test pipelines."""
import json


class TestRecord():
    """
    Dummy `Record` class.

    Encapsulates data fields for all pipeline.
    """

    LOG_TIME = 123
    USER_ID = 123
    EVENT_TYPE = "test_event_type"
    COURSE_ID = 456

    def __init__(self,
                 record_type,
                 log_time=LOG_TIME,
                 user_id=USER_ID,
                 event_type=EVENT_TYPE,
                 course_id=COURSE_ID):
        """
        Initialise a test record object.

        Facilitates objects mocking.
        """
        self.record_type = record_type
        self.log_time = log_time

        event_body = None
        if self.record_type == "discussion":
            event_body = {"commentable_id": "test_commentable_id",
                          "id": "test_discussion_id",
                          "thread_type": "test_thread_type",
                          "category_id": "test_category_id"}
        elif self.record_type == "student_step" or self.record_type == "course_activity":
            event_body = json.dumps({"test_key": "test_value"})

        self.log_message = json.dumps({"event": event_body,
                                      "context": {"user_id": user_id,
                                                  "course_id": course_id}})
        self.message_type = event_type

    def log_message(self):
        """
        Return `log_message` value.

        Facilitates objects mocking.
        """
        return self.log_message
