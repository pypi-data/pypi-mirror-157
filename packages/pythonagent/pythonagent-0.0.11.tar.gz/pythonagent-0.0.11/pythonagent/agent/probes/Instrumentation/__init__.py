from ..base import ExitCallInterceptor
from pythonagent.agent.probes.Instrumentation.parser import create_method_array
# from pythonagent.agent.probes.havoc.havoc_manager import NDNetHavocMonitor
from pythonagent.utils import get_current_timestamp_in_ms

import os
import configparser
import time
import logging

logger = logging.getLogger('pythonagent.agent')

#configParser = configparser.RawConfigParser()
path = os.environ.get('ND_HOME')
path = path + '/config/ndsettings.conf'
logger.info("path of  NDC config : ", path)
#configParser.read(path)
#path_for_insProfile = configParser.get('PYTHON_AGENT', 'path_profile')
myvars = {}

with open(path) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        myvars[name.strip()] = var
try:
    #print("inside try")
    path_for_insProfile = myvars.get('path_profile').strip('\n')
except:
    #print("inside except")
    path_for_insProfile= os.environ.get('ND_HOME') + "/CavAgent/instrumentationprofile.json"
logger.debug('Profiler path at : {}'.format(path_for_insProfile))
#custom_methods_to_instrument = create_method_array('/home/cavisson/shop/my-shop/instrumentationprofile.txt')
custom_methods_to_instrument = create_method_array(path_for_insProfile)
logger.debug("ALL custom modules(Instrument)-> ".format(custom_methods_to_instrument))


class MethodInterceptor(ExitCallInterceptor):

    def _custom_method(self, original_method, *args, **kwargs):

        logger.info("\n\n\n\nInside Custom Method\n\n\n")
        bt = self.bt

        if len(self.cls.__package__) >= 1:
            fqmforentry = str(self.cls.__package__) + "." + str(self.cls.__name__) + "." + str(original_method.__name__)
        else:
            #fqmforentry = "_." + str(self.cls.__name__) + "." + str(original_method.__name__)
            fqmforentry = "." + str(self.cls.__name__) + "." + str(original_method.__name__)

        # print("Inside custom method")

        #before_time = time.time_ns() // 1000000
        before_time=get_current_timestamp_in_ms()

        # print("Before applying method call delay")
        # print("FQM: ", fqmforentry)

        from pythonagent.agent.probes.havoc.havoc_manager import NDNetHavocMonitor, NDHavocException
        havoc_monitor = NDNetHavocMonitor.get_instance()

        # havoc_monitor.apply_method_invocation_failure(fqmforentry)

        method = None
        if bt is not None:
            try:

                method = self.agent.method_entry(bt, fqmforentry)

                response = original_method(*args, **kwargs)

                havoc_monitor.apply_method_call_delay(fqmforentry)

            except Exception as e:
                self.agent.logger.exception('Modulename: MethodInterceptor class inside _custom_method got exception in orginal method')
                raise e  # Added by Samanvay on 06/04/2022 while debugging outbound havoc failure main -> http_callout -> request.get

            finally:

                #after_time = time.time_ns() // 1000000
                after_time = get_current_timestamp_in_ms()
                duration = after_time - before_time
                logger.info("Duration Calculated: {}".format(duration))

                try:
                    havoc_monitor.apply_method_invocation_failure(fqmforentry)
                except Exception as e:
                    if isinstance(e, NDHavocException):
                        logger.error("Havoc Exception {}".format(e))
                        status = 503
                        self.agent.method_exit(bt, fqmforentry, status, duration)
                        self.agent.set_current_status_code(503)
                        raise e
                    else:
                        logger.error("Non-Havoc Exception {}".format(e))

                status = 0  # Needed for callouts only
                if self.agent.cav_env == "AWS_LAMBDA":
                    self.agent.method_exit(bt, fqmforentry, status, duration)
                if self.agent.cav_env == "NATIVE":
                    self.agent.method_exit(bt, fqmforentry)

                if method is not None:
                    if self.agent.cav_env == "AWS_LAMBDA":
                        self.agent.method_exit(bt, fqmforentry, status, duration)
                    if self.agent.cav_env == "NATIVE":
                        self.agent.method_exit(bt, fqmforentry)
        else:
            # self.agent.logger.info("did not find BT in ModuleInterceptor._custom_method")
            self.agent.logger.exception('Modulename: MethodInterceptor class inside _custom_method,,did not find BT in ModuleInterceptor._custom_method')
            response = original_method(*args, **kwargs)
        return response 


def intercept_instrumented_method(agent, mod):
    logger.info("\n\n\n")
    logger.info("intercept instrumented method")
    logger.info("\n\n\n")

    for item in custom_methods_to_instrument:
        check = item.split(".")
        if len(check) == 2:
            try:
                MethodInterceptor(agent, mod).attach(check[1], patched_method_name='_custom_method')
            except:
                agent.logger.exception("Modulename: MethodInterceptor class inside intercept_instrumented_method,Instrumentation.__init__: class {} not present in module".format(check[1]))

                continue    
        if len(check) == 3:
            try:
                MethodInterceptor(agent, getattr(mod, check[1])).attach(check[2],patched_method_name='_custom_method')
            except:
                agent.logger.exception("Modulename: MethodInterceptor class inside intercept_instrumented_method, Instrumentation.__init__: method /class: {}.{} not present in module".format(check[1], check[2]))
                continue

