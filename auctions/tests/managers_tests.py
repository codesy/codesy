from model_mommy import mommy

from ..models import Vote, Claim

from . import MarketWithClaimTestCase


class ClaimManagerTestCase(MarketWithClaimTestCase):
    def test_voted_on_by_user_returns_claims(self):
        mommy.make(Vote, user=self.user2, claim=self.claim, approved=True)
        claims = Claim.objects.voted_on_by_user(self.user2)
        self.assertEqual(1, len(claims))
        for claim in claims:
            self.assertEqual(self.claim, claim)
