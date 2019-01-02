Built-in Rules
==============

Squabble ships with several rules that are focused mostly on
preventing unsafe schema migrations. To enable these rules,
reference them in your ``.squabblerc`` configuration file.

For example: ::

  {
    "rules": {
      "AddColumnDisallowConstraints": {
        "disallowed": ["DEFAULT"]
      },
      "RequirePrimaryKey": {}
    }
  }

.. contents:: Available Rules
   :local:

AddColumnDisallowConstraints
----------------------------
.. autoclass:: squabble.rules.add_column_disallow_constraints.AddColumnDisallowConstraints
   :members:
   :show-inheritance:
   :exclude-members: enable

DisallowChangeColumnType
------------------------
.. autoclass:: squabble.rules.disallow_change_column_type.DisallowChangeColumnType
   :members:
   :show-inheritance:
   :exclude-members: enable

DisallowRenameEnumValue
-----------------------
.. autoclass:: squabble.rules.disallow_rename_enum_value.DisallowRenameEnumValue
   :members:
   :show-inheritance:
   :exclude-members: enable

RequireColumns
--------------
.. autoclass:: squabble.rules.require_columns.RequireColumns
   :members:
   :show-inheritance:
   :exclude-members: enable

RequireConcurrentIndex
----------------------
.. autoclass:: squabble.rules.require_concurrent_index.RequireConcurrentIndex
   :members:
   :show-inheritance:
   :exclude-members: enable

RequirePrimaryKey
-----------------
.. autoclass:: squabble.rules.require_primary_key.RequirePrimaryKey
   :members:
   :show-inheritance:
   :exclude-members: enable