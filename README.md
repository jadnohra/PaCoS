# PaCoS 
Pa(rallel) Co(mputation) S(imulator) 


---

```
$ python -m pacos4.examples.all

=== pingpong-serial ===
WARNING: step: 1, pings_left: 3
WARNING: step: 3, pings_left: 2
WARNING: step: 5, pings_left: 1
=== pingpong-parallel ===
WARNING-17695: PING - time: 0.00e+00, pings_left: 3
WARNING-17696: PONG - time: 1.00e-09, pong
WARNING-17695: PING - time: 2.00e-09, pings_left: 2
WARNING-17696: PONG - time: 3.00e-09, pong
WARNING-17695: PING - time: 4.00e-09, pings_left: 1
WARNING-17696: PONG - time: 5.00e-09, pong
=== pingpong-parallel-slow_sim_hw ===
WARNING-17697: PING - time: 0.00e+00, pings_left: 3
INFO-17698: busy wait
WARNING-17698: PONG - time: 1.00e-09, pong
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
WARNING-17697: PING - time: 5.00e-09, pings_left: 2
WARNING-17698: PONG - time: 6.00e-09, pong
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
WARNING-17697: PING - time: 1.00e-08, pings_left: 1
WARNING-17698: PONG - time: 1.10e-08, pong
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
INFO-17698: busy wait
=== parallel-count ===
WARNING-17699: time: 0.00e+00, count: 0
WARNING-17700: time: 0.00e+00, count: 0
WARNING-17701: time: 0.00e+00, count: 0
WARNING-17701: time: 1.00e-09, count: 1
WARNING-17700: time: 1.00e-09, count: 1
WARNING-17699: time: 1.00e-09, count: 1
WARNING-17699: time: 2.00e-09, count: 2
WARNING-17700: time: 2.00e-09, count: 2
WARNING-17701: time: 2.00e-09, count: 2
0.9906778509994183 s. (wall time)
=== timer-race ===
WARNING-17704: Sink received value: OK
=== timer-race ===
WARNING-17707: Sink received value: OK
=== timer-race ===
WARNING-17710: Sink received value: OK
=== timer-race ===
WARNING-17713: Sink received value: UNINITIALIZED
=== timer-race ===
WARNING-17716: Sink received value: OK
```

# Credits

* pacos.jpg is from https://pxhere.com/en/photo/87232
