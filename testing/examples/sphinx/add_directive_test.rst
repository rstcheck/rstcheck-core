====
Test
====

.. req:: test add directives
    :id: REQ_cVcB6E4I
    :name: test req
    description
    - list item 1
          - list item 2
    - list item 3

    .. req:: A custom requirement with picture
      :author: daniel
      :id: EX_REQ_4
      :tags: example
      :status: open
      :layout: example
      :style yellow, blue_border

    This example uses the value from **author** to reference an image.
        See :ref:`layouts_styles` for the complete explanation.

    .. req:: A requirement with a permalink
      :id: EX_REQ_5
      :tags: example
      :status: open
      :layout: permalink_example

.. code:: python
    print(

.. spec:: Nested Spec Need
   :id: JINJAID125
   :status: open
   :tags: user;login
   :links: JINJAID126
   :jinja_content: true

   Nested need with ``:jinja_content:`` option set to ``true``.
   This requirement has tags: **{{ tags | join(', ') }}**.

   It links to:
   {% for link in links %%%}
      - {{ link }}
   {% endfor %}
