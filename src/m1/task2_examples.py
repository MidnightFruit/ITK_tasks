from src.task2 import Singleton_meta, Singleton_new
from src.task2 import instanse as Singleton_import1
from src.task2 import instanse as Singleton_import2

s1 = Singleton_meta()
s2 = Singleton_meta()
print(s1 is s2)

s3 = Singleton_new()
s4 = Singleton_new()
print(s3 is s4)

print(Singleton_import1 is Singleton_import2)
