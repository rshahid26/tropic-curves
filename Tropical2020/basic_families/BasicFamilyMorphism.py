from Tropical2020 import BasicFamily, MonoidHomomorphism, Vertex, Edge, Leg


class BasicFamilyMorphism(object):
    def __init__(self, domain, codomain, curveMorphismDict, monoidMorphism):

        # Type checking
        assert isinstance(domain, BasicFamily), "The domain of a basic family morphism should be a BasicFamily."
        assert isinstance(codomain, BasicFamily), "The codomain of a basic family morphism should be a BasicFamily."
        assert isinstance(curveMorphismDict, dict), \
            "curveMorphismDict should be a Dictionary[domain.vertices, codomain.vertices]."
        assert isinstance(monoidMorphism, MonoidHomomorphism), "monoidMorphism should be a MonoidHomomorphism."
        assert monoidMorphism.domain == domain.monoid, \
            "The domain of the monoid morphism should match the given domain."
        assert monoidMorphism.codomain == codomain.monoid, \
            "The codomain of the monoid morphism should match the given codomain."

        self.domain = domain
        self.codomain = codomain
        self.curveMorphismDict = curveMorphismDict
        self.monoidMorphism = monoidMorphism

        # Make sure that the given curveMorphismDict is actually a function from domain to codomain...
        assert set(curveMorphismDict.keys()) == domain.vertices | domain.edges | domain.legs, \
            "The keys of curveMorphismDict should be the vertices, edges, and legs of the domain curve."
        for vert in domain.vertices:
            assert curveMorphismDict[vert] in codomain.vertices, \
                "curveMorphismDict should map vertices to vertices of the codomain curve."
        for nextEdge in domain.edges:
            assert curveMorphismDict[nextEdge] in codomain.vertices | codomain.edges, \
                "curveMorphismDict should map edges to vertices or edges of the codomain curve."
        for nextLeg in domain.legs:
            assert curveMorphismDict[nextLeg] in codomain.legs, \
                "curveMorphismDict should map legs to legs of the codomain curve."

        # Make sure that the given curveMorphismDict is actually a homomorphism...
        for nextLeg in domain.legs:
            assert curveMorphismDict[nextLeg.root] == curveMorphismDict[nextLeg].root, \
                "curveMorphismDict should preserve leg roots."
        for nextEdge in domain.edges:
            if curveMorphismDict[nextEdge] in codomain.edges:
                assert set(map(lambda v: curveMorphismDict[v], nextEdge.vertices)) == curveMorphismDict[nextEdge].vertices, \
                    "curveMorphismDict should preserve endpoints of non-collapsed edges."
                assert monoidMorphism(nextEdge.length) == curveMorphismDict[nextEdge].length, \
                    "curveMorphismDict and monoidMorphism should be compatible on edge lengths."
            if curveMorphismDict[nextEdge] in codomain.vertices:
                assert curveMorphismDict[nextEdge] == curveMorphismDict[nextEdge.vert1] and \
                    curveMorphismDict[nextEdge] == curveMorphismDict[nextEdge.vert2], \
                    "curveMorphismDict should preserve endpoints of collapsed edges."
                assert monoidMorphism(nextEdge.length) == codomain.monoid.zero(), \
                    "curveMorphismDict and monoidMorphism should be compatible on edge lengths."
        for vert in codomain.vertices:
            assert self.preimage(vert).genus == vert.genus, \
                "curveMorphismDict should preserve genus."

    # Returns the preimage of the given vertex as a BasicFamily
    def preimage(self, vert):
        assert vert in self.codomain.vertices, "vert should be a codomain vertex"

        preimageVertices = {v for v in self.domain.vertices if self.curveMorphismDict[v] == vert}
        preimageEdges = {e for e in self.domain.edges if self.curveMorphismDict[e] == vert}

        preimage = BasicFamily("Preimage of " + vert.name)
        preimage.addEdges(preimageEdges)
        preimage.addVertices(preimageVertices)

        return preimage

    # Returns the image of the morphism as a BasicFamily
    def image(self):

        # Note that we don't need to worry about edges that collapse to a vertex - their endpoints go to the same place.
        imageVertices = {self(v) for v in self.domain.vertices}

        # Only take edges that are not collapsed
        imageEdges = {self(e) for e in self.domain.edges if self(e) in self.codomain.edges}

        imageLegs = {self(nextLeg) for nextLeg in self.domain.legs}

        # Keep the whole codomain monoid. Another option is to take the image of self.monoidMorphism, but this has not
        # yet been implemented.
        imageMonoid = self.codomain.monoid

        image = BasicFamily("Image curve")

        image.addVertices(imageVertices)
        image.addEdges(imageEdges)
        image.addLegs(imageLegs)
        image.monoid = imageMonoid

        return image

    def __call__(self, x):
        if isinstance(x, Vertex):
            assert x in self.domain.vertices, "The given input must be a domain vertex."
            return self.curveMorphismDict[x]
        elif isinstance(x, Edge):
            assert x in self.domain.edges, "The given input must be a domain edge."
            return self.curveMorphismDict[x]
        elif isinstance(x, Leg):
            assert x in self.domain.legs, "The given input must be a domain leg."
            return self.curveMorphismDict[x]
        elif isinstance(x, self.domain.monoid.Element):
            return self.monoidMorphism(x)
        else:
            raise ValueError("Cannot call on the given input - not a reasonable type.")
