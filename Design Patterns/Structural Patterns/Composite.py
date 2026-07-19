# The Composite pattern lets you treat individual objects and groups of objects uniformly. 
# It's useful when you have a tree-like structure (files/folders, org charts, UI components) 
# and want client code to interact with a single leaf or a whole subtree through the same interface.

from abc import ABC, abstractmethod

# Component: common interface for both leaves and composites
class FileSystemComponent(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def show(self, indent = 0):
        pass
    
    @abstractmethod
    def getSize(self):
        pass

# Leaf: represents individual objects with no children
class File(FileSystemComponent):
    def __init__(self, name, size):
        super().__init__(name)
        self.size = size
    
    def show(self, indent=0):
        print(" " * indent + f"📄 {self.name} ({self.size}KB)")

    def getSize(self):
        return self.size

# Composite: represents a group of components (can contain files or folders)
class Folder(FileSystemComponent):
    def __init__(self, name):
        super().__init__(name)
        self.children = []
    
    def add(self, component: FileSystemComponent):
        self.children.append(component)
        return self  # allows chaining

    def remove(self, component: FileSystemComponent):
        self.children.remove(component)
    
    def show(self, indent=0):
        print(" " * indent + f"📁 {self.name}/")
        for child in self.children:
            child.show(indent + 2)

    def getSize(self):
        # Delegates to children, regardless of whether they're files or folders
        return sum(child.getSize() for child in self.children)

root = Folder("project")

src = Folder("src")
src.add(File("main.py", 12))
src.add(File("utils.py", 8))

tests = Folder("tests")
tests.add(File("test_main.py", 5))

root.add(src)
root.add(tests)
root.add(File("README.md", 3))

root.show()
print(f"\nTotal size: {root.getSize()}KB")