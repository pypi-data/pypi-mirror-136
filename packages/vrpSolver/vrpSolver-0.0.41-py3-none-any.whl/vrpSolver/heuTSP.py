import heapq
import math

from .const import *
from .common import *
from .graph import *
from .geometry import *

def lbTSP(
    nodes:      "Dictionary, returns the coordinate of given nodeID, \
                    {\
                        nodeID1: {'loc': (x, y)}, \
                        nodeID2: {'loc': (x, y)}, \
                        ... \
                    }" = None, 
    edges:      "1) String (default) 'Euclidean' or \
                 2) String 'LatLon' or \
                 3) Dictionary {(nodeID1, nodeID2): dist, ...}" = "Euclidean",
    nodeIDs:    "1) String (default) 'All', or \
                 2) A list of node IDs" = 'All',
    subgradM:   "Double" = 1,
    subgradRho: "Double, (0, 1)" = 0.95,
    stopType:   "1) String, (default) 'Epsilon' (`stopEpsilon` will be used) or \
                 2) String, 'IterationNum' (`stopK` will be used) or \
                 3) String, 'Runtime' (`stopTime` will be used)" = 'Epsilon',
    stopEpsilon:"Double, small number" = 0.01,
    stopK:      "Integer, large number" = 200,
    stopTime:   "Double, in seconds" = 600
    ) -> "Returns a Held & Karp lower bound of the TSP using Lagrangian Relaxation":

    # Define nodeIDs ==========================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = []
            for i in nodes:
                nodeIDs.append(i)

    # Define edges ============================================================
    if (type(edges) is not dict):
        if (edges == 'Euclidean'):
            edges = getTauEuclidean(nodes)
        elif (edges == 'LatLon'):
            edges = getTauLatLon(nodes)
        else:
            print("Error: Incorrect type `edges`")
            return None

    # Initialize ==============================================================
    k = 0
    u = [0 for i in range(len(nodeIDs))]
    d = None
    costSum = None
    L = None
    oldL = None

    # Calculate 1 tree ========================================================
    def _cal1Tree(weightArcs):
        # Separate first node
        arcsWithVertexOne = []
        arcsWithoutVertexOne = []
        for i in range(len(weightArcs)):
            if (weightArcs[i][0] == 0 or weightArcs[i][1] == 0):
                arcsWithVertexOne.append(weightArcs[i])
            else:
                arcsWithoutVertexOne.append(weightArcs[i])

        # MST for the rest of vertices
        mst = graphMST(
            weightArcs = arcsWithoutVertexOne
            )['mst']

        # Find two cheapest arcs to vertex one
        sortedArcswithVertexOne = []
        for i in range(len(arcsWithVertexOne)):
            heapq.heappush(sortedArcswithVertexOne, (arcsWithVertexOne[i][2], arcsWithVertexOne[i]))

        # Build 1-tree
        leastTwo = []
        leastTwo.append(heapq.heappop(sortedArcswithVertexOne))
        leastTwo.append(heapq.heappop(sortedArcswithVertexOne))

        m1t = [i for i in mst]
        m1t.append(leastTwo[0][1])
        m1t.append(leastTwo[1][1])

        # Calculate total cost
        costSum = 0
        for i in range(len(m1t)):
            costSum += m1t[i][2]

        # Arcs to neighbors
        neighbors = arcs2AdjList(m1t)
        d = []
        for i in range(len(nodeIDs)):
            d.append(2 - len(neighbors[i]))

        return {
            'costSum': costSum,
            'm1t': m1t,
            'd': d
        }

    # Main iteration ==========================================================
    continueFlag = True
    while (continueFlag):
        # Update cost of each edge
        weightArcs = []
        for i in range(len(nodeIDs)):
            for j in range(len(nodeIDs)):
                if (i != None and j != None and i < j):
                    weightArcs.append((i, j, edges[i, j] - u[i] - u[j]))

        # Calculate 1-tree
        oneTree = _cal1Tree(weightArcs)

        # Update L and d
        costSum = oneTree['costSum']
        m1t = oneTree['m1t']
        uSum = sum(u)
        if (L != None):
            oldL = L
        L = costSum + 2 * uSum
        d = oneTree['d']

        # update u
        oldU = [i for i in u]
        u = []
        eff = subgradM * math.pow(subgradRho, k)
        for i in range(len(nodeIDs)):
            u.append(oldU[i] + eff * d[i])

        # Check if continue
        def _allZero(d):
            for i in d:
                if (i != 0):
                    return False
            return True
        if (k >= stopK):
            continueFlag = False
        elif (oldL != None and abs(oldL - L) < stopEpsilon):
            continueFlag = False
        elif (_allZero(d)):
            continueFlag = False
        else:
            k += 1

    return {
        'lrLowerBound': costSum
    }

