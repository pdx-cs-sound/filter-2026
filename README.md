# filter.py: simple filter demo
Bart Massey 2026

This provides some really simple filter demo
support. Currently does moving-average and windowed sinc FIR
filtering. Provides plots of filter response.

## Examples

Run these on a signal file, or with `--plot` to see what
they will do. Generate white noise with

```
sox -n -r 48000 -b 16 -t wav -c 1 noise.wav synth 5 noise white gain -3
```

### Moving Average

* Moving-average filter. Not great shape, but simple.

  ```
  --algorithm ma --order 2
  ```

* Moving-average filter cascade: improves response
  at the expense of quality

  ```
  --algorithm ma --order 2 --cascade 32
  ```

* Moving-average filter with lower cutoff point.  The -6dB
  cutoff point for an order-L filter is about $0.886 / L$,
  so about 0.1 here.

  ```
  --algorithm ma --order 8 --cascade 32
  ```

## Windowed-sinc FIR

* Windowed-sinc FIR filter. Roughly same computation as last
  MA example. Flat passband, narrow transition band, ok
  stopband.

  ```
  --algorithm firwin --order 256
  ```

* Cascade to double transition band but dramatically
  improve stopband.

  ```
  --algorithm firwin --order 128 --cascade 2
  ```

## Parks-McLellan FIR (Remez Exchange)

* FIR filter with fairly flat passband and stopband,
  narrow transition region.

  ```
  --algorithm remez --cutoff 0.5 --order 256 --transition 0.05
  ```

* Narrowing the transition band hurts the stopband a bit.

  ```
  --algorithm remez --cutoff 0.5 --order 256 --transition 0.01
  ```

## IIR (Chebyshev Type II)

* Flat passband, fairly sharp transition band and great
  stopband rejection from a lowish-order filter.

  ```
  --algorithm cheby2 --cutoff 0.5 --stop-db 100 --order 16
  ```
