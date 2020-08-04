import itertools
from typing import Dict, Iterator, List, TypeVar

from .BasicFamily import BasicFamily
from .Vertex import Vertex

VertexMap = Dict[Vertex, Vertex]
A = TypeVar("A")
B = TypeVar("B")
S = TypeVar("S")


class GraphIsoHelper(object):

    @staticmethod
    def getPermutations(lst: List[A]) -> List[List[A]]:
        """Returns the list of all permutations of the input list.

        A "permutation" of a list ``lst`` is any list with the same elements as ``lst``, but perhaps with a different
        order.

        Parameters
        ----------
        lst : List[A]
            The list of which to calculate permutations.

        Returns
        -------
        List[List[A]]
            The list of all permutations of ``lst``.
        """

        # If lst is empty then there are no permutations
        if len(lst) == 0:
            return []

        # If there is only one element in lst then, only one permutation is possible
        if len(lst) == 1:
            return [lst]

        # Find the permutations for lst if there are more than 1 characters

        perms = []  # empty list that will store current permutation

        # Iterate the input(lst) and calculate the permutation
        for i in range(len(lst)):
            m = lst[i]

            # Extract lst[i] or m from the list.  remLst is
            # remaining list
            remLst = lst[:i] + lst[i + 1:]

            # Generating all permutations where m is first
            # element
            for p in GraphIsoHelper.getPermutations(remLst):
                perms.append([m] + p)
        return perms

    # Given a function permDict: A -> Powerset(B), returns a list of all
    # functions of the form c \circ permDict: A \to B such that...
    # 1. c is a choice function for image(permDict)
    # 2. c \circ permDict is a bijection
    # Intended type of this function is (A => List[B]) => List[A => B]
    @staticmethod
    def getBijections(candidates: Dict[A, List[B]]) -> List[Dict[A, B]]:
        """Returns a list of all bijections compatible with ``candidates``.

        For a function ``f`` to be compatible with ``candidates``, we mean there exists a function ``c`` such
        that
        * ``c`` is a choice function for the image of ``candidates``, and
        * ``f`` is the composition of ``c`` with ``candidates``.
        This function collects all compatible bijections into a list and returns them.

        Parameters
        ----------
        candidates : Dict[A, List[B]]
            The function determining compatible bijections.

        Returns
        -------
        List[Dict[A, B]]
            A list of all bijections compatible with ``candidates``.
        """

        if len(candidates) == 0:
            return [{}]

        # Choose an input to process at this stage of recursion
        nextInput = list(candidates.keys())[0]
        candidateValues: List[B] = candidates.pop(nextInput)

        # Process the rest of the inputs
        partialFunctions: List[Dict[A, B]] = GraphIsoHelper.getBijections(candidates)

        # Start incorporating our chosen input into what we've already processed

        # Successful combinations of ``partialFunctions`` with choices from our ``candidateValues`` for ``nextInput``
        expandedFunctions: List[Dict[A, B]] = []

        for funcVal in candidateValues:
            for partialFunc in partialFunctions:
                # ``nextInput |-> funcVal`` is compatible only if ``funcVal`` has not already been used by
                # ``partialFunc``. We may throw away this partial function in higher recursion steps, but for now
                # it's a safe choice.
                if funcVal not in partialFunc.values():
                    # Take the union of {nextInput: funcVal} and partialFunc
                    expandedFunction: Dict[A, B] = {nextInput: funcVal}
                    for k in partialFunc:
                        expandedFunction[k] = partialFunc[k]

                    expandedFunctions.append(expandedFunction)

        return expandedFunctions

    # Given functions a: A -> S and b: B -> S such that...
    # 1. a and b are surjections, and
    # 2. |A| = |B|,
    # this method produces a list of all bijections f: A -> B such that b \circ f = a.
    @staticmethod
    def getFilteredBijections(a: Dict[A, S], b: Dict[B, S]) -> List[Dict[A, B]]:
        """Returns a list of all bijections filtered by ``a`` and ``b``.

        For a function ``f`` to be filtered by ``a`` and ``b``, we mean that the composition of ``b`` with ``f``
        equals ``a``. For example, if ``a`` and ``b`` are functions mapping edges to their length, then any bijection
        filtered by ``a`` and ``b`` preserves edge length.

        Parameters
        ----------
        a : Dict[A, S]
            A function associating data to domain values.
        b : Dict[B, S]
            A function associating data to codomain values.

        Returns
        -------
        List[Dict[A, B]]
            A list of all bijections filtered by ``a`` and ``b``.
        """

        # Runtime type checking
        assert isinstance(a, dict)
        assert isinstance(b, dict)

        # Ensure that ``a`` and ``b`` have the same image (good enough substitution for surjectivity)
        if set(a.values()) != set(b.values()):
            return []

        # Ensure that there are any bijections at all
        domA = set(a.keys())
        domB = set(b.keys())
        if len(domA) != len(domB):
            return []

        # Prepare the preimage of B for use with ``getBijections``
        preimageOfB: Dict[S, List[B]] = {}
        for v in b.values():
            preimageOfB[v] = [k for k in b if b[k] == v]

        # Compose the preimage of b with a
        # This maps from A to Powerset(B)
        candidates = {k: preimageOfB[a[k]] for k in a}

        return GraphIsoHelper.getBijections(candidates)

    # Checks if a bijection: domain.vertices -> codomain.vertices is an isomorphism
    @staticmethod
    def checkIfBijectionIsIsomorphism(
            domain: BasicFamily,
            codomain: BasicFamily,
            bijection: VertexMap) -> bool:
        """Determines whether or not a supplied map of vertices is an isomorphism of pure graphs.

        Parameters
        ----------
        domain : BasicFamily
            The desired domain.
        codomain : BasicFamily
            The desired codomain.
        bijection : Dict[Vertex, Vertex]
            The bijection to be tested.

        Returns
        -------
        bool
            Whether or not ``bijection`` is an isomorphism of pure graphs with domain ``domain``
            and codomain ``codomain``.
        """

        # print("Checking input list: ", [v.name for v in inputList])
        # print("With corresponding output list: ", [v.name for v in outputList])

        for v1, v2 in itertools.product(bijection, bijection):
            numInputEdges = sum(1 for e in domain.edges if e.vertices == {v1, v2})
            numOutputEdges = sum(1 for e in codomain.edges if e.vertices == {bijection[v1], bijection[v2]})
            if numInputEdges != numOutputEdges:
                # print("Function does not preserve number of connecting edges")
                return False

        for v in bijection:
            if v.genus != bijection[v].genus:
                return False
            numInputLegs = sum(1 for leg in domain.legs if leg.root == v)
            numOutputLegs = sum(1 for leg in codomain.legs if leg.root == bijection[v])
            if numInputLegs != numOutputLegs:
                # print("Function does not preserve number of legs")
                return False

        # print("This was an isomorphism!")
        return True

    @staticmethod
    def getIsomorphismsIter(domain: BasicFamily, codomain: BasicFamily) -> Iterator[VertexMap]:
        """Returns an iterator of all isomorphisms from ``domain`` to ``codomain``.

        The isomorphisms are encoded as vertex maps. All bijections from ``domain`` to ``codomain`` (filtered by vertex
        characteristic) are computed at the time of calling, but the isomorphism check is only performed when the
        iterator produces elements.

        Parameters
        ----------
        domain : BasicFamily
        codomain : BasicFamily

        Returns
        -------
        Iterator[Dict[Vertex, Vertex]]
            An iterator of all isomorphisms from ``domain`` to ``codomain``.
        """

        assert isinstance(domain, BasicFamily)
        assert isinstance(codomain, BasicFamily)

        domainVertexInfo = {v: domain.getCharacteristicOfVertex(v) for v in domain.vertices}
        codomainVertexInfo = {v: codomain.getCharacteristicOfVertex(v) for v in codomain.vertices}
        bijections: List[VertexMap] = GraphIsoHelper.getFilteredBijections(domainVertexInfo, codomainVertexInfo)

        return filter(lambda x: GraphIsoHelper.checkIfBijectionIsIsomorphism(domain, codomain, x), bijections)

    @staticmethod
    def isBruteForceIsomorphicTo(domain: BasicFamily, codomain: BasicFamily) -> bool:
        """Checks by brute force whether or not ``domain`` is isomorphic (as a pure graph) to ``codomain``.

        Produces all bijections from ``domain`` to ``codomain`` (filtered by vertex characteristic)
        and then checks whether or not any of the bijections are isomorphisms.

        Parameters
        ----------
        domain : BasicFamily
        codomain : BasicFamily

        Returns
        -------
        bool
            Whether or not the given families are isomorphic.
        """

        for _ in GraphIsoHelper.getIsomorphismsIter(domain, codomain):
            return True
        return False

    @staticmethod
    def isIsomorphicTo(domain: BasicFamily, codomain: BasicFamily) -> bool:
        """Checks whether or not ``domain`` is isomorphic (as a pure graph) to ``codomain``.

        This function first checks the following heuristics in order:
        * The number of edges of each family.
        * The number of vertices of each family.
        * The number of vertices of each characteristic. See
            :func:`~Tropical2020.basic_families.BasicFamily.BasicFamily.getCharacteristicOfVertex`.
        If all such tests fail, then the function checks, by brute force, whether any bijection filtered by
        vertex characteristic is an isomorphism of pure graphs.

        Parameters
        ----------
        domain : BasicFamily
        codomain : BasicFamily

        Returns
        -------
        bool
            Whether or not the given families are isomorphic.
        """

        if domain.numEdges != codomain.numEdges:
            # print("Different Number of Edges")
            return False

        if domain.numVertices != codomain.numVertices:
            # print("Different Number of Vertices")
            return False

        if domain.vertexCharacteristicCounts != codomain.vertexCharacteristicCounts:
            # print("Different counts of vertices with a given number of legs, edges, and genus")
            # print(self.getVerticesByEverything())
            # print(other.getVerticesByEverything())
            # print(self.vertexEverythingDict)
            # print(other.vertexEverythingDict)
            return False

        # print("Easy tests were inconclusive - switching to brute force")
        return domain.isBruteForceIsomorphicTo(codomain)
