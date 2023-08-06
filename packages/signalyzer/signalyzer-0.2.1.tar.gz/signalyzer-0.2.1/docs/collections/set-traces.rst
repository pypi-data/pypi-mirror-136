.. currentmodule:: signalyzer

.. testsetup:: *

    from signalyzer import *

.. _set trace:

Set Traces
==========

The `set trace`_ collection is used to store the resulting :ref:`signal
traces <signal trace>` produced by the :ref:`signal statistics <signal statistics>`
analysis for each combined set of the provided sets of signal
:attr:`~Trace.samples`.

Create the Trace Collection
---------------------------

You can create a `set trace`_ collection from multiple traces, iterables,
iterators and/or numbers by calling the class method :meth:`~SetTraces.from_traces`
with the sets of signal :attr:`~Trace.samples` which shall be combined and
statistically analyzed.

  >>> # create a set trace collection from traces, iterables, iterators, numbers
  >>> traces = SetTraces.from_traces(
  ...   Trace('Signal', [1, 2, 3]),
  ...   Trace('Signal', [-3, -2, -1]),
  ...   [1, 0, -1],
  ...   range(3),
  ...   0)
  >>> traces
  SetTraces(mean=Trace(label='SetTrace:mean',
                       samples=[-0.2, 0.2, 0.6]),
    weighted_mean=Trace(label='SetTrace:weighted_mean',
                        samples=[-0.13333333333333333, 0.13333333333333333, 0.4]),
    median=Trace(label='SetTrace:median',
                 samples=[0, 0, 0]),
    mode=Trace(label='SetTrace:mode',
               samples=[1, 0, -1]),
    rms=Trace(label='SetTrace:rms',
              samples=[1.4832396974191326, 1.3416407864998738, 1.7320508075688772]),
    minimum=Trace(label='SetTrace:minimum',
                  samples=[-3, -2, -1]),
    maximum=Trace(label='SetTrace:maximum',
                  samples=[1, 2, 3]),
    range=Trace(label='SetTrace:range',
                samples=[4, 4, 4]),
    midrange=Trace(label='SetTrace:midrange',
                    samples=[-1.0, 0.0, 1.0]),
    absolute_error=Trace(label='SetTrace:absolute_error',
                         samples=[5.6000000000000005, 5.2, 7.6]),
    variance=Trace(label='SetTrace:variance',
                   samples=[2.1599999999999993, 1.7600000000000002, 2.6399999999999997]),
    deviation=Trace(label='SetTrace:deviation',
                    samples=[1.4696938456699067, 1.32664991614216, 1.624807680927192]),
    coefficient=Trace(label='SetTrace:coefficient',
                      samples=[-7.348469228349533, 6.6332495807108005, 2.7080128015453204]),
    skew=Trace(label='SetTrace:skew',
               samples=[-1.1642636431747204, -0.37003665016361925, 0.3804646084815739]),
    kurtosis=Trace(label='SetTrace:kurtosis',
             samples=[2.8127572016460904, 2.21694214876033, 1.4421487603305787]))

.. important::

  All *iterables* should have the same length, otherwise only a subset is returned!

.. note::

  The linear *weighted mean* is computed with the order of the provided traces
  to combine. The lowest weight has the first trace the highest weight has the
  last trace.


Empty Collection
~~~~~~~~~~~~~~~~

You can create a `set trace`_ collection without :attr:`~Trace.samples`
by calling the :class:`SetTraces` class.

  >>> # create an empty set trace collection
  >>> traces = SetTraces()
  >>> traces
  SetTraces(mean=Trace(label='Trace', samples=[]),
            weighted_mean=Trace(label='Trace', samples=[]),
            median=Trace(label='Trace', samples=[]),
            mode=Trace(label='Trace', samples=[]),
            rms=Trace(label='Trace', samples=[]),
            minimum=Trace(label='Trace', samples=[]),
            maximum=Trace(label='Trace', samples=[]),
            range=Trace(label='Trace', samples=[]),
            midrange=Trace(label='Trace', samples=[]),
            absolute_error=Trace(label='Trace', samples=[]),
            variance=Trace(label='Trace', samples=[]),
            deviation=Trace(label='Trace', samples=[]),
            coefficient=Trace(label='Trace', samples=[]),
            skew=Trace(label='Trace', samples=[]),
            kurtosis=Trace(label='Trace', samples=[]))

