class InvertedIndex:
    def __init__(self, docs):
        self.myDocs = docs  # document collection
        self.termList = []  # dictionary
        self.docLists = []  # used for each term's postings

        for i in range(len(self.myDocs)):
            tokens = self.myDocs[i].split()  # perform basic tokenization
            for token in tokens:
                if token not in self.termList:  # new term
                    self.termList.append(token)  # add term to dictionary
                    docList = [i]  # postings for this term
                    self.docLists.append(docList)  # add postings list for this term
                else:  # an existing term; update postings list for that term
                    index = self.termList.index(token)  # find index from term list
                    docList = self.docLists[index]
                    if i not in docList:  # not already a posting
                        docList.append(i)  # add posting to postings
                        self.docLists[index] = docList  # update postings for this term

    def __str__(self):
        matrixString = ""
        for i in range(len(self.termList)):
            matrixString += "{:<15}".format(self.termList[i])
            docList = self.docLists[i]
            for j in range(len(docList)):
                matrixString += str(docList[j]) + "\t"
            matrixString += "\n"
        return matrixString

    def search(self, query):
        if query not in self.termList:
            return None
        index = self.termList.index(query)
        if index < 0:  # no documents contain this keyword, return nothing
            # print(f"Documents do not contain '{query}'")
            return None
        # print(f"Documents containing '{query}': {self.docLists[index]}")
        return self.docLists[index]  # return postings for this term

    def search_multiple(self, query):
        result = self.search(query[0])  # look for first keyword
        termId = 1
        while termId < len(query):  # look for remaining keywords
            result1 = self.search(query[termId])  # look for current keyword
            if result1 is None or result is None:
                return None
            result = self.merge(result, result1)  # merge current list with intermediate list
            termId += 1
        if not result:
            return None
        return result

    def search_or(self, query):
        result = self.search(query[0])  # look for first keyword
        termId = 1
        while termId < len(query):  # look for remaining keywords
            result1 = self.search(query[termId])  # look for current keyword
            if result1:
                result.extend(result1)
            termId += 1
        if not result:
            return None
        return result

    @staticmethod
    def merge(l1, l2):
        mergedList = []
        id1, id2 = 0, 0  # positions in the respective lists
        while id1 < len(l1) and id2 < len(l2):
            if l1[id1] == l2[id2]:  # found a match
                mergedList.append(l1[id1])
                id1 += 1
                id2 += 1
            elif l1[id1] < l2[id2]:  # l1 docId is smaller, advance l1 pointer
                id1 += 1
            else:  # l2 docId is smaller, advance l2 pointer
                id2 += 1
        return mergedList
