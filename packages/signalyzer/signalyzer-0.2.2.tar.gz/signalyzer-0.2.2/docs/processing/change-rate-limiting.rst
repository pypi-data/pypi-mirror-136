.. currentmodule:: signalyzer

.. testsetup:: *

    from signalyzer import *

.. _change-rate limiting:

Change-Rate Limiting
====================

The signal :attr:`~Trace.samples` of a **binary** :ref:`signal trace <signal trace>`
can be processed with a `change-rate limiting`_ algorithm.

Limiting Change-Rates
---------------------

You can limit the *on*-state and *off*-state change-rate of the **binary** signal
:attr:`~Trace.samples` by the number of samples to delay (supress) the change to
the *on*-state, and by the number of samples to delay (supress) the change to
the *off*-state by calling the method :meth:`~Trace.delay`.

A new :class:`Trace` instance *labeled* with the performed transformation
``'delay'`` is returned.

  >>> # change-rate limited binary signal samples
  >>> Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0]).delay(1, 1)
  Trace(label='Signal:delay', samples=[0, 0, 1, 1, 1, 1, 0, 0, 0])

.. plotly::

  from signalyzer import Trace

  signal = Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0])
  trace = signal.delay(1, 1)
  fig = go.Figure([signal.digital.plot(),
                   trace.digital.plot(mode='lines+markers')])
  fig.show()


Delaying On-State
-----------------

You can delay the *on*-state of the **binary** signal :attr:`~Trace.samples` by
the number of samples to delay (supress) the change to the *on*-state by calling
the method :meth:`~Trace.delay`.

A new :class:`Trace` instance *labeled* with the performed transformation
``'delay'`` is returned.

  >>> # on-state filtered/delayed binary signal samples
  >>> Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0]).delay(on=1)
  Trace(label='Signal:delay', samples=[0, 0, 1, 0, 0, 0, 0, 0, 0])

.. plotly::

  from signalyzer import Trace

  signal = Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0])
  trace = signal.delay(1, 0)
  fig = go.Figure([signal.digital.plot(),
                   trace.digital.plot(mode='lines+markers')])
  fig.show()


Delaying Off-State
------------------

You can delay the *off*-state of the **binary** signal :attr:`~Trace.samples` by
the number of samples to delay (supress) the change to the *off*-state by
calling the method :meth:`~Trace.delay`.

A new :class:`Trace` instance *labeled* with the performed transformation
``'delay'`` is returned.

  >>> # off-state filtered/delayed binary signal samples
  >>> Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0]).delay(off=1)
  Trace(label='Signal:delay', samples=[0, 1, 1, 1, 1, 1, 0, 1, 1])

.. plotly::

  from signalyzer import Trace

  signal = Trace('Signal', [0, 1, 1, 0, 1, 0, 0, 1, 0])
  trace = signal.delay(0, 1)
  fig = go.Figure([signal.digital.plot(),
                   trace.digital.plot(mode='lines+markers')])
  fig.show()