def heuTSP(
    nodes:      "Dictionary, returns the coordinate of given nodeID, \
                    {\
                        nodeID1: {'loc': (x, y)}, \
                        nodeID2: {'loc': (x, y)}, \
                        ... \
                    }" = None, 
    edges:      "1) String (default) 'Euclidean' or \
                 2) String 'LatLon' or \
                 3) Dictionary {(nodeID1, nodeID2): dist, ...}" = "Euclidean",
    depotID:    "DepotID, default to be 0" = 0,
    nodeIDs:    "1) String (default) 'All', or \
                 2) A list of node IDs" = 'All',
    serviceTime: "Service time spent on each customer (will be added into travel matrix)" = 0,
    consAlgo:   "1) String 'k-NearestNeighbor' or \
                 2) String 'FarthestNeighbor' or \
                 3) String (default) 'Insertion' or \
                 4) String 'Sweep' or \
                 5) String 'DepthFirst' or \
                 6) String 'Christofides' or \
                 7) String 'Random'" = 'Insertion',
    consAlgoArgs: "Dictionary, args for constructive heuristic" = None,
    enableLocalImproveFlag: "True if call local improvement to improve solution quality" = True,
    impAlgo:    "1) String (not available) 'LKH' or \
                 2) String (default) '2Opt' = '2Opt'" = '2Opt',
    impAlgoArgs: "Dictionary, args for improvement heuristic" = None,
    ) -> "Use given heuristic methods to get TSP solution":

    # Define nodeIDs ==========================================================
    if (type(nodeIDs) is not list):
        if (nodeIDs == 'All'):
            nodeIDs = []
            for i in nodes:
                nodeIDs.append(i)
        else:
            print(ERROR_INCOR_NODEIDS)
            return
            
    # Define edges ============================================================
    if (type(edges) is not dict):
        if (edges == 'Euclidean'):
            edges = getTauEuclidean(nodes)
        elif (edges == 'LatLon'):
            edges = getTauLatLon(nodes)
        else:
            print(ERROR_INCOR_TAU)
            return None

    # Service time ============================================================
    if (serviceTime != None and serviceTime > 0):
        for e in edges:
            if (e[0] != depotID and e[1] != depotID):
                edges[e] += serviceTime / 2
    else:
        serviceTime = 0

    # Constructive heuristic (with out specifying depot) ======================
    seq = _consTSP(
        nodes = nodes,
        edges = edges,
        nodeIDs = nodeIDs,
        algo = consAlgo,
        algoArgs = consAlgoArgs)

    # Local improvement heuristic (with out specifying depot) =================
    if (enableLocalImproveFlag):
        seq = _impTSP(
            nodes = nodes, 
            edges = edges, 
            initSeq = seq, 
            algo = impAlgo)

    # Fix the sequence to make it start from the depot ========================
    startIndex = None
    truckSeq = []
    for k in range(len(seq)):
        if (seq[k] == depotID):
            startIndex = k
    if (startIndex < len(seq) - 1):
        for k in range(startIndex, len(seq)):
            truckSeq.append(seq[k])
    if (startIndex > 0):
        for k in range(0, startIndex):
            truckSeq.append(seq[k])
    truckSeq.append(depotID)

    ofv = calSeqCostMatrix(edges, seq)

    return {
        'ofv': ofv,
        'seq': truckSeq,
        'serviceTime': serviceTime
    }

