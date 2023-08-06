Dataset loader for specific data
=================================

Project description:
~~~~~~~~~~~~~~~~~~~~

This project contains a loader of a special data set, as well as a connection to the database using pymssql.

Prepare for project
~~~~~~~~~~~~~~~~~~~
First you need to create a settings.json in which the fields are specified: ::

  "prefix_login" - If you need a prefix for login (if not required, add a field and pass an empty string),
  "url" - Url for connection by token,
  "cert_vault_tls" - The path to the security certificate,
  "cert_vault_key" - The path to the security key,
  "cert_vault_verify" - The path to the security verify

Get start:
~~~~~~~~~~~~~~~~~~~~
First you need to import the package: ::

    import pack_dataset

Now create an instance of the connection class: ::

    datasets_loader = pack_dataset.create_connect()

And the data for connecting to the database is contained in the permanent environment, then they are automatically initialized. Connection to databases is carried out in 2 ways. The first is the connection via login and password: ::

    datasets_loader.connect_to_db_with_login(login, password)

Or through a special token using the **hvac** library: ::

    datasets_loader.connect_to_db_with_token(vault_token, vault_secret_engine, vault_path)

Now you just want to get a data set indicating how many rows you need to get (don't specify lines if you want to unload everything): ::
    
    dataset = datasets_loader.get_data_weather(row=15)

Manual connection to the database:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If, when creating a class, a message is displayed stating that it was not possible to get connection data to the database, you must specify them manually: ::

    datasets_loader.connect_data['server'] = server:port
    datasets_loader.connect_data['database'] = database_name
    datasets_loader.connect_data['schema'] = schema_name
    datasets_loader.connect_data['table'] = table_name

Next, you can connecting to the database (in any convenient way) and get a dataset: ::

    datasets_loader.connect_to_db_with_login(login, password)
    dataset = datasets_loader.get_data_weather(row=15)

