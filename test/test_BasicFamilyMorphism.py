from Tropical2020.basic_families import *

# Set up a free monoid for sake of convenience
freeMonoid = Monoid()
freeMonoid.addgen("a")
freeElementA = freeMonoid.Element({"a": 1})
freeMonoid.addgen("b")
freeElementB = freeMonoid.Element({"b": 1})
freeMonoid.addgen("c")
freeElementC = freeMonoid.Element({"c": 1})
freeMonoid.addgen("d")
freeElementD = freeMonoid.Element({"d": 1})


def test_example_3_5():
    C = BasicFamily("Example 3.5")

    v1 = Vertex("v1", 0)
    v2 = Vertex("v2", 0)
    v3 = Vertex("v3", 1)
    # Take all edges to be of the same length (for sake of mesa testing)
    e1 = Edge("e1", freeElementA, v1, v2)
    e2 = Edge("e2", freeElementB, v2, v3)
    e3 = Edge("e3", freeElementC, v1, v3)
    e4 = Edge("e4", freeElementD, v1, v1)
    leg = Leg("l", v1)

    C.addEdges({e1, e2, e3, e4})
    C.addLeg(leg)
    C.monoid = freeMonoid

    automorphisms = list(BasicFamilyMorphism.getAutomorphismsIter(C))

    # This family only possesses the identity automorphism
    assert len(automorphisms) == 1
    for auto in automorphisms:
        for x in C.vertices | C.edges | C.legs:
            assert auto(x) == x

def test_theta_curve():
    C = BasicFamily("Theta Curve")

    v1 = Vertex("Left", 0)
    v2 = Vertex("Right", 0)

    m = Monoid()
    m.addgen("a")
    a = m.Element({"a": 1})

    e1 = Edge("top", a, v1, v2)
    e2 = Edge("middle", a, v1, v2)
    e3 = Edge("bottom", a, v1, v2)

    C.monoid = m
    C.addEdges({e1, e2, e3})

    automorphisms = list(BasicFamilyMorphism.getAutomorphismsIter(C))


    """    for auto in automorphisms:
    print("\n\nPrinting an automorphism")
    print(str(v1), " |-> ", str(auto(v1)))
    print(str(v2), " |-> ", str(auto(v2)))
    print(str(e1), " |-> ", str(auto(e1)))
    print(str(e2), " |-> ", str(auto(e2)))
    print(str(e3), " |-> ", str(auto(e3)))"""

    assert len(automorphisms) == 6
