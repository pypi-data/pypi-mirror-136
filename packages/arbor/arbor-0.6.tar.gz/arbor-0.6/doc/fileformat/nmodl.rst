.. _formatnmodl:

NMODL
=====

.. csv-table::
   :header: "Name", "File extension", "Read", "Write"

   "NMODL", "``mod``", "✓", "✗"

*NMODL* is a `DSL <https://www.neuron.yale.edu/neuron/static/py_doc/modelspec/programmatic/mechanisms/nmodl.html>`_
for describing ion channel and synapse dynamics that is used by NEURON,
which provides the mod2c compiler parses dynamics described in NMODL to
generate C code that is called from NEURON.

Arbor has an NMODL compiler, *modcc*, that generates
optimized code in C++ and CUDA, which is optimized for
the target architecture. NMODL does not have a formal specification,
and its semantics are often
ambiguous. To manage this, Arbor uses its own dialect of NMODL that
does not allow some constructions used in NEURON's NMODL.

.. note::
    We hope to replace NMODL with a DSL that is well defined, and easier
    for both users and the Arbor developers to work with in the long term.
    Until then, please write issues on our GitHub with any questions
    that you have about getting your NMODL files to work in Arbor.

This page is a collection of NMODL rules for Arbor. It assumes that the reader
already has a working knowledge of NMODL.

Units
-----

Arbor doesn't support unit conversion in NMODL. This table lists the key NMODL
quantities and their expected units.

===============================================  ===================================================  ==========
quantity                                         identifier                                           unit
===============================================  ===================================================  ==========
voltage                                          v / v_peer                                           mV
time                                             t                                                    ms
temperature                                      celsius                                              °C
diameter (cross-sectional)                       diam                                                 µm

current_density (density mechanisms)             identifier defined using ``NONSPECIFIC_CURRENT``     mA/cm²
conductivity (density mechanisms)                identifier inferred from current_density equation    S/cm²
                                                 e.g. in ``i = g*v`` g is the conductivity
current (point and junction mechanisms)          identifier defined using ``NONSPECIFIC_CURRENT``     nA
conductance (point and junction mechanisms)      identifier inferred from current equation            µS
                                                 e.g. in ``i = g*v`` g is the conductance
ion X current_density (density mechanisms)       iX                                                   mA/cm²

ion X current (point and junction mechanisms)    iX                                                   nA

ion X reversal potential                         eX                                                   mV
ion X internal concentration                     Xi                                                   mmol/L
ion X external concentration                     Xo                                                   mmol/L
===============================================  ===================================================  ==========

Ions
-----

* Arbor recognizes ``na``, ``ca`` and ``k`` ions by default. Any new ions
  used in NMODL need to be explicitly added into Arbor along with their default
  properties and valence (this can be done in the recipe or on a single cell model).
  Simply specifying them in NMODL will not work.
* The parameters and variables of each ion referenced in a ``USEION`` statement
  are available automatically to the mechanism. The exposed variables are:
  internal concentration ``Xi``, external concentration ``Xo``, reversal potential
  ``eX`` and current ``iX``. It is an error to also mark these as
  ``PARAMETER``, ``ASSIGNED`` or ``CONSTANT``.
* ``READ`` and ``WRITE`` permissions of ``Xi``, ``Xo``, ``eX`` and ``iX`` can be set
  in NMODL in the ``NEURON`` block. If a parameter is writable it is automatically
  readable and doesn't need to be specified as both.
* If ``Xi``, ``Xo``, ``eX``, ``iX`` are used in a ``PROCEDURE`` or ``FUNCTION``,
  they need to be passed as arguments.
* If ``Xi`` or ``Xo`` (internal and external concentrations) are written in the
  NMODL mechanism they need to be declared as ``STATE`` variables and their initial
  values have to be set in the ``INITIAL`` block in the mechanism.

Special variables
-----------------

* Arbor exposes some parameters from the simulation to the NMODL mechanisms.
  These include ``v``, ``diam``, ``celsius`` and ``t`` in addition to the previously
  mentioned ion parameters.
* These special variables should not be ``ASSIGNED`` or ``CONSTANT``, they are
  ``PARAMETER``. This is different from NEURON where a built-in variable is
  declared ``ASSIGNED`` to make it accessible.
* ``diam`` and ``celsius`` are set from the simulation side.
* ``v`` is a reserved variable name and can be read but not written in NMODL.
* ``dt`` is not exposed to NMODL mechanisms.
* ``area`` is not exposed to NMODL mechanisms.
* ``NONSPECIFIC_CURRENTS`` should not be ``PARAMETER``, ``ASSIGNED`` or ``CONSTANT``.
  They just need to be declared in the NEURON block.

