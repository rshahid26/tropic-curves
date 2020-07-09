from .BasicFamily import BasicFamily
from .RPC import MonoidHomomorphism
from .Vertex import Vertex
from .Edge import Edge
from .Leg import Leg
from .GraphIsoHelper import *
import itertools


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
                assert set(map(lambda v: curveMorphismDict[v], nextEdge.vertices)) == curveMorphismDict[
                    nextEdge].vertices, \
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

    # Converts an isomorphism of pure graphs into a set of isomorphisms of basic families
    # This is done by incorporating edge lengths and leg marking
    @staticmethod
    def _getFamilyMorphisms(domainFamily, codomainFamily, pureGraphIso):

        assert isinstance(domainFamily, BasicFamily)
        assert isinstance(codomainFamily, BasicFamily)

        assert isinstance(pureGraphIso, dict)
        assert set(pureGraphIso.keys()) == domainFamily.vertices
        assert set(pureGraphIso.values()) == codomainFamily.vertices

        # Make sure that the given pure graph iso preserves leg marking
        for leg in domainFamily.legs:
            mappedRoot = pureGraphIso[leg.root]
            candidateLegs = {x for x in codomainFamily.legs if x.root == mappedRoot and x.marking == leg.marking}
            if len(candidateLegs) == 0:
                return set()

        # Any choice function from this dict will determine an isomorphism of basic families
        partialIsomorphisms = {}

        for v1, v2 in itertools.product(domainFamily.vertices, domainFamily.vertices):
            # Set of edges connecting v1 and v2
            domainConnections = {e for e in domainFamily.edges if e.vertices == {v1, v2}}

            # Set of edges connecting the images of v1 and v2
            codomainConnections = {e for e in codomainFamily.edges if
                                   e.vertices == {pureGraphIso[v1], pureGraphIso[v2]}}

            # Record the lengths of the connections
            domConByLength = {e: e.length for e in domainConnections}
            codomConByLength = {e: e.length for e in codomainConnections}

            # Get the set of all bijections from domainConnections to codomainConnections that preserve length
            lengthPreservingBijections = GraphIsoHelper.getFilteredBijections(domConByLength, codomConByLength)
            partialIsomorphisms[{v1, v2}] = lengthPreservingBijections

        # Can't form any choice functions if one of our sets is empty
        if set() in partialIsomorphisms:
            return set()

        # We now need to form the set of all choice functions / product...
        # Helps convert partialIsomorphisms, which has type Set[Vertex] => (Edge => Edge), into a value of type
        # Set[Edge => Edge]. Any choice function for image(partialIsomorphisms) is essentially a function Edge => Edge,
        # and we collect all such things into a set.
        def _getProductDictionary(current, remaining):
            # Assert that current has type Set[Edge => Edge] (too lazy to check more refined type)
            assert isinstance(current, set)
            assert all(map(lambda x: isinstance(x, dict), current))

            # Assert that remaining has type Set[???] => Set[??? => ???] (too lazy to check more refined type)
            # Supposed to be Set[Vertex] => Set[Edge => Edge]
            assert isinstance(remaining, dict)
            assert all(map(lambda x: isinstance(x, set), remaining.keys()))
            assert all(map(lambda x: isinstance(x, set), remaining.values()))
            assert all(map(lambda x: all(map(lambda y: isinstance(y, dict), x)), remaining.values()))
            for x in remaining.values():
                assert all(map(lambda y: isinstance(y, dict), x))

            if len(remaining) == 0:
                return current

            # This will become a Set[Edge => Edge]
            newFunctions = set()

            # partsToAssimilate is a Set[Edge => Edge]
            keyToPop = list(remaining.keys())[0]
            partsToAssimilate = remaining.pop(keyToPop)

            for func in current:
                for newPart in partsToAssimilate:
                    newFunc = {}
                    for x in func:
                        newFunc[x] = func[x]
                    for x in newPart:
                        newFunc[x] = newPart[x]
                    newFunctions.add(newFunc)

            return _getProductDictionary(newFunctions, remaining)

        edgeIsos = _getProductDictionary(set({}), partialIsomorphisms)

        basicFamilyIsos = set()
        for edgeIso in edgeIsos:
            curveMorphismDict = {}

            for vertex in domainFamily.vertices:
                curveMorphismDict[vertex] = pureGraphIso[vertex]

            for edge in domainFamily.edges:
                curveMorphismDict[edge] = edgeIso[edge]

            for leg in domainFamily.legs:
                mappedRoot = pureGraphIso[leg.root]
                candidateLegs = {x for x in codomainFamily.legs if x.root == mappedRoot and x.marking == leg.marking}
                curveMorphismDict[leg] = candidateLegs.pop()

            basicFamilyIsos.add(BasicFamilyMorphism(domainFamily, codomainFamily, curveMorphismDict, ?????))

        pass

    @staticmethod
    def getIsomorphismsIter(domainFamily, codomainFamily):
        assert isinstance(domainFamily, BasicFamily)
        assert isinstance(codomainFamily, BasicFamily)

        pureGraphIsos = GraphIsoHelper.getIsomorphismsIter(domainFamily, codomainFamily)
        unflattenedBFIsos = map(lambda x: BasicFamilyMorphism._getFamilyMorphisms(domainFamily, codomainFamily, x),
                                pureGraphIsos)

        # Flatten the Set[Set[BasicFamily Isomorphism]] into a Set[Basic Family Isomorphism]]
        basicFamilyIsos = set()
        for s in unflattenedBFIsos:
            basicFamilyIsos |= s

        return basicFamilyIsos

    @staticmethod
    def getAutomorphismsIter(basicFamily):
        assert isinstance(basicFamily, BasicFamily)

        return BasicFamilyMorphism.getIsomorphismsIter(basicFamily, basicFamily)

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