def _consTSP(
    nodes:      "Dictionary, returns the coordinate of given nodeID, \
                    {\
                        nodeID1: {'loc': (x, y)}, \
                        nodeID2: {'loc': (x, y)}, \
                        ... \
                    }" = None, 
    edges:      "Dictionary {(nodeID1, nodeID2): dist, ...}" = None,
    nodeIDs:    "A list of node IDs" = None,
    algo:       "1) String 'k-NearestNeighbor' or \
                 2) String 'FarthestNeighbor' or \
                 3) String (default) 'Insertion' or \
                 4) String (not available) 'Patching' or \
                 5) String 'Sweep' or \
                 6) String 'DepthFirst' or \
                 7) String 'Christofides' or \
                 8) String 'Random'" = 'Insertion',
    algoArgs:   "Dictionary, needed for some algorithm options, \
                 1) None for unspecified `algo` options, or \
                 2) for 'k-NearestNeighbor' \
                    {\
                        'k': k-th nearest neighbor\
                    } \
                 3) for 'Christofides' \
                    {\
                        'matchingAlgo': algorithm for finding minimum matching\
                    } \
                 4) for 'Insertion' \
                    {\
                        'initSeq': initial TSP route\
                    }"= None
    ) -> "Constructive heuristic solution for TSP, the output sequence does not necessarily start from depot":

    # Subroutines for different constructive heuristics =======================
    def _consTSPkNearestNeighbor(nodes, nodeIDs, edges, k = 1):
        seq = [nodeIDs[0]]
        remain = [nodeIDs[i] for i in range(1, len(nodeIDs))]

        # Accumulate seq ------------------------------------------------------
        while (len(remain) > 0):
            currentNodeID = seq[-1]
            sortedNodes = getSortedNodesByDist(
                nodes = nodes,
                edges = edges,
                nodeIDs = remain,
                refNodeID = currentNodeID)
            if (k > len(remain)):
                seq.append(sortedNodes[-1])
            else:
                seq.append(sortedNodes[k - 1])
            remain = [i for i in nodeIDs if i not in seq]
        seq.append(seq[0])
        return seq
    def _consTSPFarthestNeighbor(nodeIDs, edges):
        # Initialize ----------------------------------------------------------
        seq = [nodeIDs[0]]
        remain = [nodeIDs[i] for i in range(1, len(nodeIDs))]

        # Accumulate seq ------------------------------------------------------
        while (len(remain) > 0):
            nextLeng = None
            nextID = None
            for node in remain:
                if ((node, seq[-1]) in edges):
                    if (nextLeng == None or edges[node, seq[-1]] > nextLeng):
                        nextID = node
                        nextLeng = edges[node, seq[-1]]
                elif ((seq[-1], node) in edges):
                    if (nextLeng == None or edges[seq[-1], node] > nextLeng):
                        nextID = node
                        nextLeng = edges[seq[-1], node]
            seq.append(nextID)
            remain.remove(nextID)
        seq.append(seq[0])
        return seq
    def _consTSPSweep(nodes, nodeIDs, edges):
        # Sweep seq -----------------------------------------------------------
        sweepSeq = getSweepSeq(
            nodes = nodes, 
            nodeIDs = nodeIDs)
        sweepSeq.append(sweepSeq[0])
        return sweepSeq
    def _consTSPRandomSeq(nodeIDs, edges):
        # Get random seq ------------------------------------------------------
        seq = [i for i in nodeIDs]
        N = len(nodeIDs)
        for i in range(N):
            j = random.randint(0, N - 1)
            t = seq[i]
            seq[i] = seq[j]
            seq[j] = t
        seq.append(seq[0])
        return seq
    def _consTSPInsertion(nodeIDs, initSeq, edges):
        # Initialize ----------------------------------------------------------
        seq = None
        if (initSeq == None):
            seq = [nodeIDs[0], nodeIDs[0]]
        else:
            seq = [i for i in initSeq]
        insertDict = {}
        if (len(nodeIDs) < 1):
            return {
                'ofv': 0,
                'seq': None
            }
        unInserted = [i for i in nodeIDs if i not in seq]

        # Try insertion one by one --------------------------------------------
        while (len(unInserted) > 0):
            bestCus = None
            bestCost = None
            bestInsertionIndex = None
            for cus in unInserted:
                for i in range(1, len(seq)):
                    if (list2Tuple([seq[i - 1], cus, seq[i]]) not in insertDict):
                        insertDict[list2Tuple([seq[i - 1], cus, seq[i]])] = (
                            edges[seq[i - 1], cus] 
                            + edges[cus, seq[i]] 
                            - (edges[seq[i - 1], seq[i]] if seq[i - 1] != seq[i] else 0))
                    cost = insertDict[list2Tuple([seq[i - 1], cus, seq[i]])]
                    if (bestCost == None or bestCost > cost):
                        bestCost = cost
                        bestCus = cus
                        bestInsertionIndex = i
            if (bestCost != None):
                seq.insert(bestInsertionIndex, bestCus)
                unInserted.remove(bestCus)

        return seq

    # Heuristics that don't need to transform arc representation ==============
    seq = None
    if (algo == 'k-NearestNeighbor'):
        if (algoArgs == None):
            algoArgs = {'k': 1}
        seq = _consTSPkNearestNeighbor(nodes, nodeIDs, edges, algoArgs['k'])
    elif (algo == 'FarthestNeighbor'):
        seq = _consTSPFarthestNeighbor(nodeIDs, edges)
    elif (algo == 'Insertion'):
        if (algoArgs == None):
            algoArgs = {'initSeq': [nodeIDs[0], nodeIDs[0]]}
        seq = _consTSPInsertion(nodeIDs, algoArgs['initSeq'], edges)
    elif (algo == 'Sweep'):
        seq = _consTSPSweep(nodes, nodeIDs, edges)
    elif (algo == 'Random'):
        seq = _consTSPRandomSeq(nodeIDs, edges)
    else:
        pass
    if (seq != None):
        return seq

    # Create arcs =============================================================
    # FIXME! indexes of nodes starts from 0 here!
    # FIXME! Add mapping between 0 to n and nodeIDs
    weightArcs = []
    for (i, j) in edges:
        if (i != None and j != None and i < j):
            weightArcs.append((i, j, edges[i, j]))

    # Subroutines for different constructive heuristics =======================
    def _consTSPDepthFirst(weightArcs):
        # Create MST ----------------------------------------------------------
        mst = graphMST(weightArcs)['mst']

        # Seq of visit is the seq of Depth first search on the MST ------------
        seq = traversalGraph(mst)['seq']
        seq.append(seq[0])

        return seq
    def _consTSPChristofides(weightArcs, matchingAlgo):
        # Create MST ----------------------------------------------------------
        mst = graphMST(weightArcs)['mst']

        # Derive subgraph of odd degree vertices ------------------------------
        neighbors = arcs2AdjList(mst)
        oddDegrees = []
        for node in neighbors:
            if (len(neighbors[node]) % 2 != 0):
                oddDegrees.append(node)
        subGraph = []
        for arc in weightArcs:
            if (arc[0] in oddDegrees and arc[1] in oddDegrees):
                subGraph.append(arc)

        # Find minimum cost matching of the subgraph --------------------------
        minMatching = graphMatching(
            weightArcs=subGraph, 
            mType='Minimum', 
            algo=matchingAlgo)['matching']

        # Add them back to create a new graph ---------------------------------
        newGraph = []
        for arc in minMatching:
            newGraph.append(arc)
        for arc in mst:
            newGraph.append(arc)

        # Traverse graph and get seq ------------------------------------------
        # Try to find a vertex with degree 1
        oID = None
        for node in neighbors:
            if (len(neighbors[node]) == 1):
                oID = node
                break
        seq = traversalGraph(newGraph, oID=oID)['seq']
        seq.append(seq[0])

        return seq

    # Constructive Heuristics for TSP =========================================
    seq = None
    if (algo == 'DepthFirst'):
        seq = _consTSPDepthFirst(weightArcs)
    elif (algo == 'Christofides'):
        if (algoArgs == None):
            algoArgs = {'matchingAlgo': 'IP'}
        seq = _consTSPChristofides(weightArcs, algoArgs['matchingAlgo'])

    return seq

