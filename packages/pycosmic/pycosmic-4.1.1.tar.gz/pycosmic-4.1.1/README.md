
# Pycosmic

A Simple Package that makes Your Code Simple




## Installation

Install pycosmic with `pip`

```bash
  pip install pycosmic
```
or 


```
git clone https://github.com/rishabh-creator601/pycosmic.git
cd pycosmic
python setup.py install 
```

    
## Usage/Examples

1) Get code of any function / class 
```python
from pc import codeof

def test(a,b):
    return a + b

print(codeof(test))
>>> def test(a,b):
     return a + b

   
```

2) download a file from github

```python 
from pc import SetCode

SetCode(repo={reponame},filename={filename},user={username})


```

3) Extract Mathematical Equations from string 

```python 
from pc import Parser

exp = "hello string 2 + 2"
eq = Parser(exp).exp
print(eq)
>>> 2 + 2

```


4) Use maths Functions 
``` python 


import pc 

print(pc.sin(60))
print(pc.square(200))


```



5) Replace Snippets 



Example 1: Create File

Before :

``` python 
with open("file.txt","w") as f:
     f.write("hello")
     
f.close()


```


After:

``` python 


import pc 

pc.create("file.txt",cont="hello",mode="w") # You May Choose mode to 'wb'


```



Example 2: Load Files 


Before: 

```python 

#Load Txts 

with open("file.txt","r") as f:
      data = f.read()
f.close()



#Load Jsons 


import json 


with open("file.json","r") as f:
      data = json.load(f)


f.close()

```



After:


``` python 
 


import pc 

#Load Txts

data  = pc.load("file.txt","r") # Mode can Be 'rb'


#Load Jsons

data = pc.load_json("file.json","r")



```
