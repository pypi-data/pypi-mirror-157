import os
from datetime import datetime, timedelta
from time import sleep

from robot.api.deco import keyword
from robot.utils import is_truthy, timestr_to_secs, secs_to_timestr

from RemoteMonitorLibrary.api import db, services
from RemoteMonitorLibrary.api.tools import GlobalErrors
from RemoteMonitorLibrary.library.listeners import *
from RemoteMonitorLibrary.runner import HostRegistryCache
from RemoteMonitorLibrary.utils import get_error_info
from RemoteMonitorLibrary.utils import logger
from RemoteMonitorLibrary.utils.sql_engine import insert_sql, update_sql, DB_DATETIME_FORMAT


class ConnectionKeywords:
    __doc__ = """=== Connections keywords ===
    `Create host monitor`

    `Close host monitor`

    `Terminate all monitors`

    === PlugIn's keywords ===

    `Start monitor plugin`

    `Stop monitor plugin`

    === Flow control ===

    `Start period`

    `Stop period`

    `Wait`

    `Set mark` - TBD

    === Examples ===

    | ***** Settings ***** 
    | Library           RemoteMonitorLibrary 
    | Library           BuiltIn
    | 
    | Suite Setup    run keyword   Create host monitor  SSH  host=${HOST}  username=${USER}  password=${PASSWORD}  ...
    | ...           AND  Create host monitor  WEB  url=${URL}  user=${USER}  password=${PASSWORD}  ...
    | Suite Teardown    terminate_all_monitors
    |
    | ***** Variables *****
    | ${HOST}           ...
    | ${USER}           ...
    | ${PASSWORD}       ...
    | ${INTERVAL}       1s
    | ${PERSISTENT}     yes
    | ${DURATION}       1h
    |
    | ${URL}            ...
    | ${W_USER}         ...
    | ${W_PASSWORD}     ...
    | ${UUID}           ...
    | ***** Tests *****
    | Test Host monitor
    |   [Tags]  ssh  monitor
    |   Start monitor plugin  aTop  interval=${INTERVAL}  persistent=${PERSISTENT}
    |   Start monitor plugin  Time  command=make -j 40 clean all  interval=0.5s  persistent=${PERSISTENT}
    |   ...                         name=Compilation  start_in_folder=~/bm_noise/linux-5.11.10
    |   sleep  ${DURATION}  make something here
    |   Stop monitor plugin  Time  name=Complilation
    |   [Teardown]  run keywords  generate module statistics  plugin=Time  name=Compilation
    |   ...         AND  generate module statistics  plugin=aTop
    |
    | Test WEB monitor
    |   [Tags]  web  monitor
    |   Start monitor plugin  API  interval=${INTERVAL}  persistent=${PERSISTENT}  protectorUuid=${UUID}  
    |   ...                         protectorStatus=CONNECTED  
    |   
    |   sleep  ${DURATION}  make something here
    |   Stop monitor plugin  Time  name=Complilation
    |   [Teardown]  run keywords  generate module statistics  plugin=Time  name=Compilation
    |   ...         AND  generate module statistics  plugin=aTop
    |
    """

    def __init__(self, rel_location, file_name, **options):

        self._modules = HostRegistryCache()
        self.location, self.file_name, self.cumulative = \
            rel_location, file_name, is_truthy(options.get('cumulative', False))
        self._log_to_db = options.get('log_to_db', False)
        self.ROBOT_LIBRARY_LISTENER = AutoSignPeriodsListener()

        suite_start_kw = self._normalise_auto_mark(options.get('start_suite', None), 'start_period')
        suite_end_kw = self._normalise_auto_mark(options.get('start_suite', None), 'stop_period')
        test_start_kw = self._normalise_auto_mark(options.get('start_test', None), 'start_period')
        test_end_kw = self._normalise_auto_mark(options.get('end_test', None), 'stop_period')

        if suite_start_kw:
            self.register_kw(AllowedHooks.start_suite, suite_start_kw)
        if suite_end_kw:
            self.register_kw(AllowedHooks.end_suite, suite_end_kw)
        if test_start_kw:
            self.register_kw(AllowedHooks.start_test, test_start_kw)
        if test_end_kw:
            self.register_kw(AllowedHooks.end_test, test_end_kw)

    @staticmethod
    def _normalise_auto_mark(custom_kw, default_kw):
        if is_truthy(custom_kw) is True:
            return default_kw
        elif custom_kw is not None:
            return custom_kw
        return None

    def _init(self):
        output_location = BuiltIn().get_variable_value('${OUTPUT_DIR}')
        services.DataHandlerService().init(os.path.join(output_location, self.location), self.file_name,
                                           self.cumulative)

        level = BuiltIn().get_variable_value('${LOG LEVEL}')
        logger.setLevel(level)
        rel_log_file_path = os.path.join(self.location, self.file_name)
        abs_log_file_path = os.path.join(output_location, self.location, self.file_name)

        logger.set_file_handler(abs_log_file_path)
        if is_truthy(self._log_to_db):
            services.TableSchemaService().register_table(db.log())
            logger.addHandler(services.SQLiteHandler())
        services.DataHandlerService().start()
        logger.warn(f'<a href="{rel_log_file_path}">{self.file_name}</a>', html=True)

    def get_keyword_names(self):
        return [
            self.create_host_monitor.__name__,
            self.close_host_monitor.__name__,
            self.terminate_all_monitors.__name__,
            self.start_monitor_plugin.__name__,
            self.stop_monitor_plugin.__name__,
            self.start_period.__name__,
            self.stop_period.__name__,
            self.pause_monitor.__name__,
            self.resume_monitor.__name__,
            self.add_to_plugin.__name__,
            self.remove_from_plugin.__name__,
            self.set_mark.__name__,
            self.wait.__name__,
            self.register_kw.__name__,
            self.unregister_kw.__name__,
            self.get_current_errors.__name__
        ]

    @keyword("Create host monitor")
    def create_host_monitor(self, module_name, alias=None, **module_options):
        """Create basic host connection module used for trace host
        Last created connection handled as 'current'
        In case tracing required for one host only, alias can be ignored

        # Arguments:
        - alias: 'username@host:port' if omitted
        - timeout       : connection & command timeout


        == Supported modules ==
        === SSH ===
        Connection arguments:
            - host: IP address, DNS name,
            - username
            - password
            - port          : 22 if omitted
            - certificate   : key file (.pem) Optional

        === SSH Examples ===
        |  KW                    | Module   |  Arguments             | Comments              |
        |  Create host monitor   | SSH  | host=127.0.0.1  username=any_user  password=any_password  | Default port; No alias |
        |  Create host monitor   | SSH  | host=127.0.0.1  username=any_user  password= any_password  port=2243        | Custom port; No alias |
        |  Create host monitor   | SSH  | host=127.0.0.1  username=any_user  password= any_password  alias=<name>     | Custom port; Alias    |
        |  Create host monitor   | SSH  | host=127.0.0.1  username=any_user  password= any_password  alias=${my_name} | Default port; Alias    |
        |  Create host monitor   | SSH  | host=127.0.0.1  username=any_user  password= any_password  certificate=key_file.pem | Certificate file will be assigned  |

        === WEB Examples ===
        |  KW                    | Module   |  Arguments             | Comments              |
        |  Create host monitor   | WEB  | url=www.d.com  user=any_user  password=any_password  | Default port; No alias |

        === Auto start/stop periods ===
        By default keyword `Start period`, `Stop period` assigned for start/end test accordingly following by test name

        Can be overwritten by key value pairs
        | listener method=keyword name

        Where listener are one of:
        | start_suite
        | end_suite
        | start_test
        | end_test
        """

        assert module_name in services.ModulesRegistryService().keys(), f"Module '{module_name}' not registered"
        module_type = services.ModulesRegistryService().get(module_name)
        if not services.DataHandlerService().is_active:
            self._init()
        try:
            module = module_type(services.PlugInService(), services.DataHandlerService().add_data_unit,
                                 alias=alias, **module_options)
            module.start()
            logger.info(f"Connection {module.alias} ready to be monitored")
            _alias = self._modules.register(module, module.alias)
            self._start_period(alias=module.alias)
        except Exception as e:
            BuiltIn().fatal_error(f"Cannot start module '{module_name}; Reason: {e}")
        else:
            return module.alias

    @keyword("Close host monitor")
    def close_host_monitor(self, alias=None):
        """
        Stop all plugins_modules related to host by its alias

        Arguments:
        - alias: 'Current' used if omitted
        """
        self._stop_period(alias)
        self._modules.stop_current()

    @keyword("Terminate all monitors")
    def terminate_all_monitors(self):
        """
        Terminate all active hosts & running plugins_modules
        """
        for module in self._modules:
            self._stop_period(module.alias)
        self._modules.close_all()
        services.DataHandlerService().stop()

    @keyword("Start monitor plugin")
    def start_monitor_plugin(self, plugin_name, *args, alias=None, **options):
        """
        Start plugin by its name on host queried by options keys

        Arguments:
        - plugin_names: name must be one for following in loaded table, column 'Class'
        - alias: host monitor alias (Default: Current if omitted)
        - options: interval=... , persistent=yes/no,

        extra parameters relevant for particular plugin can be found in `BuiltIn plugins_modules` section

        """
        try:
            monitor: services.RegistryModule = self._modules.get_connection(alias)
            monitor.plugin_start(plugin_name, *args, **options)
        except Exception as e:
            f, li = get_error_info()
            raise BuiltIn().fatal_error(f"{e}; File: {f}:{li}")
        else:
            logger.info(f"PlugIn '{monitor}' created")

    @keyword("Stop monitor plugin")
    def stop_monitor_plugin(self, plugin_name, alias=None, **options):
        monitor = self._modules.get_connection(alias)
        monitor.plugin_terminate(plugin_name, **options)
        logger.info(f"PlugIn '{plugin_name}' stopped on {monitor.alias}", also_console=True)

    @keyword("Pause monitor")
    def pause_monitor(self, reason, alias=None):
        """
        Pause monitor's plugins_modules (Actual for host reboot or network restart tests)

        Arguments:
        - reason: Pause reason text
        - alias: Desired monitor alias (Default: current)
        """
        monitor = self._modules.get_connection(alias)
        monitor.pause_plugins()
        self._start_period(reason, alias)

    @keyword("Resume monitor")
    def resume_monitor(self, reason, alias=None):
        """
        Resume previously paused monitor (Actual for host reboot or network restart tests)

        Arguments:
        - reason: Pause reason text
        - alias: Desired monitor alias (Default: current)
        """
        monitor: services.RegistryModule = self._modules.get_connection(alias)
        monitor.resume_plugins()
        self._stop_period(reason, alias)

    @keyword("Add to Plugin")
    def add_to_plugin(self, plugin_name, *args, **kwargs):
        """
        Add to Plugin - allow runtime modify (adding) plugin configuration

        Particular PlugIn's options see in `BuiltIn plugins_modules`

        Arguments:
        - plugin_name:
        - alias:
        - args: Plugin related unnamed arguments
        - kwargs: Plugin related named arguments
        """
        alias = kwargs.pop('alias', None)
        monitor: services.RegistryModule = self._modules.get_connection(alias)
        plugins = monitor.get_plugin(plugin_name)
        assert len(plugins) > 0, f"Plugin '{plugin_name}{f' ({alias})' if alias else ''}' not started"
        for plugin in plugins:
            plugin.upgrade_plugin(*args, **kwargs)

    @keyword("Remove from Plugin")
    def remove_from_plugin(self, plugin_name, *args, **kwargs):
        """
        Remove from Plugin - allow runtime modify (reducing) plugin configuration

        Particular PlugIn's options see in `BuiltIn plugins_modules`

         Arguments:
        - plugin_name:
        - alias:
        - args: Plugin related unnamed arguments
        - kwargs: Plugin related named arguments
        """
        alias = kwargs.pop('alias', None)
        monitor: services.RegistryModule = self._modules.get_connection(alias)
        plugins = monitor.get_plugin(plugin_name)
        assert len(plugins) > 0, f"Plugin '{plugin_name}{f' ({alias})' if alias else ''}' not started"
        for plugin in plugins:
            plugin.downgrade_plugin(*args, **kwargs)

    @keyword("Start period")
    def start_period(self, period_name=None, alias=None):
        """
        Start period keyword

        Arguments:
        - period_name: Name of period to be started
        - alias: Connection alias
        """
        self._start_period(period_name, alias)

    def _start_period(self, period_name=None, alias=None):
        module: services.RegistryModule = self._modules.get_connection(alias)
        table = services.TableSchemaService().tables.Points
        services.DataHandlerService().execute(insert_sql(table.name, table.columns),
                                              module.host_id, period_name or module.alias,
                                              datetime.now().strftime(DB_DATETIME_FORMAT),
                                              None)

    @keyword("Stop period")
    def stop_period(self, period_name=None, alias=None):
        """
        Stop period keyword

        Arguments:
        - period_name: Name of period to be stopped
        - alias: Connection alias
        """
        self._stop_period(period_name, alias)

    def _stop_period(self, period_name=None, alias=None):
        module: services.RegistryModule = self._modules.get_connection(alias)
        table = services.TableSchemaService().tables.Points
        point_name = rf"{period_name or module.alias}"
        services.DataHandlerService().execute(update_sql(table.name, 'End',
                                                         HOST_REF=module.host_id, PointName=point_name),
                                              datetime.now().strftime(DB_DATETIME_FORMAT))

    @keyword("Wait")
    def wait(self, timeout, reason=None, reminder='1h'):
        """
        Wait are native replacement for keyword 'sleep' from BuiltIn library
        Difference: wait exit in case Any global errors occurred within active Plugins

        Arguments:
        - timeout:  String in robot format (20, 1s, 1h, etc.)
        - reason:   Any string to indicate exit if no errors occurred
        - reminder: Log out remain time each <remind> period
        """
        timeout_sec = timestr_to_secs(timeout)
        end_time = datetime.now() + timedelta(seconds=timeout_sec)
        next_reminder_time = datetime.now() + timedelta(seconds=timestr_to_secs(reminder))
        BuiltIn().log(f"Waiting {timeout} ({timeout_sec}sec.) till {end_time.strftime('%F %H:%H:%S')}", console=True)
        while datetime.now() <= end_time:
            if len(GlobalErrors()) > 0:
                BuiltIn().fail("Global error occurred: {}".format('\n\t'.join([f"{e}" for e in GlobalErrors()])))
            elif datetime.now() >= next_reminder_time:
                BuiltIn().log(f"Remain {secs_to_timestr((end_time - datetime.now()).total_seconds(), compact=True)}",
                              console=True)
                next_reminder_time = datetime.now() + timedelta(seconds=timestr_to_secs(reminder))
            sleep(1)
        if reason:
            BuiltIn().log(reason)

    @keyword("Set mark")
    def set_mark(self, mark_name, alias=None):
        module: services.RegistryModule = self._modules.get_connection(alias)
        table = services.TableSchemaService().tables.Points
        services.DataHandlerService().execute(update_sql(table.name, 'Mark',
                                                         HOST_REF=module.host_id, PointName=mark_name),
                                              datetime.now().strftime(DB_DATETIME_FORMAT))

    @keyword("Get Current RML Errors")
    def get_current_errors(self):
        return GlobalErrors()

    @keyword("Register KW")
    def register_kw(self, hook: AllowedHooks, kw_name, *args, **kwargs):
        """
        Register keyword to listener

        Arguments:
        - hook: one of start_suite, end_suite, start_test, end_test
        - kw_name: Keyword name
        - args: unnamed arguments
        - kwargs: named arguments
        """
        self.ROBOT_LIBRARY_LISTENER.register(hook, kw_name, list(args) + [f"{k}={v}" for k, v in kwargs.items()])

    @keyword("Unregister kw")
    def unregister_kw(self, hook: AllowedHooks, kw_name):
        """
        Unregister keyword from listener
        - hook: one of start_suite, end_suite, start_test, end_test
        - kw_name: Keyword name
        """
        self.ROBOT_LIBRARY_LISTENER.unregister(hook, kw_name)
