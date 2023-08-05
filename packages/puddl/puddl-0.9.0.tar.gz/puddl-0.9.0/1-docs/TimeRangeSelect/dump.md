how to grid
```
In [1]: # größenordnung 30x20 wär' ok

In [2]: print("größenordnung 30x20 wär' ok")
größenordnung 30x20 wär' ok

In [3]: MINPERDAY = 24*60

In [4]: for x in [5,6,10,12,15]:
   ...:     print(MINPERDAY / x)
   ...:
288.0
240.0
144.0
120.0
96.0

In [5]: print 30 * 20
  File "<ipython-input-5-b6b87441f292>", line 1
    print 30 * 20
           ^
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(30 * 20)?


In [6]: print(30*20)
600

In [7]: print("bei 5 sind's also 288 felder. das ist", 2**4 * 3**3)
bei 5 sind's also 288 felder. das ist 432

In [8]: print("""
   ...: WTF? Wie falsch kann meine Rechnung denn sein?
   ...: """)

WTF? Wie falsch kann meine Rechnung denn sein?


In [9]: 24 * 60 / 5
Out[9]: 288.0

In [10]: 24 * 30 * 2 / 5
Out[10]: 288.0

In [11]: 24 * 6 * 10 / 5
Out[11]: 288.0

In [12]: 24 * 6 * 2
Out[12]: 288

In [13]: 12 * 12 * 6 * 2
Out[13]: 1728

In [14]: 24 * 6 * 2
Out[14]: 288

In [15]: 2 * 12 * 6 * 2
Out[15]: 288

In [16]: 2 * 3* * 2 * 6 * 2
  File "<ipython-input-16-63eb0a3ab062>", line 1
    2 * 3* * 2 * 6 * 2
           ^
SyntaxError: invalid syntax


In [17]: 2 * 2**2 * 2 * 6 * 2
Out[17]: 192

In [18]: 2 * 2**2 * 3 * 6 * 2  # typo
Out[18]: 288

In [19]: 2**4 * 3 * 6
Out[19]: 288

In [20]: 2**5 * 3**2
Out[20]: 288

In [21]: print("primfaktorzerlegung done")
primfaktorzerlegung done

In [22]: 16 * 18
Out[22]: 288

In [23]: 18 * 16
Out[23]: 288

In [24]: x=18

In [25]: y = 16

In [26]: x * y
Out[26]: 288

In [27]: print("für desktop isses fein. frage ist: macht's spaß zu bedienen?")
für desktop isses fein. frage ist: macht's spaß zu bedienen?
```
