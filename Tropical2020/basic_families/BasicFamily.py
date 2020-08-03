import itertools
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

import numpy as np  # type: ignore

from .RPC import *
from .Edge import Edge
from .Leg import Leg
from .Vertex import Vertex

VertexCharacteristic = Tuple[int, int, int, int]


# A Combinatorial Tropical Curve has a name, set of edges, and set of legs
class BasicFamily(object):
    """Represents a basic family of combinatorial tropical curves.

    Attributes
    ----------
    name : str
        An identifier for the family.
    monoid : :class:`~Tropical2020.basic_families.RPC.Monoid`
        A monoid from which the edge lengths of the family are taken.
    """

    # name_ should be a string identifier - only unique if the user is careful (or lucky) to make it so
    def __init__(self, name_: str) -> None:
        """
        Parameters
        ----------
        name_ : str
            An identifier for the family.
        """

        self.name: str = name_
        self._vertices: Set[Vertex] = set()
        self._edges: Set[Edge] = set()
        self._legs: Set[Leg] = set()
        self.monoid: Monoid = Monoid()

        # Variables for caching vertices
        self._vertexCacheValid: bool = False
        self._vertexCache: Set[Vertex] = set()

        # Variables for caching genus
        self._genusCacheValid: bool = False
        self._genusCache: int = 0

        # Variables for caching vertex characteristic counts
        self._vertexCharacteristicCacheValid: bool = False
        self._vertexCharacteristicCache: Dict[VertexCharacteristic, int] = {}

        # Variables for caching the core
        self._coreCacheValid: bool = False
        self._coreCache: Optional[BasicFamily] = None

    def invalidateCaches(self) -> None:
        """Invalidates the vertex, genus, characteristic, and core caches"""

        self._vertexCacheValid = False
        self._genusCacheValid = False
        self._vertexCharacteristicCacheValid = False
        self._coreCacheValid = False

    # The set of vertices is a read only property computed upon access, unless a valid cache is available
    # It is the collection of vertices that are endpoints of edges or roots of legs
    @property
    def vertices(self) -> Set[Vertex]:
        """Holds a set of :class:`~Tropical2020.basic_families.Vertex.Vertex` instances.

        The vertices in a basic family can not be modified without considering the edges and
        legs of the family, so we control how they are get and set.
        """

        return self._vertices

    def addVertex(self, v: Vertex) -> None:
        """Adds the specified vertex if it is not ``None``.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex to be added.
        """

        if v is not None:
            self._vertices.add(v)

            # Possibly need to recalculate genus/core/etc.
            self.invalidateCaches()

    def addVertices(self, vertices: Set[Vertex]) -> None:
        """Adds the given set of vertices.

        This function adds vertices by making a call to :func:`~addVertex` on each element of the vertices
        parameter. This means that if ``None`` belongs to ``vertices``, then it will be skipped.

        Parameters
        ----------
        vertices : set
            The set of :class:`~Tropical2020.basic_families.Vertex` instances to be added.
        """

        assert all(map(lambda x: isinstance(x, Vertex), vertices)), "vertices should be a set[Vertex]"
        for v in copy.copy(vertices):
            self.addVertex(v)

    def removeVertex(self, v: Vertex, removeDanglingVertices: bool = False) -> None:
        """Removes a vertex and all connected edges/legs.

        This function removes the specified vertex directly and removes connected edges and legs
        by making calls to :func:`~removeEdge` and :func:`~removeLeg`.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex to be removed.
        removeDanglingVertices : bool, optional
            Whether or not to remove dangling vertices - used by :func:`~removeEdge`.
        """

        if v in self._vertices:
            self._vertices.remove(v)

            # Removing a vertex removes all connected legs and edges
            for e in {e for e in self.edges if v in e.vertices}:
                self.removeEdge(e, removeDanglingVertices)
            for nextLeg in {nextLeg for nextLeg in self.legs if v in nextLeg.vertices}:
                self.removeLeg(nextLeg)

            # Possibly need to recalculate genus/core/etc.
            self.invalidateCaches()

    def removeVertices(self, vertices: Set[Vertex]) -> None:
        """Removes a set of vertices.

        This function removes the vertices in ``vertices`` by making calls to :func:`~removeVertex`.

        Parameters
        ----------
        vertices : set
            The set of :class:`~Tropical2020.basic_families.Vertex.Vertex` instanced to remove.
        """

        for v in copy.copy(vertices):
            self.removeVertex(v)

    @property
    def edges(self) -> Set[Edge]:
        """Holds a set of :class:`~Tropical2020.basic_families.Edge.Edge` instances.

        The edges in a basic family can not be modified without considering the vertices and
        legs of the family, so we control how they are get and set.
        """

        return self._edges

    # Control how edges are set
    @edges.setter
    def edges(self, edges_: Set[Edge]) -> None:
        """Sets the specified edges and invalidates caches.

        Parameters
        ----------
        edges_ : set
        """

        assert all(map(lambda x: isinstance(x, Edge), edges_)), "Every element of `edges_` must be an edge."

        self._edges = edges_
        self.invalidateCaches()

    @property
    def edgesWithVertices(self) -> Set[Edge]:
        """The set of edges for which neither endpoint is `None`.
        """

        return {e for e in self.edges if not (e.vert1 is None or e.vert2 is None)}

    def addEdge(self, e: Edge) -> None:
        """Adds the specified edge and its endpoints, and invalidates caches.

        Parameters
        ----------
        e : :class:`~Tropical2020.basic_families.Edge.Edge`
            The edge to be added.
        """

        self._edges.add(e)
        self.addVertices(e.vertices)

        # Possibly need to recalculate genus/core/etc.
        self.invalidateCaches()

    def addEdges(self, edges: Set[Edge]) -> None:
        """Adds each edge in the given set.

        Calls `addEdge` on each edge in ``edges``.

        Parameters
        ----------
        edges : set
            The set of :class"`Tropical2020.basic_families.Edge.Edge` instances to be added.
        """

        for e in copy.copy(edges):
            self.addEdge(e)

    def removeEdge(self, e: Edge, removeDanglingVertices: bool = True) -> None:
        """Removes the specified edge.

        Optionally, if ``removeDanglingVertices`` is set to ``True``, then after edge ``e`` is
        removed, any vertex of degree zero will also be removed. Also invalidates caches.

        Parameters
        ----------
        e : :class:`~Tropical2020.basic_families.Edge.Edge`
            The edge to be removed.
        removeDanglingVertices : bool
            Whether or not to also remove dangling vertices after ``e`` is removed.
        """

        if e in self._edges:
            self._edges.remove(e)

            # A "dangling vertex" is an endpoint of e is isolated after we remove edge e
            # By default, removing an edge removes such vertices
            if removeDanglingVertices:
                for v in e.vertices:
                    if self.degree(v) == 0:
                        self.removeVertex(v)

            # Possibly need to recalculate genus/core/etc.
            self.invalidateCaches()

    def removeEdges(self, edges: Set[Edge]) -> None:
        """Removes each edge in the given set.

        Makes a call to `removeEdge` on each element of ``edges``.

        Parameters
        ----------
        edges : set
            The set of edges to be removed.
        """

        for e in copy.copy(edges):
            self.removeEdge(e)

    @property
    def legs(self) -> Set[Leg]:
        """Holds a set of :class:`~Tropical2020.basic_families.Leg.Leg` instances.

        The legs in a basic family can not be modified without considering the vertices and
        edges of the family, so we control how they are get and set.
        """

        return self._legs

    # Control how legs are set
    @legs.setter
    def legs(self, legs_: Set[Leg]) -> None:
        """Updates the legs property to the supplied set and invalidates caches.
        """

        self._legs = legs_

        # Possibly need to recalculate genus/core/etc.
        self.invalidateCaches()

    @property
    def legsWithVertices(self) -> Set[Leg]:
        """The set of legs whose root is not `None`.
        """

        return {nextLeg for nextLeg in self.legs if nextLeg.root is not None}

    def addLeg(self, newLeg: Leg) -> None:
        """Adds the supplied leg and its root and invalidates caches.

        Parameters
        ----------
        newLeg : :class:`~Tropical2020.basic_families.Leg.Leg`
            The leg to be added.
        """

        self._legs.add(newLeg)
        self.addVertices(newLeg.vertices)

        # Possibly need to recalculate genus/core/etc.
        self.invalidateCaches()

    def addLegs(self, newLegs: Set[Leg]) -> None:
        """Adds each of the specified legs by making calls to :func:`addLeg`.

        Parameters
        ----------
        newLegs : set
            The legs to be added.
        """

        for newLeg in copy.copy(newLegs):
            self.addLeg(newLeg)

    def removeLeg(self, leg: Leg, removeDanglingVertices: bool = True) -> None:
        """Removes the specified leg.

        Optionally, if ``removeDanglingVertices`` is set to ``True``, then after edge ``leg`` is
        removed, any vertex of degree zero will also be removed. Also invalidates caches.

        Parameters
        ----------
        leg : :class:`~Tropical2020.basic_families.Leg.Leg`
            The leg to be removed.
        removeDanglingVertices : bool
            Whether or not to also remove dangling vertices after ``leg`` is removed.
        """

        if leg in self._legs:
            self._legs.remove(leg)

            # The root of a leg is "dangling" if it becomes isolated after removing the leg
            # By default, removing a leg removes such a vertex
            if removeDanglingVertices:
                for v in leg.vertices:
                    if self.degree(v) == 0:
                        self.removeVertex(v)

            # Possibly need to recalculate genus/core/etc.
            self.invalidateCaches()

    def removeLegs(self, legs: Set[Leg]) -> None:
        """Removes each leg in the given set.

        Makes a call to :func:`removeLeg` on each element of ``legs``.

        Parameters
        ----------
        legs : set
            The set of legs to be removed.
        """

        for badLeg in copy.copy(legs):
            self.removeLeg(badLeg)

    @property
    def numVertices(self) -> int:
        """The number of vertices in the basic family.
        """

        return len(self.vertices)

    @property
    def numEdges(self) -> int:
        """The number of edges in the basic family.
        """

        return len(self.edges)

    @property
    def numEdgesWithVertices(self) -> int:
        """The number of edges with both endpoints in the basic family.
        """

        return len(self.edgesWithVertices)

    # The Betti number is a read only property computed upon access
    @property
    def bettiNumber(self) -> int:
        """The Betti number of the curve (computed on access).

        This is computed as the number of edges (with vertices),
        minus the number of vertices, plus one.

        Returns
        -------
        int
            The Betti number of the curve.
        """

        return self.numEdgesWithVertices - self.numVertices + 1

    @property
    def genus(self) -> int:
        """The (possibly cached) genus of the curve.

        This is computed as the :func:`Betti number <bettiNumber>` of the curve plus
        the genuses of each vertex. If a cached copy of the genus is available, then
        it is used. Otherwise, a new value is computed and cached.

        Returns
        -------
        int
            The genus of the curve.
        """

        # If the cached copy of genus is invalid, then recalculate it
        if not self._genusCacheValid:
            self._genusCache = self.bettiNumber + sum([v.genus for v in self.vertices])
            self._genusCacheValid = True
        return self._genusCache

    # Returns the degree of vertex v accounting for legs and self loops
    def degree(self, v: Vertex) -> int:
        """The number of endpoints of edges and legs at ``v``.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex whose degree is to be computed.

        Returns
        -------
        int
            The degree of the supplied vertex.
        """

        return self.edgeDegree(v) + self.legDegree(v)

    # Returns the number of endpoints of finite edges at vertex v
    def edgeDegree(self, v: Vertex) -> int:
        """The number of endpoints of finite edges at ``v``.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex whose (edge) degree is to be computed.

        Returns
        -------
        int
            The (edge) degree of the supplied vertex.
        """

        return sum(1 for e in self.edges if e.vert1 == v) + sum(1 for e in self.edges if e.vert2 == v)

    # Returns the number of roots of legs at v
    def legDegree(self, v: Vertex) -> int:
        """The number of legs rooted at ``v``.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex whose (leg) degree is to be computed.

        Returns
        -------
        int
            The (leg) degree of the supplied vertex.
        """

        return sum(1 for attachedLeg in self.legs if attachedLeg.root == v)

    # Returns a copy of this curve where all vertices, edges, and legs are also copied shallowly
    def getFullyShallowCopy(self, returnCopyInfo: bool = False):
        """Returns a copy of this family where all vertices, edges, and legs are also copied.

        Creates and returns a fully shallow copy of this family. This means that all vertices,
        edges, and legs are also copied. If the optional parameter ``returnCopyInfo`` is
        set to ``True``, then some information about the copying is returned as well. Specifically,
        a dictionary is also returned whose keys are the vertices, edges, and legs of the original
        family, and the values are the copied versions of those vertices, edges, and legs.

        Parameters
        ----------
        returnCopyInfo : bool, optional
            Whether or not to track and return how the copying was performed.

        Returns
        -------
        Union[BasicFamily, (BasicFamily, Dict)]
            The copied family and optionally, the copy information.
        """

        # todo: Use the monoid copying function once it's written.

        # copyInfo will be a dictionary whose keys are the legs, edges, and vertices of self
        # copyInfo[*] will be the copy of *
        copyInfo: Dict[Union[Vertex, Leg, Edge], Union[Vertex, Leg, Edge]] = {}

        # First, copy the vertices of the graph and keep track of how it was done.
        # Even if the copy info is not returned, we need to know how vertices are copied to get compatible edge copies
        vertexCopyDict: Dict[Vertex, Vertex] = {}
        for v in self.vertices:
            vCopy = copy.copy(v)
            vertexCopyDict[v] = vCopy

            if returnCopyInfo:
                copyInfo[v] = vCopy

        # Next, copy edges and legs
        edgeCopies: Set[Edge] = set()
        for nextEdge in self.edges:
            # Keep the same name and length, but use the new versions of endpoints
            nextEdgeCopy = Edge(nextEdge.name, nextEdge.length,
                                vertexCopyDict[nextEdge.vert1], vertexCopyDict[nextEdge.vert2])
            edgeCopies.add(nextEdgeCopy)

            if returnCopyInfo:
                copyInfo[nextEdge] = nextEdgeCopy

        legCopies: Set[Leg] = set()
        for nextLeg in self.legs:
            # Keep the sane name, but use the new version of the root
            nextLegCopy = Leg(nextLeg.name, vertexCopyDict[nextLeg.root])
            legCopies.add(nextLegCopy)

            if returnCopyInfo:
                copyInfo[nextLeg] = nextLegCopy

        # Build the copy
        curveCopy = BasicFamily(self.name)
        curveCopy.addEdges(edgeCopies)
        curveCopy.addLegs(legCopies)
        curveCopy.monoid = copy.copy(self.monoid)

        if returnCopyInfo:
            return curveCopy, copyInfo
        else:
            return curveCopy

    # Contract edge e in place
    def contract(self, e: Edge) -> None:
        """Contracts an edge in place on the basic family.

        The assertion is made that the edge exists, else an error is raised.
        If the edge is a self loop, then the genus contribution of the loop will be placed in the new vertex.
        If the edge is NOT a self loop, then we have that the new vertex only bears the genus of the endpoints.

        Furthermore, each edge or leg adjacent to the edge has their endpoints moved to the contraction of the edge.

        Parameters
        ----------
        e : :class:`~Tropical2020.basic_families.Edge.Edge`
            The edge to be contracted.
        """

        # Don't contract a nonexistent edge
        assert e in self.edges

        genus: int
        if e.vert1 == e.vert2:
            # If e is a self loop, then the genus contribution of the loop will be placed in the new vertex
            genus = e.vert1.genus + 1
        else:
            # If e is not a self loop, then the new vertex only bears the genus of the endpoints
            genus = e.vert1.genus + e.vert2.genus

        v: Vertex = Vertex("(Contraction of " + e.name + ")", genus)

        # For each edge or leg adjacent to e, move endpoints to the contraction of e
        for nextEdge in copy.copy(self.edges) - {e}:
            if nextEdge.vert1 in e.vertices:
                nextEdge.vert1 = v
            if nextEdge.vert2 in e.vertices:
                nextEdge.vert2 = v
        for nextLeg in self.legs:
            if nextLeg.root in e.vertices:
                nextLeg.root = v

        # Apply the contraction
        self.addVertex(v)
        self.removeEdge(e)

    # Returns a new BasicFamily with edge e contracted
    def getContraction(self, e: Edge, returnCopyInfo: bool = False) -> Union["BasicFamily", Tuple["BasicFamily", Dict]]:
        """Returns a new BasicFamily with the edge ``e`` contracted.

        To avoid accidentally modifying self, we use a fully shallow copy.

        Parameters
        ----------
        e : :class:`~Tropical2020.basic_families.Edge.Edge`
            The edge to be contracted in the new BasicFamily.
        returnCopyInfo : bool (optional)
            Whether or not to track and return how the copying was performed.

        Returns
        -------
        BasicFamily, Dict (optional)
            The new basic family with ``e`` contracted and copyInfoDict (optional),
            a fully shallow copy of the basic family (self).
        """

        # To avoid accidentally modifying self, we work with a fully shallow copy
        contraction, copyInfoDict = self.getFullyShallowCopy(True)

        # Safely contract the copy in place
        contraction.contract(copyInfoDict[e])

        if returnCopyInfo:
            return contraction, copyInfoDict
        else:
            return contraction

    # Returns the set of all elements of the form (e, n), where e is an edge or leg, n is 1 or 2,
    # and the n^th endpoint of e is v
    def getEndpointsOfEdges(self, v: Vertex) -> Set[Tuple[Union[Leg, Edge], int]]:
        """This function returns the set of all elements of the form ``(e,n)`` where ``e`` is an edge or leg, ``n`` is
        1 or 2, and the ``n``th endpoint of ``e`` is ``v``.

        Parameters
        ----------
        v : :class:`~Tropical2020.basic_families.Vertex.Vertex`
            The vertex which will have edges calculated.

        Returns
        -------
        set
            The set of endpoints of edges at ``v``.
        """

        endpoints: List[Tuple[Union[Leg, Edge], int]] = []
        endpoints += [(edge, 1) for edge in self.edges if edge.vert1 == v]
        endpoints += [(edge, 2) for edge in self.edges if edge.vert2 == v]

        # By default, consider the root of a leg to be its first endpoint
        endpoints += [(leg, 1) for leg in self.legs if leg.root == v]

        return set(endpoints)

    def getCharacteristicOfVertex(self, v):
        edgeDegree = self.edgeDegree(v)
        legDegree = self.legDegree(v)
        g = v.genus
        loops = sum(1 for e in self.edges if e.vertices == {v})
        return edgeDegree, legDegree, g, loops

    # This dictionary keeps track of the number of vertices of a certain characteristic
    # Currently, the characteristic of a vertex v is a triple (d_e, d_l, g, l), where d_e is the edge degree of v,
    # d_l is the leg degree of v, and g is the genus of v, and there are l loops based at v.
    # The characteristic of a vertex is invariant under isomorphism, so if two graphs have different
    # "vertexEverythingDict"s, then they are definitely not isomorphic.
    @property
    def vertexCharacteristicCounts(self) -> Dict[VertexCharacteristic, int]:
        """Keeps track of the number of vertices of a certain characteristic.

        Currently, the characteristic of a vertex ``v`` is a triple ``(d_e, d_l, g, l)``, where ``d_e`` is the edge
        degree of ``v``, ``d_l`` is the leg degree of ``v``, and ``g`` is the genus of ``v``, and there are ``l`` loops
        based at ``v``.

        The characteristic of a vertex is invariant under isomorphism, so if two graphs have different
        results for ``vertexCharacteristicCounts``, then they are not isomorphic.

        Returns
        -------
        dict
            A dictionary where the keys are vertices of a certain characteristic
            and the values are the number of said vertices.
        """

        # If the cached copy of the dictionary is invalid, then recalculate it.
        if not self._vertexCharacteristicCacheValid:
            self._vertexCharacteristicCache = {}
            for v in self.vertices:
                key = self.getCharacteristicOfVertex(v)

                # Increase the count of that characteristic, or set it to 1 if not already seen
                if key in self._vertexCharacteristicCache:
                    self._vertexCharacteristicCache[key] += 1
                else:
                    self._vertexCharacteristicCache[key] = 1

            self._vertexCharacteristicCacheValid = True

        return self._vertexCharacteristicCache

    # Very similar to the vertexCharacteristicCounts. Returns a dictionary vertexDict defined as follows. The keys of
    # vertexDict are triples of integers (d_e, d_l, g, l), and vertexDict[(d_e, d_l, g)] is the list of all vertices
    # with edge degree d_e, leg degree d_l, genus g, and l loops based at that vertex.
    # The values of vertexDict form a partition of self.vertices and every value of vertexDict is nonempty.
    # When brute-force checking for an isomorphism between two graphs, we only need to check bijections that preserve
    # corresponding characteristic blocks. (i.e., reduce the number of things to check from n! to
    # (n_1)! * (n_2)! * ... * (n_k)!, where n = n_1 + ... + n_k)
    def getVerticesByCharacteristic(self) -> Dict[VertexCharacteristic, List[Vertex]]:
        vertexDict: Dict[VertexCharacteristic, List[Vertex]] = {}
        for v in self.vertices:
            key = self.getCharacteristicOfVertex(v)

            # Update that characteristic entry, or initialize it if not already present
            if key in vertexDict:
                vertexDict[key].append(v)
            else:
                vertexDict[key] = [v]
        return vertexDict

    # Returns the number of edges whose endpoints are indistinct. Invariant under isomorphism
    def getNumSelfLoops(self) -> int:
        return sum(1 for e in self.edges if len(e.vertices) == 1)

    # Returns a list of all permutations of lst. A permutation of lst is itself a list.
    def getPermutations(self, lst: List[Any]) -> List[List[Any]]:
        from .GraphIsoHelper import GraphIsoHelper
        return GraphIsoHelper.getPermutations(lst)

    # Checks if the given data constitutes an isomorphism from self to other.
    # domainOrderingDict and codomainOrderingDict should have the same keys, and their values should partition the
    # vertices of self and other with all blocks of the partitions nonempty. The bijection f recovered from this data
    # is as follows: for each key k, and each index of domainOrderingDict[k],
    # f(domainOrderingDict[k][i]) = codomainOrderingDict[k][i].
    #def checkIfBijectionIsIsomorphism(
    #        self,
    #        other: "BasicFamily",
    #        domainOrderingDict: Dict[Any, List[Vertex]],
    #        codomainOrderingDict: Dict[Any, List[Vertex]]) -> bool:
    #    return GraphIsoHelper.checkIfBijectionIsIsomorphism(self, other, domainOrderingDict, codomainOrderingDict)

    # permDict should have the property that for any choice function
    # f for the values of permDict, f(k_1) + ... + f(k_n) is a permutation of self.vertices, where k_1, ..., k_n are
    # the keys of permDict. Moreover, every permutation of self.vertices should arise in this manner.
    def getBijections(self, permDict: Dict[Any, List[List[Vertex]]]):
        from .GraphIsoHelper import GraphIsoHelper
        return GraphIsoHelper.getBijections(permDict)

    # Checks all bijections that preserve characteristic
    def isBruteForceIsomorphicTo(self, other: "BasicFamily") -> bool:
        from .GraphIsoHelper import GraphIsoHelper
        return GraphIsoHelper.isBruteForceIsomorphicTo(self, other)

    # Checks if some easy to check invariants are preserved, and then checks candidate bijections
    def isIsomorphicTo(self, other: "BasicFamily") -> bool:
        from .GraphIsoHelper import GraphIsoHelper
        return GraphIsoHelper.isIsomorphicTo(self, other)

    # Simplifies names of vertices, edges, and legs in place.
    def simplifyNames(self) -> None:
        orderedVertices = list(self.vertices)
        for i in range(len(orderedVertices)):
            orderedVertices[i].name = "v" + str(i)
        for e in self.edges:
            e.name = "edge(" + e.vert1.name + ", " + e.vert2.name + ")"
        for nextLeg in self.legs:
            nextLeg.name = "leg(" + nextLeg.root.name + ")"

    def showNumbers(self) -> None:
        print("Number of Vertices: ", self.numVertices, " Number of Edges: ", self.numEdges)

    @staticmethod
    def printCurve(curve: "BasicFamily") -> None:
        print("Vertices:")
        for v in curve.vertices:
            print(v.name, " with genus ", v.genus)
        print("Edges:")
        for e in curve.edges:
            print(e.name)
        print("Legs:")
        for nextLeg in curve.legs:
            print(nextLeg.name)

    def printSelf(self) -> None:
        BasicFamily.printCurve(self)

    # Prints the names of vertices
    def showVertices(self) -> None:
        print([v.name for v in self.vertices])

    # Prints the names of edges
    def showEdges(self) -> None:
        print([e.name for e in self.edges])

    # Prints the names of legs
    def showLegs(self) -> None:
        print([nextLeg.name for nextLeg in self.legs])

    # This function will check if the tropical curve is connected (in the style of Def 3.10)
    @property
    def isConnected(self) -> bool:
        """Computes whether or not the basic family is connected.

        This function computes the `connected component <https://en.wikipedia.org/wiki/Component_(graph_theory)>`_
        of an arbitrarily chosen vertex. The basic family is connected if and only if this connected component
        is the whole family.

        Returns
        -------
        bool
            ``True`` if the family is connected, ``False`` otherwise.
        """

        # Fix an ordering of the vertices
        vertex_list: List[Vertex] = list(self.vertices)

        # Construct the (symmetric) adjacency matrix ``A``
        A: np.ndarray = np.zeros((self.numVertices, self.numVertices))
        for edge in self.edges:
            i = vertex_list.index(edge.vert1)
            j = vertex_list.index(edge.vert2)

            # Record the connection
            A[i][j] = 1
            A[j][i] = 1

        # In order to test for connectedness, we start at an arbitrary vertex (in this case, whichever vertex has
        # index 0) and travel to any adjacent vertex that has not yet been visited. This continues until every vertex
        # in the connected component of the starting vertex has been visited.

        # Initialize the visited and new indices
        visitedVertexIndices: Set[int] = set()
        newIndices: Set[int] = {0}

        # While there are still new indices, visit them and search for more
        while newIndices:
            # Add the indices we found in the previous loop
            visitedVertexIndices |= newIndices

            # All potential connections from elements of ``newIndices`` to some other index
            possibleConnections: Iterator[Tuple[int, int]] = itertools.product(newIndices, range(self.numVertices))

            # Collect all indices that (1) are connected to some element of ``newIndices`` and (2) have not yet been
            # visited
            newIndices = {k for (i, k) in possibleConnections if k not in visitedVertexIndices and A[i][k]}

        # Compare the size of the connected component of the starting vertex to the total number of vertices. The
        # family is connected if and only if the connected component of the starting vertex is the whole family.
        return len(visitedVertexIndices) == self.numVertices

    @property
    def core(self) -> Optional["BasicFamily"]:

        # Calculate the core if our current copy is invalid
        if not self._coreCacheValid:

            # Only allow the core to be requested from curves where the core is defined.
            if not self.genus > 0:
                raise ValueError("The core is only defined for curves of positive genus.")
            if not self.isConnected:
                raise ValueError("The core is only defined for connected curves.")

            # In order to generate the core, we start with a copy of self and repeatedly prune off certain leaves
            core: BasicFamily = BasicFamily("(Core of " + self.name + ")")
            core.addEdges(self.edges)
            core.addVertices(self.vertices)

            # Flag to indicate whether new leaves were pruned
            keepChecking: bool = True

            while keepChecking:

                # If nothing happens this loop, then stop.
                keepChecking = False

                # Search for leaves to prune
                for nextVertex in copy.copy(core.vertices):
                    # A vertex is the endpoint of a leaf to prune if it is connected to exactly one edge and has
                    # genus zero
                    if nextVertex.genus == 0 and core.degree(nextVertex) < 2:
                        # Prune the leaf
                        core.removeVertex(nextVertex)
                        keepChecking = True

            # Save the new, valid, core and set the valid flag to true
            self._coreCache = core
            self._coreCacheValid = True

        # Return the saved copy of the core (possibly just calculated)
        return self._coreCache

    # Class to assist in reasoning about loops and spanning trees
    class Tree:
        def __init__(self):
            # Tree Parent
            self.parent = None
            # Edge connecting self to parent
            self.parentConnection = None
            # Node holds a vertex value
            self.value = None
            # List of (Tree, Edge) children
            self.children = []

        def setValue(self, vert: Vertex) -> None:
            self.value = vert

        def setParent(self, p) -> None:
            self.parent = p

        def addChild(self, vert: Vertex, connectingEdge: Edge) -> None:
            if (
                    # Don't allow a self loop to be added
                    (vert != self.value) and
                    # Make sure connectingEdge is actually a connecting edge
                    (connectingEdge.vertices == {self.value, vert}) and
                    # Don't introduce any loops
                    (vert not in self.getVertices())
            ):
                childTree = BasicFamily.Tree()
                childTree.setValue(vert)
                childTree.setParent(self)
                childTree.parentConnection = connectingEdge
                self.children.append((childTree, connectingEdge))

        def getEdgesOfChildren(self) -> list:
            edges = []
            for child in self.children:
                childTree, connectingEdge = child
                edges.append(connectingEdge)
                edges += childTree.getEdgesOfChildren()
            return edges

        def getEdges(self) -> list:
            # If we're actually the root of the whole tree, then descend recursively
            if self.parent is None:
                return self.getEdgesOfChildren()
            else:
                return self.parent.getEdges()

        def getVerticesFromChildren(self) -> set:
            vertices = {self.value}
            for child in self.children:
                childTree, connectingEdge = child
                vertices = vertices | childTree.getVerticesFromChildren()
            return vertices

        def getVertices(self) -> set:
            if self.parent is None:
                return self.getVerticesFromChildren()
            else:
                return self.parent.getVertices()

        def findVertexInChildren(self, vert: Vertex):
            if self.value == vert:
                return self
            else:
                for child in self.children:
                    childTree, connectingEdge = child
                    possibleFind = childTree.findVertexInChildren(vert)
                    if possibleFind is not None:
                        return possibleFind
                return None

        def findVertex(self, vert: Vertex):
            if self.parent is None:
                return self.findVertexInChildren(vert)
            else:
                return self.parent.findVertex(vert)

        def getAncestorEdges(self, vert: Vertex) -> list:
            currentTree = self.findVertex(vert)
            ancestorEdges = []

            while currentTree.parent is not None:
                ancestorEdges.append(currentTree.parentConnection)
                currentTree = currentTree.parent

            return ancestorEdges

    @property
    def spanningTree(self) -> Tree:
        return self.getSpanningTree(list(self.vertices)[0])

    # Will return a list of edges in a loop.
    def getLoop(self, e: Edge) -> List[Edge]:
        spanningTree = self.spanningTree
        if e in spanningTree.getEdges():
            raise ValueError("Edge " + e.name + " must not belong to the spanning tree to determine a unique loop.")

        anc1: List[Edge] = spanningTree.getAncestorEdges(e.vert1)
        anc2: List[Edge] = spanningTree.getAncestorEdges(e.vert2)

        leastAncestorIndex = 0
        for i in range(min(len(anc1), len(anc2))):
            leastAncestorIndex = i
            if anc1[i] != anc2[i]:
                break
        else:
            leastAncestorIndex = min(len(anc1), len(anc2))

        anc1 = anc1[leastAncestorIndex:]
        anc2 = anc2[leastAncestorIndex:]
        anc1.reverse()

        if anc1 == [None]:
            anc1 = []

        if anc2 == [None]:
            anc2 = []

        return anc1 + [e] + anc2

    @property
    def loops(self) -> List[List[Edge]]:
        loopDeterminers: Set[Edge] = self.edges - set(self.spanningTree.getEdges())
        _loops: List[List[Edge]] = []
        for nextEdge in loopDeterminers:
            _loops.append(self.getLoop(nextEdge))
        return _loops

    def getSpanningTree(self, vert: Vertex) -> Tree:
        
        if not self.isConnected:
            raise ValueError("A spanning tree is only defined for a connected graph")

        tree = self.Tree()          
        tree.setValue(vert)

        verticesToCheck: Set[Vertex] = {vert}

        while verticesToCheck:

            nextVertex: Vertex = verticesToCheck.pop()

            connectedEdges: Set[Edge] = {e for e in self.edges if (nextVertex == e.vert1 or nextVertex == e.vert2)}

            adjacentVertices: Set[Vertex] = set()

            for e in connectedEdges:
                adjacentVertices = adjacentVertices | e.vertices 

            newAdjacentVertices: Set[Vertex] = adjacentVertices - set(tree.getVertices())

            nextTree = tree.findVertex(nextVertex)    

            for v in newAdjacentVertices:
                connectingEdge = {e for e in self.edges if e.vertices == {nextVertex, v}}.pop()
                nextTree.addChild(v, connectingEdge)

            verticesToCheck = verticesToCheck | newAdjacentVertices

        return tree
