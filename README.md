# PaCoS
Pa(rallel) Co(mputation) S(imulator)

---

```
$ python -m pacos --all
=== ping-pong ===
ping
pong
ping
pong
ping
pong
=== perfect ===
* 0  OK-LAT(0)
* 1  OK-LAT(0)
* 2  OK-LAT(0)
* 3  OK-LAT(0)
* 4  OK-LAT(0)
=== inverted ===
* 0  STARVING-LAT(N/A)
* 1  OK-LAT(-1)
* 2  OK-LAT(-1)
* 3  OK-LAT(-1)
* 4  OK-LAT(-1)
=== nondet-impulse ===
* 0  STARVING-LAT(N/A)
* 1  OK-LAT(-1)
* 2  DROPPING(1)-LAT(0)
* 3  STARVING-LAT(N/A)
* 4  OK-LAT(-1)
* 5  OK-LAT(-1)
* 6  OK-LAT(-1)
* 7  OK-LAT(-1)
* 8  OK-LAT(-1)
* 9  DROPPING(1)-LAT(0)
=== starving ===
* 0  STARVING-LAT(N/A)
* 1  STARVING-LAT(N/A)
* 2  STARVING-LAT(N/A)
* 3  OK-LAT(0)
* 4  STARVING-LAT(N/A)
* 5  STARVING-LAT(N/A)
* 6  STARVING-LAT(N/A)
* 7  OK-LAT(0)
* 8  STARVING-LAT(N/A)
* 9  STARVING-LAT(N/A)
=== dropping ===
* 0  OK-LAT(0)
* 3  DROPPING(2)-LAT(0)
* 6  DROPPING(2)-LAT(0)
* 9  DROPPING(2)-LAT(0)
=== fuzzy ===
* 0  STARVING-LAT(N/A)
* 4  OK-LAT(-4)
* 8  OK-LAT(-1)
* 12  OK-LAT(-1)
* 16  STARVING-LAT(N/A)
* 20  OK-LAT(-2)
* 24  DROPPING(1)-LAT(-1)
* 28  OK-LAT(-2)
=== unsynch ===
* 0 A2 STARVING-LAT(N/A)
* 0 A1 OK-LAT(0)
* 1 A2 STARVING-LAT(N/A)
* 1 A1 OK-LAT(0)
* 2 A2 OK-LAT(-2)
* 2 A1 OK-LAT(0)
* 3 A2 OK-LAT(-2)
* 3 A1 OK-LAT(0)
* 4 A2 OK-LAT(-2)
* 4 A1 OK-LAT(0)
=== synch ===
* 0 A1 OK-LAT(0)
* 0 A2 OK-LAT(0)
* 1 A1 OK-LAT(0)
* 1 A2 OK-LAT(0)
* 2 A1 OK-LAT(0)
* 2 A2 OK-LAT(0)
* 3 A1 OK-LAT(0)
* 3 A2 OK-LAT(0)
* 4 A1 OK-LAT(0)
* 4 A2 OK-LAT(0)
=== unsynch-slow ===
* 0 A2 STARVING-LAT(N/A)
* 0 A1 OK-LAT(0)
* 1 A2 STARVING-LAT(N/A)
* 1 A1 OK-LAT(0)
* 2 A2 STARVING-LAT(N/A)
* 2 A1 OK-LAT(0)
* 3 A2 STARVING-LAT(N/A)
* 3 A1 OK-LAT(0)
* 4 A2 OK-LAT(-4)
* 4 A1 OK-LAT(0)
=== synch-slow ===
* 0 A1 OK-LAT(0)
* 1 A2 OK-LAT(-1)
* 1 A1 OK-LAT(0)
* 2 A2 OK-LAT(-1)
* 2 A1 OK-LAT(0)
* 3 A2 OK-LAT(-1)
* 3 A1 OK-LAT(0)
* 4 A2 OK-LAT(-1)
* 4 A1 OK-LAT(0)
```
