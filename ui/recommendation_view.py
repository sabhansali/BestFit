"""Recommendation approval controls."""


def render_approval_controls(st, state):
    if state.status.value != "waiting_for_approval":
        return None
    st.subheader("Human approval")
    st.caption("Review the deterministic recommendation and choose an action.")
    approve, reject = st.columns(2)
    if approve.button("Approve recommendation", type="primary", use_container_width=True):
        state.record_human_decision(True)
        return "approved"
    if reject.button("Reject / re-analyze", use_container_width=True):
        state.record_human_decision(False)
        return "rejected"
    return None
