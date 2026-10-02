from app.planner import planner
def test_action_is_write():
    p=planner.compile("research issue and send update")
    a=[t for t in p.tasks if t.kind=="action"][0]
    assert a.risk=="write"
def test_verify_last_dependencies():
    p=planner.compile("research knowledge")
    v=[t for t in p.tasks if t.kind=="verify"][0]
    assert "research" in v.dependencies and "knowledge" in v.dependencies
