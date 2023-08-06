# BlCh
a python package that can help you make a blockchain within 50 lines of code

## Example
```python=
from blch import Block, Blockchain

def  main():
	blockchain  =  Blockchain()
	database  = ["Joe gives 2 coins to jack", "Jack gives 3 coins to Joe", "May gave 10 coins to Klaus", "Klaus gave 5 coins to May"]
	
	num  =  0
	for  data  in  database:
	num  +=  1
	
	blockchain.mine(Block(num, data=data))
	for  block  in  blockchain.chain:
		print(block)

	print(blockchain.isValid())
	blockchain.mine(blockchain.chain[0])

if  __name__  ==  '__main__':
	main()
```
This is a simple example of the code which can be tweaked by your needs

---
If any problems please raise an issue in the github repo of this package

---


## Repo
Please fork my repo and make sure to let me know for any ideas or problems to fix

[![Build Status](https://img.shields.io/badge/BlCh-repo-blue)](https://github.com/lofibot-22/blch/)
