"""Recommendation approval controls."""


def render_approval_controls(st, state):
    if state.status.value != "waiting_for_approval":
        return None
    st.subheader("Human approval")
    st.caption("Review the deterministic recommendation and choose an action.")
    reason = st.selectbox(
        "If rejecting, what should be improved?",
        (
            "too_expensive",
            "wrong_color",
            "wrong_style",
            "wrong_occasion",
            "poor_combination",
            "other",
        ),
        format_func=lambda value: value.replace("_", " ").title(),
    )
    feedback = st.text_input("Optional feedback")
    approve, reject = st.columns(2)
    if approve.button("Approve recommendation", type="primary", use_container_width=True):
        state.record_human_decision(True)
        return "approved"
    if reject.button("Reject / re-analyze", use_container_width=True):
        state.record_human_decision(False, reason, feedback)
        return "rejected"
    return None
