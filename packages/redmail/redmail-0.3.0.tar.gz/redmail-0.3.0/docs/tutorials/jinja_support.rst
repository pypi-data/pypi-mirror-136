
.. _jinja-support:

Jinja Support
=============

Red Mail uses Jinja for templating the HTML and text 
bodies. This enables a lot of features out-of-the box.
See `Jinja documentation <https://jinja.palletsprojects.com/>`_ 
for more details of the templating.

Parametrizing Emails
--------------------

You can also parametrize an email using Jinja 
parameters:

.. code-block:: python

    email.send(
        subject='email subject',
        receivers=['first.last@example.com'],
        html="""
            <h1>Hi {{ client }},</h1>
            <p>we are opening the source of {{ project_name }}.</p>
            <p>Kind regards
            <br>{{ company }}</p>
        """,
        text="""
            Hi {{ client }},
            we are opening the source of {{ project_name }}.

            Kind regards,
            {{ company }}
        """,
        body_params={
            'client': 'Customer LTD', 
            'project_name': 'Red Mail', 
            'company': 'Company LTD',
        }
    )

Both text and HTML body support Jinja parametrization. 

Default Parameters
^^^^^^^^^^^^^^^^^^

There are also some parameters passed automatically for convenience.
You can always override these if you wish. Here is a quick example of
some of them:

.. code-block:: python

    email.send(
        subject='email subject',
        receivers=['first.last@example.com'],
        html="""
            <h1>Hi,</h1>
            <p>nice to meet you</p>
            <p>Kind regards
            <br>{{ sender.full_name }}</p>
        """,
    )

Here is a list of default parameters:

================ ==================================== =========================================================
Parameter Name   Type                                 Description
================ ==================================== =========================================================
sender           :class:`redmail.models.EmailAddress` Format class of the email sender
error            :class:`redmail.models.Error`        Format class of the current exception (if any)
node             str                                  Computer’s network name (if can be determined)
user             str                                  Name of the current user logged on the computer
now              datetime.datetime                    Current date and time
================ ==================================== =========================================================


Including Loops and Control Flow
--------------------------------

As the bodies use Jinja in the background, you can use various additional features such 
as if statements, for loops, macros etc. Here is a quick illustration:

.. code-block:: python

    email.send(
        subject='email subject',
        receivers=['first.last@example.com'],
        html="""
            <h1>Hi!</h1>
            <p>
                Soon you will meet my team. 
                Here is a quick introduction:
            </p>
            <ul>
                {% for colleague in colleagues.items() %}
                    <li>{{ colleague }}: {{ description }}</li>
                {% endfor %}
            </ul>
            {% if confidential %}
                <p>
                    This message is confidential. 
                </p>
            {% endif %}

            <p>Kind regards
            <br>{{ sender.full_name }}</p>
        """,
        body_params={
            'colleagues': {'Jack': 'Developer', 'John': 'CEO'},
            'confidential': False
        }
    )

Please see `Jinja documentation <https://jinja.palletsprojects.com/>`_ 
for more.