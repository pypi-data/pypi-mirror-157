.. _{{ fullname }}:

.. raw:: html

    <br><br><br><br>

{{ fullname }}
{{ underline }}

.. raw:: html

    <br><br>

.. automodule:: {{ fullname }}
    :members:

    {% block exceptions %}
    {% if exceptions %}
    .. rubric:: exceptions

    .. autosummary::
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block classes %}
    {% if classes %}
    .. rubric:: classes

    .. autosummary:: 
    {% for item in classes %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    {% block functions %}
    {% if functions %}
    .. rubric:: functions

    .. autosummary::
    {% for item in functions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}

    .. raw:: html

        <br><br>
