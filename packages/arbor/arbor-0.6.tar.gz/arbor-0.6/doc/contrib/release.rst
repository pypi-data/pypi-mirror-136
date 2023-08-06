Releases
********

Release cycle
=============

0. release every 3 months (at time ``T``)
1. ``T-11`` weeks: ``all`` add your favorite Issues to the next-rel column
2. ``T-10`` weeks: ``Scrum Master`` prep dev meet (internal)

   * Update/trim next-release column in Kanban
   * Prepare agenda, include possible additions not covered by Kanban/Issues
   * Add milestone tags (nextver, nextver+1, etc.)
3. ``T-8`` weeks: ``Release Manager`` dev meet (external/public)

   * Use Kanban as starter
   * Move issues around based on input
   * Add milestone tags, for this release or future releases
4. ``T±0``: ``Release Manager`` release!
5. ``T+1`` weeks: ``Scrum Master`` retrospective
   
   * set date for next release

Procedure
=========

These notes enumerate the steps required every time we release a new
version of Arbor.

Pre-release
-----------

Update tags/versions and test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

0. Check README.md, ATTRIBUTIONS.md, CONTRIBUTING.md.
1. Create new temp-branch ending in ``-rc``. E.g. ``v0.6-rc``
2. Bump the ``VERSION`` file:
   https://github.com/arbor-sim/arbor/blob/master/VERSION
   Don't append ``-rc`` here, but if you do, remove it before releasing.
3. Run all tests.
   - ``ciwheel.yml`` triggers when you push a branch called ``v*rc``, ON YOUR OWN REPO (so check ``github.com/$yourname/arbor/actions``). Make sure the tests pass.
   - This should catch many problems. For a manual check:
   - Verify MANIFEST.in (required for PyPI sdist)
   - Check Python/pip/PyPi metadata and scripts, e.g. ``setup.py``
   - Double check that all examples/tutorials/etc are covered by CI

Test the RC
~~~~~~~~~~~

4. Collect artifact from the above GA run.
   In case you want to manually want to trigger ``ciwheel.yml`` GA, overwrite the ``ciwheel`` branch with the commit of your choosing and force push to Github.
5. ``twine upload -r testpypi dist/*``
6. Ask users to test the above, e.g.:

.. code-block:: bash

   python -m venv env && source env/bin/activate
   pip install numpy
   pip install -i https://test.pypi.org/simple/ arbor==0.6-rc
   python -c ’import arbor; print(arbor.__config__)’

Release
-------

0. Make sure ``ciwheel.yml`` passes tests, produced working wheels, and nobody reported problems testing the RC.
   Make sure ``VERSION`` does not end with ``-rc`` or ``-dev``
1. Tag and release: https://github.com/arbor-sim/arbor/releases

   -  on cmdline: git tag -a TAGNAME
   -  git push origin TAGNAME
   -  Go to `GH tags`_ and click “…” and “Create release”
   -  Go through merged PRs to come up with a changelog

2. Create tarball with
   ``scripts/create_tarball ~/loc/of/arbor tagname outputfile``

   -  eg ``scripts/create_tarball /full/path/to/arbor v0.5.1 ~/arbor-v0.5.1-full.tar.gz``

3. [`AUTOMATED`_] push to git@gitlab.ebrains.eu:arbor-sim/arbor.git
4. Download output of wheel action and extract (verify the wheels and
   source targz is in /dist)
5. Verify wheel

   -  create venv: python -m venv env && source env/bin/activate
   -  pip install arbor-0.5.1-cp39-cp39-manylinux2014_x86_64.whl
   -  python -c ’import arbor; print(arbor.__config__)’

6. Upload to pypi

   -  twine upload -r arborpypi dist\*

7. Verify

   -  create venv: python -m venv env && source env/bin/activate
   -  pip install arbor==0.5.1 –verbose
   -  python -c ’import arbor; print(arbor.__config__)’

Post release
------------

1. Update spack package

   -  first, update ``spack/package.py``. The checksum of the targz is the sha256sum.
   -  Then, use the file to `make PR here <https://github.com/spack/spack/blob/develop/var/spack/repos/builtin/packages/>`_

2. In the same PR with the update to `spack/package.py`, might as well bump `VERSION` file.
3. Announce on our website
4. Add release for citation on Zenodo, add new ID to docs
5. Add tagged version of docs on ReadTheDocs (should happen automatically)
6. HBP internal admin

  - [Plus](https://plus.humanbrainproject.eu/components/2691/)
  - [TC Wiki](https://wiki.ebrains.eu/bin/view/Collabs/technical-coordination/EBRAINS%20components/Arbor/)
  - [KG](https://kg.ebrains.eu/search/instances/Software/80d205a9-ffb9-4afe-90b8-2f12819950ec) - [Update howto](https://github.com/bweyers/HBPVisCatalogue/wiki/How-to-start-software-meta-data-curation%3F#update-curated-software).
    - Supported file formats (ie [ContentTypes](https://humanbrainproject.github.io/openMINDS/v3/core/v4/data/contentType.html)), [details](https://github.com/HumanBrainProject/openMINDS_core/tree/v3/instances/data/contentTypes)
  - Send an update to the folk in charge of HBP Twitter if we want to shout about it
7. FZJ admin

  - https://juser.fz-juelich.de/submit

.. _GH tags: https://github.com/arbor-sim/arbor/tags
.. _AUTOMATED: https://github.com/arbor-sim/arbor/blob/master/.github/workflows/ebrains.yml 