Number of Traces
----------------

You can get the number of the traces in the :class:`SetTraces` collection
with the built-in function :func:`len`.

  >>> # number of traces in the collection
  >>> len(traces)
  15

Names of the Traces
-------------------

You can get the :class:`list` with the names of the traces in the
:class:`SetTraces` collection.

A :class:`list` with the key names of the traces is returned.

  >>> # key names of the traces in the collection
  >>> list(traces)
  ['mean',
   'weighted_mean',
   'median',
   'mode',
   'rms',
   'minimum',
   'maximum',
   'range',
   'midrange',
   'absolute_error',
   'variance',
   'deviation',
   'coefficient',
   'skew',
   'kurtosis']

  >>> # key names of the traces in the collection
  >>> list(traces.keys())
  ['mean',
   'weighted_mean',
   'median',
   'mode',
   'rms',
   'minimum',
   'maximum',
   'range',
   'midrange',
   'absolute_error',
   'variance',
   'deviation',
   'coefficient',
   'skew',
   'kurtosis']

Mean Trace
----------

You can get the arithmetic *mean* :class:`Trace` with the
:attr:`~StatisticsTraces.mean` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the arithmetic *mean* :attr:`~Trace.samples`
is returned.

  >>> # mean trace by attribute
  >>> traces.mean
  Trace(label='Trace', samples=[])
  >>> # mean trace by key
  >>> traces['mean']
  Trace(label='Trace', samples=[])

Weighted Mean Trace
-------------------

You can get the linear *weighted mean* :class:`Trace` with the
:attr:`~StatisticsTraces.weighted_mean` attribute from the
:class:`SetTraces` collection.

The :class:`Trace` with the linear *weighted mean* :attr:`~Trace.samples`
is returned.

  >>> # linear weighted mean trace by attribute
  >>> traces.weighted_mean
  Trace(label='Trace', samples=[])
  >>> # linear weighted mean trace by key
  >>> traces['weighted_mean']
  Trace(label='Trace', samples=[])

Median Trace
------------

You can get the *median* :class:`Trace` with the
:attr:`~StatisticsTraces.median` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *median* :attr:`~Trace.samples`
is returned.

  >>> # median trace by attribute
  >>> traces.median
  Trace(label='Trace', samples=[])
  >>> # median trace by key
  >>> traces['median']
  Trace(label='Trace', samples=[])

Mode Trace
----------

You can get the *mode* :class:`Trace` with the
:attr:`~StatisticsTraces.mode` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *mode* :attr:`~Trace.samples`
is returned.

  >>> # mode trace by attribute
  >>> traces.mode
  Trace(label='Trace', samples=[])
  >>> # mode trace by key
  >>> traces['mode']
  Trace(label='Trace', samples=[])

Root Mean Square Trace
----------------------

You can get the *root mean square* :class:`Trace` with the
:attr:`~StatisticsTraces.rms` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *root mean square* :attr:`~Trace.samples`
is returned.

  >>> # root mean square (rms) trace by attribute
  >>> traces.rms
  Trace(label='Trace', samples=[])
  >>> # root mean square (rms) trace by key
  >>> traces['rms']
  Trace(label='Trace', samples=[])

Minimum Trace
-------------

You can get the *minimum* :class:`Trace` with the
:attr:`~StatisticsTraces.minimum` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *minimum* :attr:`~Trace.samples` is returned.

  >>> # minimum trace by attribute
  >>> traces.minimum
  Trace(label='Trace', samples=[])
  >>> # minimum trace by key
  >>> traces['minimum']
  Trace(label='Trace', samples=[])

Maximum Trace
-------------

You can get the *maximum* :class:`Trace` with the
:attr:`~StatisticsTraces.maximum` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *maximum* :attr:`~Trace.samples` is returned.

  >>> # maximum trace by attribute
  >>> traces.maximum
  Trace(label='Trace', samples=[])
  >>> # maximum trace by key
  >>> traces['maximum']
  Trace(label='Trace', samples=[])

