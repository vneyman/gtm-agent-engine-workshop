import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test")

from gtm_agent.gtm_agent import send_prospect_email


def call_send(prospect, **kwargs):
    return send_prospect_email.func(
        prospect=prospect,
        subject="Checking in",
        body="Following up on our conversation.",
        runtime=None,
        from_rep={"name": "Rep", "email": "rep@example.com"},
        **kwargs,
    )


class SendProspectEmailTests(unittest.TestCase):
    def test_disqualified_prospect_is_blocked_without_message_id(self):
        prospect = {"prospect_id": "LEAD-1", "name": "Prospect", "email": "prospect@example.com"}
        with patch("gtm_agent.gtm_agent.data_service.get_prospect_record", return_value={"disqualified": True}):
            result = call_send(prospect)

        self.assertEqual(result, {
            "status": "blocked",
            "reason": "Prospect is flagged disqualified in the CRM; rep confirmation required before outreach.",
        })

    def test_disqualified_prospect_can_be_sent_with_explicit_override(self):
        prospect = {"prospect_id": "LEAD-1", "name": "Prospect", "email": "prospect@example.com"}
        with patch("gtm_agent.gtm_agent.data_service.get_prospect_record", return_value={"disqualified": True}):
            result = call_send(prospect, override_disqualified=True)

        self.assertEqual(result["status"], "sent")
        self.assertTrue(result["message_id"].startswith("msg-"))

    def test_non_disqualified_prospect_is_sent(self):
        prospect = {"prospect_id": "LEAD-1", "name": "Prospect", "email": "prospect@example.com"}
        with patch("gtm_agent.gtm_agent.data_service.get_prospect_record", return_value={"disqualified": False}):
            result = call_send(prospect)

        self.assertEqual(result["status"], "sent")
        self.assertTrue(result["message_id"].startswith("msg-"))
