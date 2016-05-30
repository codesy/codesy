from django import template

register = template.Library()


@register.assignment_tag
def actionable_claims_for_bid_for_user(bid, user):
    if bid:
        return bid.actionable_claims(user)


@register.assignment_tag
def bid_is_biddable(bid, user):
    if bid:
        return bid.is_biddable_by(user)