def _impTSP(
    nodes:      "Dictionary, returns the coordinate of given nodeID, \
                    {\
                        nodeID1: {'loc': (x, y)}, \
                        nodeID2: {'loc': (x, y)}, \
                        ... \
                    }" = None, 
    edges:      "Dictionary {(nodeID1, nodeID2): dist, ...}" = None,
    initSeq:    "Sequence of visiting nodes, as the initial route, generated by constructive heuristic" = [],
    algo:       "1) String (not available) 'LK' or \
                 2) String (default) '2Opt' = '2Opt'" = '2Opt'
    ) -> "Local improvement heuristic solution for TSP":

    # Subroutines for different local improvement heuristics ==================
    def _impTSP2Opt(nodeIDs, edges, initSeq):
        # Initialize ----------------------------------------------------------
        canImproveFlag = True
        impSeq = [i for i in initSeq]

        # Revert part of the sequences ----------------------------------------
        def revert(i, j, seq):
            rSeq = []
            if (j == i + 1 or j == i + 2):
                rSeq = [i for i in seq]
                rSeq[i], rSeq[j] = rSeq[j], rSeq[i]
            elif (j > i + 2):
                rSeq.extend([seq[k] for k in range(i)])
                rSeq.extend([seq[j - k] for k in range(j - i + 1)])
                rSeq.extend([seq[k] for k in range(j + 1, len(seq))])
            return rSeq

        # Main iteration ------------------------------------------------------
        if (len(impSeq) >= 4):
            while (canImproveFlag):
                canImproveFlag = False

                # Try 2-opt
                # First arc: (i, i + 1)
                # Second arc: (j, j + 1)
                # New arcs: (i, j + 1), (j, i + 1)
                for i in range(len(impSeq) - 3):
                    for j in range(i + 2, len(impSeq) - 1):
                        # Saving
                        saving = 0
                        if ((impSeq[i], impSeq[j]) in edges and (impSeq[i + 1], impSeq[j + 1]) in edges):
                            saving = (edges[impSeq[i], impSeq[i + 1]] + edges[impSeq[j], impSeq[j + 1]]) - (edges[impSeq[i], impSeq[j]] + edges[impSeq[i + 1], impSeq[j + 1]])
                        if (saving > CONST_EPSILON):
                            impSeq = revert(i + 1, j, impSeq)
                            canImproveFlag = True


        return impSeq

    # Heuristics that don't need to transform arc representation ==============
    seq = None
    nodeIDs = list(nodes.keys())
    if (algo == '2Opt'):
        seq = _impTSP2Opt(nodeIDs, edges, initSeq)

    return seq
