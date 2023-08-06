"""
FilePile is a module which can convert all the files in the specified directory
as a file tree, and support the serialize them into a list, which is convenient
for operate a large number of files in the specified directory. Type filters can
also be used to filter types during tree building.
"""
import os
import sys


def get_files(path: str) -> list:
    """
    Get All files under a path(directory).
    """
    return [name for name in os.listdir(path)]


def to_absolute_path(path: str) -> list:
    """
    Turn given path to absolute format.
    """
    if path[1] == '.' and path[0] == '.':
            path = '/'.join(sys.argv[0].split('\\')[:-2]) + path[2:]
    elif path[0] == '.':
        path = '/'.join(sys.argv[0].split('\\')[:-1]) + path[1:]
    elif path[0] == '/':
        path = sys.argv[0].split('\\')[0] + path
    elif path[1] == ':': pass
    else:
        path = '/'.join(sys.argv[0].split('\\')[:-1]) + '/' + path
    return path


def normalize_path(path: str, turn_to_absolute=True) -> str:
    """
    Normalize path to adapt to our later process.
    """
    path = path.replace('\\', '/')
    path = path if path[-1] != '/' else path[:-1]
    if turn_to_absolute:
        path = to_absolute_path(path)
    return path


def strip_pre_path(path: str) -> str:
    """
    Strip pre path and only remain its filename past.
    Such as turn "../abc/a.txt" to "a.txt".
    """
    return normalize_path(path, turn_to_absolute=False).split('/')[-1]


def get_file_type(path: str) -> str:
    """
    Get file's type.
    """
    filename = strip_pre_path(path)
    if '.' in filename:
        return filename.split('.')[-1]
    else:
        return filename



class FileNode():
    def __init__(self, path, value, inner_nodes):
        """
        value: file or dir's name
        inner: if object is a dir, there is a list. Or not, there is None.
        path: file or dir's path.
        """
        self.value = value
        self.inner = inner_nodes
        self.path = path


class FileTree:
    def __init__(self, init_path, is_absolute_path=True, type_filter=None):
        """
        Two mode: absolute path or not.
        Use type filter to filter files, such as type_filter=['exe', 'dll'] can only load 
        two kinds of files to tree.

        path: Tree's start path.
        root: Tree's start dir node.
        count: file's count, attention it's not the NODE's count.
        """
        if is_absolute_path:
            self.path = normalize_path(init_path)
        else:
            self.path = normalize_path(init_path, turn_to_absolute=False)

        self.root = FileNode(self.path, strip_pre_path(self.path), [])
        self.count = 0
        self.buildTree(type_filter)

    def addCount(self) -> None: self.count += 1

    def buildTree(self, type_filter) -> None:
        """
        Build file tree.
        """
        node_queue = []
        node_queue.append(self.root)

        while len(node_queue):
            node = node_queue.pop(0)
            file_names = get_files(node.path)

            for name in file_names:
                if os.path.isfile(to_absolute_path(node.path+'/'+name)):
                    if type_filter != None and get_file_type(name) in type_filter:
                        node.inner.append(FileNode(node.path+'/'+name, name, None))
                        self.addCount()
                    elif type_filter != None:
                        pass
                    else:
                        node.inner.append(FileNode(node.path+'/'+name, name, None))
                        self.addCount()
                else:
                    next_node = FileNode(node.path+'/'+name, name, [])
                    node_queue.append(next_node)
                    node.inner.append(next_node)

    def to_dict(self) -> dict:
        """
        Turn file tree to a big dict. It'll contains every node's info.
        """
        node_queue = []
        files_dict = {'{}'.format(self.root.value): []}
        node_queue.append((self.root, files_dict[self.root.value]))

        while len(node_queue):
            node, storage = node_queue.pop(0)
            for inner_node in node.inner:
                if inner_node.inner == None:
                    storage.append(inner_node.value)
                else:
                    storage.append({
                        '{}'.format(inner_node.value): []
                    })
                    node_queue.append((inner_node, storage[-1][inner_node.value]))
        return files_dict
    
    def generator(self):
        """
        Return a generator to all files, so we can process these file easily.
        """
        node_queue = []
        node_queue.append(self.root)

        while len(node_queue):
            node = node_queue.pop(0)
            for inner_node in node.inner:
                if inner_node.inner == None:
                    yield inner_node
                else:
                    node_queue.append(inner_node)
    
    def flat(self) -> list:
        """
        Load all file node to a list.
        """
        return list(self.generator())


if __name__ == "__main__":
    print(get_file_type('./a.txt'))
    print(get_file_type('../config'))