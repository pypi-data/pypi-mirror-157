import unittest
from QuantumPathQSOAPySDK import QSOAPlatform


class Test_NewFlow(unittest.TestCase):

    # EMPTY CIRCUIT
    def test_createCircuit(self):
        qsoa = QSOAPlatform()
        
        flow = qsoa.NewFlow() # create circuit

        self.assertEqual(flow.getFlowBody(), {'class': 'go.GraphLinksModel', 'nodeDataArray': [], 'linkDataArray': []}) # check flow body
    

    # ADD START NODE
    def test_addStartNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        startNode = flow.startNode() # add node

        self.assertEqual(startNode, {'category': 'Start', 'text': 'Start', 'key': -1, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'Start', 'text': 'Start', 'key': -1, 'loc': ''}]) # check all flow nodes
    

    # ADD INIT NODE
    def test_addInitNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        initNode = flow.initNode(0) # add node

        self.assertEqual(initNode, {'category': 'Init', 'text': '0', 'key': -2, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'Init', 'text': '0', 'key': -2, 'loc': ''}]) # check all flow nodes
    

    # ADD CIRCUIT NODE
    def test_addCircuitNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        circuitNode = flow.circuitNode('circuitName') # add node

        self.assertEqual(circuitNode, {'category': 'Circuit', 'text': 'circuitName', 'key': -3, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'Circuit', 'text': 'circuitName', 'key': -3, 'loc': ''}]) # check all flow nodes
    

    # ADD REPEAT NODE
    def test_addRepeatNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        repeatNode = flow.repeatNode(1000) # add node

        self.assertEqual(repeatNode, {'category': 'Repeat', 'text': '1000', 'key': -4, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'Repeat', 'text': '1000', 'key': -4, 'loc': ''}]) # check all flow nodes


    # ADD END NODE
    def test_addEndNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        endNode = flow.endNode() # add node

        self.assertEqual(endNode, {'category': 'End', 'text': 'End', 'key': -5, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'End', 'text': 'End', 'key': -5, 'loc': ''}]) # check all flow nodes
    

    # ADD COMMENT NODE
    def test_addCommentNode(self):
        qsoa = QSOAPlatform()

        flow = qsoa.NewFlow() # create circuit

        commentNode = flow.commentNode('Comment') # add node

        self.assertEqual(commentNode, {'category': 'Comment', 'text': 'Comment', 'key': -6, 'loc': ''}) # check node construction
        self.assertEqual(flow.getFlowBody()['nodeDataArray'], [{'category': 'Comment', 'text': 'Comment', 'key': -6, 'loc': ''}]) # check all flow nodes
    

    # LINK NODES
    def test_linkNodes(self):
        qsoa = QSOAPlatform()
        
        flow = qsoa.NewFlow() # create flow
        startNode = flow.startNode() # existing node
        initNode = flow.initNode(0) # existing node
        circuitNode = flow.circuitNode('circuitName') # existing node
        repeatNode = flow.repeatNode(1000) # existing node
        endNode = flow.endNode() # existing node

        linkNodes1 = flow.linkNodes(startNode, initNode) # link nodes
        linkNodes2 = flow.linkNodes(initNode, circuitNode) # link nodes
        linkNodes3 = flow.linkNodes(circuitNode, repeatNode) # link nodes
        linkNodes4 = flow.linkNodes(repeatNode, endNode) # link nodes

        self.assertEqual(linkNodes1, {'from': -1, 'to': -2, 'points': []}) # check link construction
        self.assertEqual(linkNodes2, {'from': -2, 'to': -3, 'points': []}) # check link construction
        self.assertEqual(linkNodes3, {'from': -3, 'to': -4, 'points': []}) # check link construction
        self.assertEqual(linkNodes4, {'from': -4, 'to': -5, 'points': []}) # check link construction
        self.assertEqual(flow.getFlowBody(), {
            'class': 'go.GraphLinksModel',
            'nodeDataArray': [
                {'category': 'Start', 'text': 'Start', 'key': -1, 'loc': ''},
                {'category': 'Init', 'text': '0', 'key': -2, 'loc': ''},
                {'category': 'Circuit', 'text': 'circuitName', 'key': -3, 'loc': ''},
                {'category': 'Repeat', 'text': '1000', 'key': -4, 'loc': ''},
                {'category': 'End', 'text': 'End', 'key': -5, 'loc': ''}
            ],
            'linkDataArray': [
                {'from': -1, 'to': -2, 'points': []},
                {'from': -2, 'to': -3, 'points': []},
                {'from': -3, 'to': -4, 'points': []},
                {'from': -4, 'to': -5, 'points': []}
            ]
        }) # check all flow nodes and links


if __name__ == '__main__':
    unittest.main()