Range Trace
-----------

You can get the *range* :class:`Trace` with the
:attr:`~StatisticsTraces.maximum` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *range* :attr:`~Trace.samples` is returned.

  >>> # range trace by attribute
  >>> traces.range
  Trace(label='Trace', samples=[])
  >>> # range trace by key
  >>> traces['range']
  Trace(label='Trace', samples=[])

Mid-Range Trace
---------------

You can get the *midrange* :class:`Trace` with the
:attr:`~StatisticsTraces.midrange` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *midrange* :attr:`~Trace.samples`
is returned.

  >>> # mid-range trace by attribute
  >>> traces.midrange
  Trace(label='Trace', samples=[])
  >>> # mid-range trace by key
  >>> traces['midrange']
  Trace(label='Trace', samples=[])

Absolute Error Trace
--------------------

You can get the *absolute error* :class:`Trace` with the
:attr:`~StatisticsTraces.absolute_error` attribute from the
:class:`SetTraces` collection.

The :class:`Trace` with the *absolute error* :attr:`~Trace.samples` is returned.

  >>> # absolute error trace by attribute
  >>> traces.absolute_error
  Trace(label='Trace', samples=[])
  >>> # absolute error trace by key
  >>> traces['absolute_error']
  Trace(label='Trace', samples=[])

Variance Trace
--------------

You can get the *variance* :class:`Trace` with the
:attr:`~StatisticsTraces.variance` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *variance* :attr:`~Trace.samples` is returned.

  >>> # variance trace by attribute
  >>> traces.variance
  Trace(label='Trace', samples=[])
  >>> # variance trace by key
  >>> traces['variance']
  Trace(label='Trace', samples=[])

Standard Deviation Trace
------------------------

You can get the *standard deviation* :class:`Trace` with the
:attr:`~StatisticsTraces.deviation` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *standard deviation* :attr:`~Trace.samples`
is returned.

  >>> # standard deviation trace by attribute
  >>> traces.deviation
  Trace(label='Trace', samples=[])
  >>> # standard deviation trace by key
  >>> traces['deviation']
  Trace(label='Trace', samples=[])

Coefficient of Variation Trace
------------------------------

You can get the *coefficient of variation* :class:`Trace` with the
:attr:`~StatisticsTraces.coefficient` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *coefficient of variation* :attr:`~Trace.samples`
is returned.

  >>> # coefficient of variation trace by attribute
  >>> traces.coefficient
  Trace(label='Trace', samples=[])
  >>> # coefficient of variation trace by key
  >>> traces['coefficient']
  Trace(label='Trace', samples=[])

Skew Trace
----------

You can get the *skew* :class:`Trace` with the
:attr:`~StatisticsTraces.skew` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *skew* :attr:`~Trace.samples` is returned.

  >>> # biased skew trace by attribute
  >>> traces.skew
  Trace(label='Trace', samples=[])
  >>> # biased skew trace by key
  >>> traces['skew']
  Trace(label='Trace', samples=[])

Kurtosis Trace
--------------

You can get the *kurtosis* :class:`Trace` with the
:attr:`~StatisticsTraces.kurtosis` attribute from the :class:`SetTraces`
collection.

The :class:`Trace` with the *kurtosis* :attr:`~Trace.samples` is returned.

  >>> # biased kurtosis trace by attribute
  >>> traces.kurtosis
  Trace(label='Trace', samples=[])
  >>> # biased kurtosis trace by key
  >>> traces['kurtosis']
  Trace(label='Trace', samples=[])

Figure
------

You can visualize the trace collection with a figure containing the subplots of
the traces in the collection by calling the method
:meth:`~StatisticsTraces.figure`.

  >>> figure = SetTraces.from_traces(
  ...   Trace('Signal', [1, 2, 3]),
  ...   Trace('Signal', [-3, -2, -1]),
  ...   [1, 0, -1],
  ...   range(3),
  ...   0).figure()

.. plotly::

  from signalyzer import SetTraces, Trace

  traces = SetTraces.from_traces(
    Trace('Signal', [1, 2, 3]), Trace('Signal', [-3, -2, -1]), [1, 0, -1], range(3), 0)
  fig = traces.figure()

  fig.show()
