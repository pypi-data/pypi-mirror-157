class NewFlow:
    """
    Create Flow.
    """
    
    # CONSTRUCTOR
    def __init__(self):
        self.__nodeData = []
        self.__linkData = []

        self.__flowBody = {
            'class': 'go.GraphLinksModel',
            'nodeDataArray': self.__nodeData,
            'linkDataArray': self.__linkData
        }


    # GETTERS
    def getFlowBody(self):
        """
        Get Flow Body.

        Output
        ----------
        dict
        """

        return self.__flowBody
    
    def getParsedBody(self):
        parsedBody = str(self.__flowBody).replace("'", '"').replace(' ', '')

        return parsedBody


    # METHODS
    def startNode(self):
        """
        Add Start node.

        Prerequisites
        ----------
        - Created flow.
        """

        startNode = {
            'category': 'Start',
            'text': 'Start',
            'key': -1,
            'loc': ''
        }

        self.__nodeData.append(startNode)

        return startNode
    
    def initNode(self, startValue):
        """
        Add Init node.

        Prerequisites
        ----------
        - Created flow.

        Parameters
        ----------
        startValue : int
            Initial value for the flow iterations.
        """

        initNode = {
            'category': 'Init',
            'text': str(startValue),
            'key': -2,
            'loc': ''
        }

        self.__nodeData.append(initNode)

        return initNode
    
    def circuitNode(self, circuitName):
        """
        Add Circuit node.

        Prerequisites
        ----------
        - Created flow.

        Parameters
        ----------
        circuitName : str
            Circuit name to introduce in the flow.
        """

        circuitNode = {
            'category': 'Circuit',
            'text': circuitName,
            'key': -3,
            'loc': ''
        }

        self.__nodeData.append(circuitNode)

        return circuitNode
    
    def repeatNode(self, numReps):
        """
        Add Repeat node.

        Prerequisites
        ----------
        - Created flow.

        Parameters
        ----------
        numReps : int
            Number of circuit repetitions.
        """

        repeatNode = {
            'category': 'Repeat',
            'text': str(numReps),
            'key': -4,
            'loc': ''
        }

        self.__nodeData.append(repeatNode)

        return repeatNode
    
    def endNode(self):
        """
        Add End node.

        Prerequisites
        ----------
        - Created flow.
        """
        
        endNode = {
            'category': 'End',
            'text': 'End',
            'key': -5,
            'loc': ''
        }

        self.__nodeData.append(endNode)

        return endNode
    
    def commentNode(self, comment):
        """
        Add Comment node.

        Prerequisites
        ----------
        - Created flow.

        Parameters
        ----------
        comment : str
            Comment.
        """

        commentNode = {
            'category': 'Comment',
            'text': comment,
            'key': -6,
            'loc': ''
        }

        self.__nodeData.append(commentNode)

        return commentNode
    
    def linkNodes(self, fromNode, toNode):
        """
        Link two nodes.

        Prerequisites
        ----------
        - Created flow.
        - Minimum two existing nodes.

        Parameters
        ----------
        fromNode : node
            Origin node to link.
        toNode : node
            Destiny node to link.
        """

        link = {
            'from': fromNode['key'],
            'to': toNode['key'],
            'points': []
        }

        self.__linkData.append(link)

        return link