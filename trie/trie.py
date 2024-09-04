class TrieNode(object):
    def __init__(self, parent: 'TrieNode', letter: str) -> None:
        self.parent = parent
        self.children = None
        self.statuses = None
        self.letter = letter
        self.word = ""
    
    def is_leaf(self):
        return self.children is None or len(self.children) == 0

    def get_child(self, letter: str):
        if self.is_leaf():
            return None
        for child in self.children:
            if child.letter == letter:
                return child
        return None
    
    def add_child(self, letter: str):
        new_child = TrieNode(self, letter)
        if self.children is None:
            self.children = []
        self.children.append(new_child)
        return new_child
    
    def add_index(self, status_id: str):
        if self.statuses is None:
            self.statuses = []
        self.statuses.append(status_id)

    def get_all_children(self, result: dict):
        '''Fills result dict with all children recursivly'''
        if self.statuses is not None:
            for status_id in self.statuses:
                if status_id in result:
                    result[status_id] += 1
                else:
                    result[status_id] = 1
        if self.is_leaf():
            return
        for child in self.children:
            child.get_all_children(result)

    def get_all_children_words(self, result: dict):
        if self.word in result:
            result[self.word] += 1
        else:
            result[self.word] = 1
        if self.is_leaf():
            return
        for child in self.children:
            child.get_all_children_words(result)


class Trie(object):
    def __init__(self) -> None:
        self._root = TrieNode(None, "")

    def add_word(self, word: str, status_id: str):
        current = self._root
        for letter in word.lower():
            next = current.get_child(letter)
            if next:
                current = next
            else:
                current = current.add_child(letter)
        current.add_index(status_id)
        current.word = word

    def find_all_word_occurences(self, word: str) -> dict:
        '''Returns dict of status ids who contain this word, even as a part of other words.'''
        return self._all_word_occurences_recursive(word.lower(), self._root, 0)

    def _all_word_occurences_recursive(self, word: str, node: TrieNode, depth) -> dict:
        '''Part of the find_all_word_occurences function'''
        result = dict()
        if node.letter == word[0]:
            new = self._all_word_occurences_in_node(word, node)
            if new:
                result = {k: result.get(k, 0) + new.get(k, 0) for k in set(result) | set(new)} # merging new values to old dict
        if node.is_leaf():
            return result
        for child in node.children:
            new = self._all_word_occurences_recursive(word, child, depth + 1)
            if new:
                result = {k: result.get(k, 0) + new.get(k, 0) for k in set(result) | set(new)} # merging new values to old dict
        return result            

    def _all_word_occurences_in_node(self, word: str, node: TrieNode) -> dict:
        '''Returns a dict of statuses that contait given word, starting from the given node'''
        current = node
        for letter in word[1:]:
            next = current.get_child(letter)
            if next:
                current = next
            else:
                return None
        result = dict()
        current.get_all_children(result)
        return result

    def autocomplete_word(self, word: str):
        current = self._root
        for letter in word:
            next = current.get_child(letter)
            if next:
                current = next
            else:
                return None
        result = dict()
        current.get_all_children_words(result)
        return result