Functions, procedures and blocks
--------------------------------

* ``SOLVE`` statements should be the first statement in the ``BREAKPOINT`` block.
* The return variable of ``FUNCTION`` has to always be set. ``if`` without associated
  ``else`` can break that if users are not careful.
* Any non-``LOCAL`` variables used in a ``PROCEDURE`` or ``FUNCTION`` need to be passed
  as arguments.

Unsupported features
--------------------

* Unit conversion is not supported in Arbor (there is limited support for parsing
  units, which are just ignored).
* Unit declaration is not supported (ex: ``FARADAY = (faraday)  (10000 coulomb)``).
  They can be replaced by declaring them and setting their values in ``CONSTANT``.
* ``FROM`` - ``TO`` clamping of variables is not supported. The tokens are parsed and ignored.
  However, ``CONSERVE`` statements are supported.
* ``TABLE`` is not supported, calculations are exact.
* ``derivimplicit`` solving method is not supported, use ``cnexp`` instead.
* ``VERBATIM`` blocks are not supported.
* ``LOCAL`` variables outside blocks are not supported.
* ``INDEPENDENT`` variables are not supported.

Arbor-specific features
-----------------------

* Arbor's NMODL dialect supports the most widely used features of NEURON. It also
  has some features unavailable in NEURON such as the ``POST_EVENT`` procedure block.
  This procedure has a single argument representing the time since the last spike on
  the cell. In the event of multiple detectors on the cell, and multiple spikes on the
  detectors within the same integration period, the times of each of these spikes will
  be processed by the ``POST_EVENT`` block. Spikes are processed only once and then
  cleared.

  Example of a ``POST_EVENT`` procedure, where ``g`` is a ``STATE`` parameter representing
  the conductance:

  .. code::

    POST_EVENT(t) {
       g = g + (0.1*t)
    }

* Arbor allows a gap-junction mechanism to access the membrane potential at the peer site
  of a gap-junction connection as well as the local site. The peer membrane potential is
  made available through the ``v_peer`` variable while the local membrane potential
  is available through ``v``, as usual.

Nernst
------
Many mechanisms make use of the reversal potential of an ion (``eX`` for ion ``X``).
A popular equation for determining the reversal potential during the simulation is
the `Nernst equation <https://en.wikipedia.org/wiki/Nernst_equation>`_.
Both Arbor and NEURON make use of ``nernst``. Arbor implements it as a mechanism and
NEURON implements it as a built-in method. However, the conditions for using the
``nernst`` equation to change the reversal potential of an ion differ between the
two simulators.

1. In Arbor, the reversal potential of an ion remains equal to its initial value (which
has to be set by the user) over the entire course of the simulation, unless another
mechanism which alters that reversal potential (such as ``nernst``) is explicitly selected
for the entire cell. (see :ref:`cppcablecell-revpot` for details).

.. NOTE:
  This means that a user cannot indicate to use ``nernst`` to calculate the reversal
  potential on some regions of the cell, while other regions of the cell have a constant
  reversal potential. It's either applied on the entire cell or not at all. This differs
  from NEURON's policy.

2. In NEURON, there is a rule which is evaluated (under the hood) per section of a given
cell to determine whether or not the reversal potential of an ion remains constant or is
calculated using ``nernst``. The rule is documented
`here <https://neuron.yale.edu/neuron/static/new_doc/modelspec/programmatic/ions.html>`_
and can be summarized as follows:

  Examining all mechansims on a given section, if the internal or external concentration of
  an ion is **written**, and its reversal potential is **read but not written**, then the
  nernst equation is used **continuously** during the simulation to update the reversal
  potential of the ion.
  And if the internal or external concentration of an ion is **read**, and its reversal
  potential is **read but not written**, then the nernst equation is used **once** at the
  beginning of the simulation to caluclate the reversal potential of the ion, and then
  remains constant.
  Otherwise, the reversal potential is set by the user and remains constant.

One of the main consequences of this difference in behavior is that in Arbor, a mechanism
modifying the reversal potential (for example ``nernst``) can only be applied (for a given ion)
at a global level on a given cell. While in Neuron, different mechanisms can be used for
calculating the reversal potential of an ion on different parts of the morphology.
This is due to the different methods Arbor and NEURON use for discretising the morphology.
(A ``region`` in Arbor may include part of a CV, where as in NEURON, a ``section``can only
contain full ``segments``).

Modelers are encouraged to verify the expected behavior of the reversal potentials of ions
as it can lead to vastly different model behavior.
