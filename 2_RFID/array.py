
from module import *
from settings import *
from First import *

a = load_module_info()
print a

#have a list with name of module and ID not in the same column
for i in range(len(a)):
    a[i] = str(a[i])
    a[i] = a[i][:-1]
    a[i] = a[i].split("(")


ID_tag = '23099302756'
ex_tag = False

for i in a:
   if i[1] == ID_tag:
       ex_tag = True
       print ('The ID of this tag is ' + ID_tag + ' and this is' + i[0])

if ex_tag == False:
    print ('This ID does not exist yet')



