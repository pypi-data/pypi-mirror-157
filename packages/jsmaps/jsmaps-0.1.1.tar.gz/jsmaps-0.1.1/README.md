# Jsmaps:
## Starting with Js maps
* Creating a map:
```py
jsmap = map_({'hi':'hello', 'wave':'hi'})
 ```
* Basic showcase:
>```py
>from jsmaps import m
>jsmap = map_({'hi':'hello', 'wave':'hi', 0:'zero'})
>print(jsmap)
>#{
>#    [0] [hi: hello]
>#    [1] [wave: hi]
>#    [2] [0: zero]
>#}
>```
>```py
>print(jsmap[1])
>#hi
>print(jsmap['hi'])
>#hello
>print(jsmap.get(0))
>#zero
>print(jsmap.pair(0))
>#{'hi':'hello'}
>print(jsmap.getpair(0))
>#{2: 'zero'}   2 is the index in the map and zero is the value
>jsmap[0] = 'bye'
>#hi will now be bye
>jsmap['wave'] = 'hand'
>#wave will now be hand
>```
## Jsmaps Docs:
### *.get(self, value):*
Like `jsmap[value]` expect the `value` is always treated as a dict key.
### _.pair(self, value, *, type_=dict):
Returns the not specifed pair as a dict or list. 

For example:
```py
#map has [1] [hi: hello]
.pair(1) #{'hi':'hello'}
.pair('hi') #{1:'hello'}
.pair(1, type=list) ##['hi','hello']
```
### _.getpair(self, value, *, type_=dict):
returns the index and value of a key as a dict or list.
```py
#map has [2] [0: zero]
.getpair(0) #{2: 'zero'}
```
### Tuple sets(beta)
**Warning! beta. not completed.**

Goal:
```py
jsmap[key, slot] = value
jsmap[1, 1] = 'hi' #[1] ['hello':'hi'] is now [1] ['hi':'hi']
jsmap[1, 2] = 'hi' #[1] ['hi':'hello'] is now [1] ['hi':'hi']
jsmap[1, None] = {'hi': 'hi'} #[1] ['hello':'hello'] is now [1] ['hi':'hi']
```