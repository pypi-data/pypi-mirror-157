#!/usr/bin/env python

import getpass
import os, sys, logging
import subprocess

import json
import argparse
# Documentation: https://kislyuk.github.io/argcomplete/
import argcomplete
import datetime
import pprint
import yaml

#import eland as ed
#from elasticsearch import Elasticsearch

class CommandException(Exception):
    pass

class Comando:
    def __init__(self, yml='args.yml', elasticsearchlink=None, redis_server=None, redis_port: int = 0, f__version__init__=False, log_level=None, redis_exp_time=300):
        self.user = getpass.getuser()
        self.redis_client = None
        self.f__version__init__ = f__version__init__
        
        '''
        self.es = Elasticsearch(
                [elasticsearchlink],
                timeout=60
                )
        '''
        self.yml = yml
        self.redis_exp_time = redis_exp_time

        # Generates the parser based on yaml files
        self.parser = self.setup_parser_from_yml(self.yml)
        
        argcomplete.autocomplete(self.parser)

        self.arguments_dict = vars(self.parser.parse_args())

        self.logger = None
        # By default, the value for log_level on the command parameters will be "log_level"
        # If "log_level" is not set on the command, then it will use the parameter used in the init function
        self.log_level = log_level
        if "log_level" in self.arguments_dict:
            self.log_level = self.arguments_dict.pop("log_level", None)
        self.setup_logging(self.log_level)
        self.logger.debug(f'log_level: {log_level}\n')

        '''
        self.redis_server = self.arguments_dict.pop("redis_server", None)
        if not self.redis_server:
           self. redis_server = os.getenv("REDIS_SERVER", None)

        self.redis_port = self.arguments_dict.pop("redis_port", None)
        if not self.redis_port:
            try:
                self.redis_port = int(os.getenv("REDIS_PORT", None))
            except Exception:
                pass
        '''


        self.redis_server = redis_server
        if not self.redis_server:
           self. redis_server = os.getenv("REDIS_SERVER", None)

        self.redis_port = redis_port
        if not self.redis_port:
            try:
                self.redis_port = int(os.getenv("REDIS_PORT", None))
            except Exception:
                pass
        

        if self.redis_server:
            self.redis_client = self._get_redis_client(redis_server, redis_port)
        
    def get_arguments_dict(self):
        return self.arguments_dict

    def get_parser(self):
        return self.parser

    def get_logger(self):
        return self.logger

    # implementar ejemplo para reutilizar este codigo para cualquier generacion de comando
    # https://wikimho.com/es/q/codereview/110108
    def load_yml_settings(self, yml, verbose=False):
        '''
        load script's settings (yaml)
        '''
        settings = ''
        with open(yml) as f:
            try:
                settings = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print("Error in configuration file:")
                self.logger.error(str(e))
                sys.exit(1)
            except Exception as e:
                # unexpected exception.
                self.logger.error(str(e), exc_info=e)
                sys.exit(1)
            if verbose:
                print (settings)
        return settings

    def read(self, rel_path: str) -> str:
        here = os.path.abspath(os.path.dirname(__file__))
        # intentionally *not* adding an encoding option to open, See:
        #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
        with open(os.path.join(here, rel_path)) as fp:
            return fp.read()

    def get_version(self, rel_path: str) -> str:
        for line in self.read(rel_path).splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        raise RuntimeError("Unable to find version string.")

    def setup_parser_from_yml(self, yml=None, arguments=None, parser=None, verbose=False):

        if not parser:
            arguments = self.load_yml_settings(yml, verbose=False)
            file_name = os.path.basename(sys.argv[0])
            file_name = file_name.split('.')[0]
            desc = 'setup autocomplete with:\n\
            CSH: eval `register-python-argcomplete --shell tcsh {f}`\n\
            BASH: eval "$(register-python-argcomplete {f})"'.format(f=file_name)
            parser = argparse.ArgumentParser(
                arguments['title'],
                description=desc,
                formatter_class=argparse.RawTextHelpFormatter,
            )

            if self.f__version__init__:
                __version__ = self.get_version("__init__.py")

                parser.add_argument(
                "--version", action="version", version=f"{__version__}"
                )

            #self.set_redis_arguments(parser)

            if verbose: pprint.pprint(arguments)

        for key, val in arguments.items():
            if verbose: print(">>>> {}:{}".format(key,val))
            if key == 'title':
                pass
            else:
                if type(val)!=bool and 'caso' in val:
                    if val['caso']=='arg':
                        try:
                            val.pop('caso')
                            # Details on https://stackoverflow.com/questions/36901/what-does-double-star-asterisk-and-star-asterisk-do-for-parameters
                            parser.add_argument( *key.split(','),**val )
                        except CommandException as e:
                            self.logger.error(str(e))
                            sys.exit(1)
                        except BrokenPipeError:
                            pass  # Ignore. Something like head is truncating output.
                        except KeyboardInterrupt:
                            sys.exit(1)
                        except Exception as e:
                            # unexpected exception.
                            self.logger.error(str(e), exc_info=e)
                            sys.exit(1)
                    elif val['caso']=='parser':
                        action_subparsers = parser.add_subparsers(dest=val['dest'])
                        action_subparsers.required = val['required']
                        subparser = action_subparsers.add_parser(
                            key, help=val['help'], description=val['description']
                        )
                        if 'caso' in val:
                            self.setup_parser_from_yml(arguments=val, parser=subparser, verbose=False)
                        else:
                            pass
                    else:
                        message = "Error: The parameter 'caso' is wrong!"
                        print(message)
                        self.logger.error(message)
                        exit(1)
                else:
                    pass
        return parser
    '''
    def load_csv(self, csv_file):
        df = ed.csv_to_eland(csv_file,
                es_client=self.es,
                es_dest_index='<index-name>',
                es_if_exists='replace',
                es_dropna=True,
                es_refresh=True,
                # compression='gzip',
                index_col=0)

    def get_info(self):
        df = self.ed.DataFrame(
        es_client=self.es,
        es_index_pattern="<index-name>"
        )
        print(df.head())
        print(df.info())
        print(df.describe())
        print(df.dtypes)
    '''
    
    def set_redis_arguments(self, parser):
        redis_group_parser = parser.add_argument_group(
            "redis", "Redis Server for caching sg* commands"
        )
        redis_group_parser.add_argument(
            "--redis-server",
            dest="redis_server",
            help="Redis Server. Also via env MGRID_REDIS_SERVER=x",
            default=None,
            required=False,
        )
        redis_group_parser.add_argument(
            "--redis-port",
            dest="redis_port",
            help="Redis Port. Also via env MGRID_REDIS_PORT=x",
            default=None,
            required=False,
        )

    def _get_redis_client(self, host, port):
        r = None
        try:
            import redis
            self.logger.debug(f"Redis {host}:{port}")
            r = redis.Redis(host=host, port=port)
            r.ping()
        except ModuleNotFoundError:
            self.logger.debug("Redis module not found. (pip install redis)")
            r = None
        except Exception as e:
            self.logger.warning(f"Redis: {e}")
            r = None
        return r
    
    def runCMD(self, command, stdin_str=None, ignore_return_code=False): 
        stdin_param = None 
        if stdin_str: 
            stdin_param = subprocess.PIPE 
        process = subprocess.Popen( 
            command, 
            shell=True, 
            stdin=stdin_param, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
        ) 
        output, error = process.communicate(stdin_str) 
        self.logger.debug(f"Command: {command} | Exit status: {process.returncode}") 
        # if process.returncode > 0: 
        #     print("stdout: " + output) 
        #     print("stderr: " + error) 
        if not ignore_return_code and process.returncode > 0: 
            raise Exception( 
                f"ERROR '{command}' (exit code {process.returncode}): {error}" 
            ) 
        else: 
            return output[:-1] #.decode('utf-8')

    def runCMD_cached(self, command, stdin_str=None, ignore_return_code=False, show_exp_redis=False, redis_exp_time=None):

        if self.redis_client:
            out = self.redis_client.get(f"cmd:{command}")
            stored_timestamp = self.redis_client.get(f"timestamp:{command}")
            if stored_timestamp is not None and show_exp_redis:
                a = int(datetime.datetime.now().timestamp())
                b = float(stored_timestamp)
                delta_seconds = a - b
                print(f'(redis cached data) This value was stored {delta_seconds} seconds ago. Default expiration time: {self.redis_exp_time}')
            if out is not None:
                self.logger.debug(f"(Cached) Command: {command}")
                return out
            else:
                self.logger.debug(f"(Not Cached) Command: {command}")
        else:
            self.logger.debug(f"redis_client not configured: {self.redis_client}")

        out = self.runCMD(
            command, stdin_str=stdin_str, ignore_return_code=ignore_return_code
        )
        if self.redis_client:
            if redis_exp_time is None:
                redis_exp_time = self.redis_exp_time
            self.redis_client.set(f"cmd:{command}", out, ex=redis_exp_time)
            self.redis_client.set(f"timestamp:{command}", str(datetime.datetime.now().timestamp()), ex=self.redis_exp_time)
        return out

    def setup_logging(self, log_level):
        """print logging into stderr"""

        # do not show stack traces on console
        short_formatter = logging.Formatter(
            "%(asctime)s;%(levelname)s;%(message)s", "%Y/%m/%d %H:%M:%S"
        )

        self.logger = logging.getLogger("pycomando")

        logging_level = logging.ERROR
        if log_level:
            if log_level == "debug":
                logging_level = logging.DEBUG
            elif log_level == "info":
                logging_level = logging.INFO
            elif log_level == "warning":
                logging_level = logging.WARNING
        else:
            env_debug_level = os.getenv("DEBUG_LEVEL", "INFO")
            if env_debug_level == "DEBUG":
                logging_level = logging.DEBUG
            elif env_debug_level == "INFO":
                logging_level = logging.INFO
            elif env_debug_level == "WARNING":
                logging_level = logging.WARNING

        self.logger.setLevel(logging_level)
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(short_formatter)
        # console_handler.setLevel(debug_level) # lower level than root logger set
        self.logger.addHandler(console_handler)

    def json_serial(self, obj):
        """
        JSON serializer for objects not serializable by default json code
        :param obj:
        :return:
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        raise TypeError("Type %s not serializable" % type(obj))

    def print_csv_list_of_dict(self, rows, keys, fd=None):
        """print a lsit of dicts in csv"""
        if len(rows) == 0:
            return
        if not fd:
            fd = sys.stdout
        import csv

        w = csv.DictWriter(fd, keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


    def dict_to_table(self, data):
        """Transform a dict for AsciiTable"""
        t = [["Key", "Value"]]
        for key, value in data.items():
            t.append([key, value])
        return t


    def list_of_dict_to_table(self, data, fields=[]):
        """Transform list of objects into rows for AsciiTable"""
        if not fields and len(data) > 0:
            fields = data[0].keys()
        t = []
        for d in data:
            if not t:
                t.append(fields)
            row = []
            for f in fields:
                if f in d:
                    row.append(d[f])
            t.append(row)
        return t


    def output_list_of_dict(self, data, fmt, fields=[], fd=None):
        """print a lsit of dicts"""
        if not fd:
            fd = sys.stdout

        if fmt == "json":
            import json

            fd.write(json.dumps(data, default=json_serial, indent=4))
        elif fmt == "txt":
            from tabulate import tabulate

            # tablefmt="orgtbl" tablefmt="psql" tablefmt="fancy_grid"
            # https://pypi.org/project/tabulate/
            if data:
                fd.write(
                    tabulate(
                        self.list_of_dict_to_table(data, fields),
                        headers="firstrow",
                        tablefmt="psql",
                        numalign="right",
                    )
                )
                fd.write("\n")
        elif fmt in ["html", "jira", "youtrack"]:
            from tabulate import tabulate

            if data:
                fd.write(
                    tabulate(
                        self.list_of_dict_to_table(data, fields),
                        headers="firstrow",
                        tablefmt=fmt,
                        numalign="right",
                    )
                )
                fd.write("\n")
        elif fmt == "csv":
            if len(data) == 0:
                return
            if not fields:
                fields = data[0].keys()
            self.print_csv_list_of_dict(data, fields, fd)
        elif fmt == "string":
            if fields:
                for row in data:
                    row_to_print = []
                    for f in fields:
                        if f in row.keys():
                            row_to_print.append(row[f])
                    fd.write("\t".join([str(x) for x in row_to_print]))
                    fd.write("\n")
            else:
                for row in data:
                    fd.write("\t".join([str(x) for x in row.values()]))
                    fd.write("\n")    

def main():
    comando = Comando(yml='args_pycomando.yml')
    arguments_dict = comando.get_arguments_dict()
    logger = comando.get_logger()
    do = arguments_dict.pop("subcommand")
    
    if do == 'subcomando':
        #pprint.pprint(arguments_dict)
        #logging.debug(f'It Runs {comando} with **arguments_dict: {arguments_dict}\n')
        logger.debug(f'Run {comando} with **arguments_dict: {arguments_dict}\n')
        print('Comando ejecutado exitosamente, se detecto el subcomando:')
        
    sys.exit(0)
 
if __name__ == "__main__":
    main()