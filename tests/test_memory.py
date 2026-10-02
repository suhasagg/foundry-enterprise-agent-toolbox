from app.memory import SevenLayerMemory
def test_seven_layers():
    m=SevenLayerMemory()
    for layer in ["working","conversation","episodic","semantic","procedural","entity","audit"]:
        m.put("t",layer,"k",{"x":1})
    s=m.snapshot("t")
    assert set(s)=={"working","conversation","episodic","semantic","procedural","entity","audit"}
