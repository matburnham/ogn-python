# ogn-python

[![Build Status](https://travis-ci.org/glidernet/ogn-python.svg?branch=master)](https://travis-ci.org/glidernet/ogn-python)
[![Coverage Status](https://img.shields.io/coveralls/glidernet/ogn-python.svg)](https://coveralls.io/r/glidernet/ogn-python)

A database backend for the [Open Glider Network](http://wiki.glidernet.org/).
The ogn-python module saves all received beacons into a database with [SQLAlchemy](http://www.sqlalchemy.org/).
It connects to the OGN aprs servers with [python-ogn-client](https://github.com/glidernet/python-ogn-client).
It requires [PostgreSQL](http://www.postgresql.org/) and [PostGIS](http://www.postgis.net/).

[Examples](https://github.com/glidernet/ogn-python/wiki/Examples)


## Installation and Setup
1. Checkout the repository

   ```
   git clone https://github.com/glidernet/ogn-python.git
   ```

2. Install python requirements

    ```
    pip install -r requirements.txt
    ```
3. Install [PostgreSQL](http://www.postgresql.org/) with [PostGIS](http://www.postgis.net/) Extension.
   Create a database (use "ogn" as default, otherwise you have to modify the configuration, see below)


4. Optional: Install redis for asynchronous tasks (like takeoff/landing-detection)

    ```
    apt-get install redis-server
    ```

5. Create database

    ```
    ./manage.py db.init
    ```

There is also a [Vagrant](https://www.vagrantup.com/) environment for the development of ogn-python.
You can create and start this virtual machine with `vagrant up` and login with `vagrant ssh`.
The code of ogn-python will be available in the shared folder `/vagrant`.

## Usage
### Running the aprs client and task server
To schedule tasks like takeoff/landing-detection (`logbook.compute`),
[Celery](http://www.celeryproject.org/) with [Redis](http://www.redis.io/) is used.
The following scripts run in the foreground and should be deamonized
(eg. use [supervisord](http://supervisord.org/)).

- Start the aprs client

  ```
  ./manage.py gateway.run
  ```

- Start a task server (make sure redis is up and running)

  ```
  celery -A ogn.collect worker -l info
  ```

- Start the task scheduler (make sure a task server is up and running)

  ```
  celery -A ogn.collect beat -l info
  ```


To load a custom configuration, create a file `myconfig.py` (see [config/default.py](config/default.py))
and set the environment variable `OGN_CONFIG_MODULE` accordingly.

```
touch myconfig.py
export OGN_CONFIG_MODULE="myconfig"
./manage.py gateway.run
```

### manage.py - CLI options
```
usage: manage [<namespace>.]<command> [<args>]

positional arguments:
  command     the command to run

optional arguments:
  -h, --help  show this help message and exit

available commands:
  
  [bulkimport]
    convert_logfile        Convert ogn logfiles to csv logfiles (one for aircraft beacons and one for receiver beacons) <arg: path>. Logfile name: blablabla.txt_YYYY-MM-DD.
    create_indices         Create indices for AircraftBeacon.
    drop_indices           Drop indices of AircraftBeacon.
    import_csv_logfile     Import csv logfile <arg: csv logfile>.
  
  [db]
    drop                   Drop all tables.
    import_airports        Import airports from a ".cup" file
    import_ddb             Import registered devices from the DDB.
    import_ddb_file        Import registered devices from a local file.
    init                   Initialize the database.
    upgrade                Upgrade database to the latest version.
  
  [gateway]
    run                    Run the aprs client.
  
  [igcexport]
    write                  Export igc file for <address> at <date>.
  
  [logbook]
    compute_logbook        Compute logbook.
    compute_takeoff_landingCompute takeoffs and landings.
    show                   Show a logbook for <airport_name>.
  
  [stats]
    airports               Compute airport statistics.
    devices                Compute device statistics
    receivers              Compute receiver statistics.
  
  [show.airport]
    list_all               Show a list of all airports.
  
  [show.deviceinfos]
    stats                  Show some stats on registered devices.
  
  [show.devices]
    aircraft_type_stats    Show stats about aircraft types used by devices.
    hardware_stats         Show stats about hardware version used by devices.
    software_stats         Show stats about software version used by devices.
    stealth_stats          Show stats about stealth flag set by devices.
  
  [show.receiver]
    hardware_stats         Show some statistics of receiver hardware.
    list_all               Show a list of all receivers.
    software_stats         Show some statistics of receiver software.
```

Only the command `logbook.compute` requires a running task server (celery) at the moment.


### Available tasks

- `ogn.collect.database.import_ddb` - Import registered devices from the DDB.
- `ogn.collect.database.import_file` - Import registered devices from a local file.
- `ogn.collect.database.update_country_code` - Update country code in receivers table if None.
- `ogn.collect.database.update_devices` - Add/update entries in devices table and update foreign keys in aircraft beacons.
- `ogn.collect.database.update_receivers` - Add/update_receivers entries in receiver table and update receivers foreign keys and distance in aircraft beacons and update foreign keys in receiver beacons.
- `ogn.collect.logbook.update_logbook` - Add/update logbook entries.
- `ogn.collect.logbook.update_max_altitude` - Add max altitudes in logbook when flight is complete (takeoff and landing).
- `ogn.collect.stats.update_device_stats` - Add/update entries in device stats table.
- `ogn.collect.stats.update_receiver_stats` - Add/update entries in receiver stats table.
- `ogn.collect.takeoff_landing.update_takeoff_landing` - Compute takeoffs and landings.

If the task server is up and running, tasks could be started manually.

```
python3
>>>from ogn.collect.database import import_ddb
>>>import_ddb.delay()
```

## License
Licensed under the [AGPLv3](LICENSE).
